import asyncio
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

from telethon import TelegramClient, types

from fast_api.app_dialogs_common.helper_dialogs_common import (
    _get_peer_storage_type,
    serialize_dialog_item,
)
from fast_api.app_telegram_folders_common.helper_telegram_folders_common import (
    _input_peer_identity,
)

DIALOGS_SNAPSHOT_TTL_SECONDS = 60.0
DIALOGS_SNAPSHOT_MAX_ENTRIES = 64

_dialogs_snapshot_cache = {}
_dialogs_snapshot_locks = {}
_dialogs_snapshot_warm_tasks = {}


def _entity_identity(entity_obj) -> Tuple[str, int]:
    return _get_peer_storage_type(entity_obj), int(entity_obj.id)


def _snapshot_key(client: TelegramClient, config_name: str) -> Tuple[str, int]:
    return config_name, id(client)


def _valid_snapshot(snapshot, now_monotonic: float) -> bool:
    return bool(snapshot and (
        now_monotonic - snapshot["created_monotonic"] <=
        DIALOGS_SNAPSHOT_TTL_SECONDS))


def _trim_snapshot_cache() -> None:
    while len(_dialogs_snapshot_cache) > DIALOGS_SNAPSHOT_MAX_ENTRIES:
        oldest_key = min(
            _dialogs_snapshot_cache,
            key=lambda key: _dialogs_snapshot_cache[key]["created_monotonic"])
        _dialogs_snapshot_cache.pop(oldest_key, None)
        _dialogs_snapshot_locks.pop(oldest_key, None)


def clear_dialogs_snapshot_cache(config_name: str = None) -> None:
    keys_to_remove = [
        key for key in _dialogs_snapshot_cache
        if config_name is None or key[0] == config_name]
    for cache_key in keys_to_remove:
        _dialogs_snapshot_cache.pop(cache_key, None)
        _dialogs_snapshot_locks.pop(cache_key, None)


async def _filter_peer_identity(client: TelegramClient,
                                input_peer) -> Tuple[str, int]:
    if isinstance(input_peer, types.InputPeerSelf):
        return _entity_identity(await client.get_me())
    return _input_peer_identity(input_peer)


async def _filter_peer_keys(client: TelegramClient,
                            input_peers: List[object]) -> List[Tuple[str, int]]:
    return [await _filter_peer_identity(client, peer) for peer in input_peers]


def _dialog_is_muted(dialog_obj) -> bool:
    notify_settings = getattr(getattr(dialog_obj, "dialog", None),
                              "notify_settings", None)
    mute_until = getattr(notify_settings, "mute_until", None)
    if isinstance(mute_until, datetime):
        compare_to = datetime.now(tz=mute_until.tzinfo or timezone.utc)
        return mute_until > compare_to
    if isinstance(mute_until, (int, float)):
        return mute_until > datetime.now(tz=timezone.utc).timestamp()
    return bool(mute_until)


def _dialog_is_unread(dialog_obj) -> bool:
    unread_count = getattr(dialog_obj, "unread_count", 0) or 0
    unread_mark = bool(getattr(getattr(dialog_obj, "dialog", None),
                               "unread_mark", False))
    return bool(unread_count or unread_mark)


def _dialog_dynamic_category(dialog_obj, filter_obj) -> Optional[str]:
    entity_obj = dialog_obj.entity
    if isinstance(entity_obj, types.User):
        if getattr(entity_obj, "bot", False):
            return "bots" if getattr(filter_obj, "bots", False) else None
        if getattr(entity_obj, "contact", False):
            return "contacts" if getattr(filter_obj, "contacts", False) else None
        return "non_contacts" if getattr(
            filter_obj, "non_contacts", False) else None
    if isinstance(entity_obj, types.Chat) or getattr(
            entity_obj, "megagroup", False):
        return "groups" if getattr(filter_obj, "groups", False) else None
    if isinstance(entity_obj, types.Channel):
        return "broadcasts" if getattr(
            filter_obj, "broadcasts", False) else None
    return None


def _dynamic_exclusion_reason(dialog_obj, filter_obj) -> Optional[str]:
    if getattr(filter_obj, "exclude_archived", False) and bool(
            getattr(dialog_obj, "archived", False)):
        return "excluded_archived"
    if getattr(filter_obj, "exclude_muted", False) and _dialog_is_muted(
            dialog_obj):
        return "excluded_muted"
    if getattr(filter_obj, "exclude_read", False) and not _dialog_is_unread(
            dialog_obj):
        return "excluded_read"
    return None


def _dialog_sort_timestamp(dialog_obj) -> float:
    date_value = getattr(dialog_obj, "date", None)
    if date_value is None:
        date_value = getattr(getattr(dialog_obj, "message", None), "date", None)
    if not isinstance(date_value, datetime):
        return 0.0
    if date_value.tzinfo is None:
        date_value = date_value.replace(tzinfo=timezone.utc)
    return date_value.timestamp()


async def _scan_all_server_dialogs(client: TelegramClient) -> List[object]:
    dialogs_by_key: Dict[Tuple[str, int], object] = {}
    for peer_folder_id in (0, 1):
        async for dialog_obj in client.iter_dialogs(
                limit=None, folder=peer_folder_id):
            entity_obj = getattr(dialog_obj, "entity", None)
            if entity_obj is None or getattr(entity_obj, "id", None) is None:
                continue
            dialogs_by_key[_entity_identity(entity_obj)] = dialog_obj
    return list(dialogs_by_key.values())


async def get_all_server_dialogs_snapshot(
        client: TelegramClient,
        config_name: str,
) -> Tuple[List[object], Dict[str, object]]:
    cache_key = _snapshot_key(client, config_name)
    now_monotonic = time.monotonic()
    cached_snapshot = _dialogs_snapshot_cache.get(cache_key)
    if _valid_snapshot(cached_snapshot, now_monotonic):
        return list(cached_snapshot["dialogs"]), {
            "snapshot_source": "cache",
            "snapshot_age_ms": round(
                (now_monotonic - cached_snapshot["created_monotonic"]) * 1000,
                3),
            "snapshot_scan_ms": 0.0,
        }

    snapshot_lock = _dialogs_snapshot_locks.setdefault(
        cache_key, asyncio.Lock())
    async with snapshot_lock:
        now_monotonic = time.monotonic()
        cached_snapshot = _dialogs_snapshot_cache.get(cache_key)
        if _valid_snapshot(cached_snapshot, now_monotonic):
            return list(cached_snapshot["dialogs"]), {
                "snapshot_source": "single_flight_cache",
                "snapshot_age_ms": round(
                    (now_monotonic - cached_snapshot["created_monotonic"]) * 1000,
                    3),
                "snapshot_scan_ms": 0.0,
            }

        scan_started = time.monotonic()
        dialogs = await _scan_all_server_dialogs(client)
        scan_finished = time.monotonic()
        _dialogs_snapshot_cache[cache_key] = {
            "created_monotonic": scan_finished,
            "dialogs": list(dialogs),
        }
        _trim_snapshot_cache()
        return dialogs, {
            "snapshot_source": "telegram_refresh",
            "snapshot_age_ms": 0.0,
            "snapshot_scan_ms": round(
                (scan_finished - scan_started) * 1000, 3),
        }


def _consume_warmup_result(cache_key, task) -> None:
    if _dialogs_snapshot_warm_tasks.get(cache_key) is task:
        _dialogs_snapshot_warm_tasks.pop(cache_key, None)
    try:
        task.result()
    except Exception as error:
        print("Telegram dialogs snapshot warm-up failed [WARNING]: %s" % error)


def schedule_dialogs_snapshot_warmup(
        client: TelegramClient,
        config_name: str,
) -> bool:
    cache_key = _snapshot_key(client, config_name)
    now_monotonic = time.monotonic()
    if _valid_snapshot(_dialogs_snapshot_cache.get(cache_key), now_monotonic):
        return False
    current_task = _dialogs_snapshot_warm_tasks.get(cache_key)
    if current_task and not current_task.done():
        return False
    warmup_task = asyncio.create_task(
        get_all_server_dialogs_snapshot(client, config_name))
    _dialogs_snapshot_warm_tasks[cache_key] = warmup_task
    warmup_task.add_done_callback(
        lambda task: _consume_warmup_result(cache_key, task))
    return True


async def get_matching_folder_dialogs(
        client: TelegramClient,
        filter_obj,
        config_name: str,
        dialogs_limit: int,
) -> Tuple[List[Dict[str, object]], int, Dict[str, object]]:
    pinned_keys = await _filter_peer_keys(
        client, list(getattr(filter_obj, "pinned_peers", [])))
    include_keys = set(await _filter_peer_keys(
        client, list(getattr(filter_obj, "include_peers", []))))
    exclude_keys = set(await _filter_peer_keys(
        client, list(getattr(filter_obj, "exclude_peers", []))))
    pinned_key_set = set(pinned_keys)

    snapshot_wait_started = time.monotonic()
    all_dialogs, snapshot_metrics = await get_all_server_dialogs_snapshot(
        client, config_name)
    snapshot_metrics["snapshot_wait_ms"] = round(
        (time.monotonic() - snapshot_wait_started) * 1000, 3)
    filtering_started = time.monotonic()
    included_by_key = {}
    match_reason_by_key = {}
    for dialog_obj in all_dialogs:
        identity = _entity_identity(dialog_obj.entity)
        if identity in exclude_keys:
            continue
        if identity in pinned_key_set:
            included_by_key[identity] = dialog_obj
            match_reason_by_key[identity] = "pinned"
            continue
        if identity in include_keys:
            included_by_key[identity] = dialog_obj
            match_reason_by_key[identity] = "explicitly_included"
            continue

        if isinstance(filter_obj, types.DialogFilterChatlist):
            continue
        category = _dialog_dynamic_category(dialog_obj, filter_obj)
        if not category or _dynamic_exclusion_reason(dialog_obj, filter_obj):
            continue
        included_by_key[identity] = dialog_obj
        match_reason_by_key[identity] = category

    ordered_dialogs = []
    for identity in pinned_keys:
        dialog_obj = included_by_key.pop(identity, None)
        if dialog_obj is not None:
            ordered_dialogs.append(dialog_obj)
    ordered_dialogs.extend(sorted(
        included_by_key.values(),
        key=_dialog_sort_timestamp,
        reverse=True))

    serialized_dialogs = []
    for dialog_obj in ordered_dialogs[:dialogs_limit]:
        identity = _entity_identity(dialog_obj.entity)
        dialog_data = serialize_dialog_item(
            config_name=config_name,
            dialog_obj=dialog_obj)
        dialog_data["is_pinned"] = identity in pinned_key_set
        dialog_data["is_archived"] = bool(getattr(dialog_obj, "archived", False))
        dialog_data["folder_match_reason"] = match_reason_by_key[identity]
        serialized_dialogs.append(dialog_data)
    snapshot_metrics["membership_filter_ms"] = round(
        (time.monotonic() - filtering_started) * 1000, 3)
    return serialized_dialogs, len(all_dialogs), snapshot_metrics
