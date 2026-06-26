from typing import Any, Dict

from telethon import TelegramClient


TARGET_SENDER_FIELDS = (
    "tlt_sender_username",
    "tlt_sender_first_name",
    "tlt_sender_last_name",
    "tlt_sender_phone",
    "tlt_sender_bot",
)


def _has_missing_sender_fields(event_params: Dict[str, Any]) -> bool:
    for cur_key in TARGET_SENDER_FIELDS:
        if event_params.get(cur_key) in (None, ""):
            return True
    return False


def _pick_username(sender_obj: Any) -> str | None:
    username = getattr(sender_obj, "username", None)
    if username:
        return username

    usernames = getattr(sender_obj, "usernames", None) or []
    for cur_username_obj in usernames:
        cur_username = getattr(cur_username_obj, "username", None)
        if cur_username and getattr(cur_username_obj, "active", True):
            return cur_username

    for cur_username_obj in usernames:
        cur_username = getattr(cur_username_obj, "username", None)
        if cur_username:
            return cur_username
    return None


def _build_sender_data(sender_obj: Any) -> Dict[str, Any]:
    if sender_obj is None:
        return {}
    return {
        "tlt_sender_username": _pick_username(sender_obj),
        "tlt_sender_first_name": getattr(sender_obj, "first_name", None),
        "tlt_sender_last_name": getattr(sender_obj, "last_name", None),
        "tlt_sender_phone": getattr(sender_obj, "phone", None),
        "tlt_sender_bot": getattr(sender_obj, "bot", None),
    }


def _merge_missing_fields(
        event_params: Dict[str, Any],
        enriched_data: Dict[str, Any],
        sender_data: Dict[str, Any],
) -> None:
    for cur_key, cur_value in sender_data.items():
        if event_params.get(cur_key) in (None, "") and cur_key not in enriched_data:
            if cur_value not in (None, ""):
                enriched_data[cur_key] = cur_value


def _still_missing_fields(event_params: Dict[str, Any], enriched_data: Dict[str, Any]) -> bool:
    for cur_key in TARGET_SENDER_FIELDS:
        if event_params.get(cur_key) in (None, "") and enriched_data.get(cur_key) in (None, ""):
            return True
    return False


async def enrich_sender_profile_data(
        event: Any,
        telethon_client: TelegramClient | None,
        event_params: Dict[str, Any],
) -> Dict[str, Any]:
    if not event_params or not _has_missing_sender_fields(event_params):
        return {}

    sender_obj = getattr(event, "sender", None)

    get_sender_func = getattr(event, "get_sender", None)
    if callable(get_sender_func):
        try:
            fetched_sender = await get_sender_func()
            if fetched_sender is not None:
                sender_obj = fetched_sender
        except Exception:
            pass

    enriched_data: Dict[str, Any] = {}
    _merge_missing_fields(
        event_params=event_params,
        enriched_data=enriched_data,
        sender_data=_build_sender_data(sender_obj),
    )

    sender_id = (
        event_params.get("tlt_sender_id")
        or getattr(event, "sender_id", None)
        or event_params.get("ev_from_id_user_id")
    )
    if telethon_client and sender_id and _still_missing_fields(event_params, enriched_data):
        try:
            entity_sender_obj = await telethon_client.get_entity(sender_id)
        except Exception:
            entity_sender_obj = None

        _merge_missing_fields(
            event_params=event_params,
            enriched_data=enriched_data,
            sender_data=_build_sender_data(entity_sender_obj),
        )

    return enriched_data
