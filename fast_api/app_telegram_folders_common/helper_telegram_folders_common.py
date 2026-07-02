from datetime import datetime, timezone
from typing import Dict, Iterable, List, Optional, Tuple

from fastapi import HTTPException
from starlette import status
from telethon import TelegramClient, functions, types
from telethon.errors import FloodWaitError, RPCError
from telethon.tl.custom import Dialog

from configs.enums import TELEGRAM_ACCOUNT_TYPE
from fast_api.app_dialogs_common.helper_dialogs_common import (
    _get_peer_storage_type,
    _get_peer_title,
    _get_peer_type,
    get_single_account_client,
    serialize_dialog_item,
)
from fast_api.app_telegram_folders_common.scheme_telegram_folders_common import (
    TGAccountData,
    TGFolderCandidateData,
    TGFolderData,
    TGFolderDefinition,
    TGPeerData,
    TGPeerRef,
    TGPeerResolutionData,
)
from telethon_manager.telethon_clients_manager import TelethonManagerSingleton

ARCHIVE_FOLDER_ID = 1
CUSTOM_FOLDER_ID_MIN = 2
CUSTOM_FOLDER_ID_MAX = 255


async def get_telegram_folder_context(
        web_account_id: str,
        web_account_username: str,
        config_name: str,
) -> Tuple[TelegramClient, object, TGAccountData]:
    telethon_manager = TelethonManagerSingleton()
    client, config = await get_single_account_client(
        telethon_manager=telethon_manager,
        web_account_id=web_account_id,
        web_account_username=web_account_username,
        config_name=config_name)

    config_owner_matches = all((
        config.web_account_id == web_account_id,
        config.web_account_username == web_account_username))
    if not config_owner_matches:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Telegram configuration was not found for web account [ERROR]")

    account_type = getattr(config.account_type, "value", config.account_type)
    if account_type != TELEGRAM_ACCOUNT_TYPE.ACCOUNT.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Telegram folders are available only for user accounts [ERROR]")

    me_obj = await client.get_me()
    bot_token = config.bot_token or ""
    account_data = TGAccountData(
        config_name=config_name,
        telegram_account_id=getattr(me_obj, "id", None),
        username=getattr(me_obj, "username", None),
        first_name_cst=getattr(me_obj, "first_name", None),
        last_name_cst=getattr(me_obj, "last_name", None),
        phone_cst=getattr(me_obj, "phone", None) or config.phone,
        account_type_cst=account_type,
        bot_cst=bot_token[-10:] if bot_token else None)
    return client, config, account_data


def raise_telegram_folders_http_error(error: Exception) -> None:
    if isinstance(error, HTTPException):
        raise error
    if isinstance(error, FloodWaitError):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Telegram flood wait: retry after %s seconds [ERROR]" % (
                error.seconds,))
    if isinstance(error, RPCError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Telegram rejected folder operation: %s [ERROR]" % (
                error.__class__.__name__,))
    raise HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail="Telegram folder operation failed: %s [ERROR]" % (error,))


def _input_peer_identity(input_peer) -> Tuple[str, int]:
    if isinstance(input_peer, (types.InputPeerUser, types.InputPeerUserFromMessage)):
        return "user", input_peer.user_id
    if isinstance(input_peer, types.InputPeerChat):
        return "chat", input_peer.chat_id
    if isinstance(input_peer, (types.InputPeerChannel,
                               types.InputPeerChannelFromMessage)):
        return "channel", input_peer.channel_id
    if isinstance(input_peer, types.InputPeerSelf):
        return "self", 0
    return input_peer.__class__.__name__.lower(), int(
        getattr(input_peer, "user_id", None) or
        getattr(input_peer, "chat_id", None) or
        getattr(input_peer, "channel_id", 0))


def _entity_identity(entity_obj) -> Tuple[str, int]:
    return _get_peer_storage_type(entity_obj), int(entity_obj.id)


def serialize_peer_entity(entity_obj, dialog_obj: Dialog = None) -> TGPeerData:
    return TGPeerData(
        peer_id=int(entity_obj.id),
        username=getattr(entity_obj, "username", None),
        title=_get_peer_title(entity_obj=entity_obj, dialog_obj=dialog_obj),
        first_name_cst=getattr(entity_obj, "first_name", None),
        last_name_cst=getattr(entity_obj, "last_name", None),
        phone_cst=getattr(entity_obj, "phone", None),
        peer_type_cst=_get_peer_type(entity_obj),
        peer_storage_type=_get_peer_storage_type(entity_obj),
        peer_is_bot=bool(getattr(entity_obj, "bot", False)))


async def resolve_peer_entity(
        client: TelegramClient,
        peer_ref: TGPeerRef,
):
    username = (peer_ref.username or "").strip().lstrip("@")
    if username:
        entity_obj = await client.get_entity(username)
    else:
        entity_obj = None
        try:
            entity_obj = await client.get_entity(peer_ref.peer_id)
        except Exception:
            async for dialog_obj in client.iter_dialogs():
                candidate = dialog_obj.entity
                if getattr(candidate, "id", None) == peer_ref.peer_id:
                    entity_obj = candidate
                    break
        if entity_obj is None:
            raise ValueError("Telegram peer was not found")

    expected_storage = (peer_ref.peer_storage_type or "").strip().lower()
    if expected_storage:
        aliases = {"bot": "user", "group": "channel"}
        expected_storage = aliases.get(expected_storage, expected_storage)
        actual_storage = _get_peer_storage_type(entity_obj)
        if actual_storage != expected_storage:
            raise ValueError(
                "Resolved peer storage type is %s, expected %s" % (
                    actual_storage, expected_storage))
    return entity_obj


async def resolve_peer_refs(
        client: TelegramClient,
        peer_refs: Iterable[TGPeerRef],
        strict: bool = True,
) -> Tuple[List[object], List[TGPeerResolutionData]]:
    entities = []
    results = []
    seen = set()
    for peer_ref in peer_refs:
        try:
            entity_obj = await resolve_peer_entity(client, peer_ref)
            identity = _entity_identity(entity_obj)
            if identity not in seen:
                entities.append(entity_obj)
                seen.add(identity)
            results.append(TGPeerResolutionData(
                requested_peer=peer_ref,
                resolved=True,
                peer=serialize_peer_entity(entity_obj)))
        except Exception as error:
            if strict:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Could not resolve Telegram peer %s: %s [ERROR]" % (
                        peer_ref.model_dump(), error))
            results.append(TGPeerResolutionData(
                requested_peer=peer_ref,
                resolved=False,
                error=str(error)))
    return entities, results


async def _serialize_input_peer(client, input_peer) -> TGPeerData:
    try:
        if isinstance(input_peer, types.InputPeerSelf):
            entity_obj = await client.get_me()
        else:
            entity_obj = await client.get_entity(input_peer)
        return serialize_peer_entity(entity_obj)
    except Exception:
        storage_type, peer_id = _input_peer_identity(input_peer)
        return TGPeerData(
            peer_id=peer_id,
            title="Peer %s" % (peer_id,),
            peer_type_cst=storage_type,
            peer_storage_type=storage_type,
            peer_is_bot=False)


def _filter_title(filter_obj) -> str:
    title_obj = getattr(filter_obj, "title", None)
    return getattr(title_obj, "text", None) or str(title_obj or "")


async def serialize_folder_filter(client, filter_obj) -> TGFolderData:
    if isinstance(filter_obj, types.DialogFilterDefault):
        return TGFolderData(
            folder_id=0,
            folder_kind="default",
            title="All chats")

    if isinstance(filter_obj, types.DialogFilterChatlist):
        folder_kind = "chatlist"
    else:
        folder_kind = "custom"

    pinned = [await _serialize_input_peer(client, peer)
              for peer in getattr(filter_obj, "pinned_peers", [])]
    included = [await _serialize_input_peer(client, peer)
                for peer in getattr(filter_obj, "include_peers", [])]
    excluded = [await _serialize_input_peer(client, peer)
                for peer in getattr(filter_obj, "exclude_peers", [])]
    return TGFolderData(
        folder_id=filter_obj.id,
        folder_kind=folder_kind,
        title=_filter_title(filter_obj),
        emoticon=getattr(filter_obj, "emoticon", None),
        color=getattr(filter_obj, "color", None),
        title_noanimate=bool(getattr(filter_obj, "title_noanimate", False)),
        contacts=bool(getattr(filter_obj, "contacts", False)),
        non_contacts=bool(getattr(filter_obj, "non_contacts", False)),
        groups=bool(getattr(filter_obj, "groups", False)),
        broadcasts=bool(getattr(filter_obj, "broadcasts", False)),
        bots=bool(getattr(filter_obj, "bots", False)),
        exclude_muted=bool(getattr(filter_obj, "exclude_muted", False)),
        exclude_read=bool(getattr(filter_obj, "exclude_read", False)),
        exclude_archived=bool(getattr(filter_obj, "exclude_archived", False)),
        has_my_invites=bool(getattr(filter_obj, "has_my_invites", False)),
        pinned_peers=pinned,
        include_peers=included,
        exclude_peers=excluded)


async def get_dialog_filters(client) -> Tuple[List[object], bool]:
    response = await client(functions.messages.GetDialogFiltersRequest())
    if hasattr(response, "filters"):
        return list(response.filters), bool(getattr(response, "tags_enabled", False))
    return list(response), False


async def get_serialized_folders(client) -> Tuple[List[TGFolderData], bool]:
    filters, tags_enabled = await get_dialog_filters(client)
    folders = [await serialize_folder_filter(client, item) for item in filters]
    return folders, tags_enabled


async def get_folder_filter(client, folder_id: int):
    filters, _ = await get_dialog_filters(client)
    for filter_obj in filters:
        if getattr(filter_obj, "id", 0) == folder_id:
            return filter_obj
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Telegram folder %s was not found [ERROR]" % (folder_id,))


def _ensure_custom_filter(filter_obj) -> None:
    if not isinstance(filter_obj, types.DialogFilter):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Imported, default, and system folders cannot be modified by this endpoint [ERROR]")


async def get_next_folder_id(client) -> int:
    filters, _ = await get_dialog_filters(client)
    used_ids = {getattr(item, "id", 0) for item in filters}
    for folder_id in range(CUSTOM_FOLDER_ID_MIN, CUSTOM_FOLDER_ID_MAX + 1):
        if folder_id not in used_ids:
            return folder_id
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="No free Telegram folder ID is available [ERROR]")


async def build_dialog_filter(
        client: TelegramClient,
        folder_id: int,
        definition: TGFolderDefinition,
):
    include_entities, _ = await resolve_peer_refs(
        client, definition.include_peers)
    pinned_entities, _ = await resolve_peer_refs(
        client, definition.pinned_peers)
    exclude_entities, _ = await resolve_peer_refs(
        client, definition.exclude_peers)

    include_by_key = {_entity_identity(entity): entity
                      for entity in include_entities}
    for entity in pinned_entities:
        include_by_key.setdefault(_entity_identity(entity), entity)
    exclude_keys = {_entity_identity(entity) for entity in exclude_entities}
    conflict_keys = set(include_by_key).intersection(exclude_keys)
    if conflict_keys:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A peer cannot be both included and excluded: %s [ERROR]" % (
                sorted(conflict_keys),))

    has_dynamic_include = any((
        definition.contacts,
        definition.non_contacts,
        definition.groups,
        definition.broadcasts,
        definition.bots))
    if not include_by_key and not has_dynamic_include:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Folder must include peers or at least one peer category [ERROR]")

    pinned_inputs = [await client.get_input_entity(entity)
                     for entity in pinned_entities]
    include_inputs = [await client.get_input_entity(entity)
                      for entity in include_by_key.values()]
    exclude_inputs = [await client.get_input_entity(entity)
                      for entity in exclude_entities]
    return types.DialogFilter(
        id=folder_id,
        title=types.TextWithEntities(text=definition.title, entities=[]),
        emoticon=definition.emoticon,
        color=definition.color,
        title_noanimate=definition.title_noanimate,
        contacts=definition.contacts,
        non_contacts=definition.non_contacts,
        groups=definition.groups,
        broadcasts=definition.broadcasts,
        bots=definition.bots,
        exclude_muted=definition.exclude_muted,
        exclude_read=definition.exclude_read,
        exclude_archived=definition.exclude_archived,
        pinned_peers=pinned_inputs,
        include_peers=include_inputs,
        exclude_peers=exclude_inputs)


def _dialog_is_muted(dialog_obj: Dialog) -> bool:
    notify_settings = getattr(getattr(dialog_obj, "dialog", None),
                              "notify_settings", None)
    mute_until = getattr(notify_settings, "mute_until", None)
    if isinstance(mute_until, datetime):
        compare_to = datetime.now(tz=mute_until.tzinfo or timezone.utc)
        return mute_until > compare_to
    return bool(mute_until and mute_until > 0)


def _dialog_category_matches(dialog_obj: Dialog,
                             definition: TGFolderDefinition) -> Optional[str]:
    entity_obj = dialog_obj.entity
    if isinstance(entity_obj, types.User):
        if getattr(entity_obj, "bot", False):
            return "bots" if definition.bots else None
        if getattr(entity_obj, "contact", False):
            return "contacts" if definition.contacts else None
        return "non_contacts" if definition.non_contacts else None
    if isinstance(entity_obj, types.Chat) or getattr(entity_obj, "megagroup", False):
        return "groups" if definition.groups else None
    if isinstance(entity_obj, types.Channel):
        return "broadcasts" if definition.broadcasts else None
    return None


async def preview_folder_candidates(
        client: TelegramClient,
        definition: TGFolderDefinition,
        dialogs_limit: int,
) -> List[TGFolderCandidateData]:
    include_entities, _ = await resolve_peer_refs(
        client, definition.include_peers)
    pinned_entities, _ = await resolve_peer_refs(
        client, definition.pinned_peers)
    exclude_entities, _ = await resolve_peer_refs(
        client, definition.exclude_peers)
    include_keys = {_entity_identity(item) for item in include_entities}
    pinned_keys = {_entity_identity(item) for item in pinned_entities}
    exclude_keys = {_entity_identity(item) for item in exclude_entities}

    candidates = []
    async for dialog_obj in client.iter_dialogs(limit=dialogs_limit):
        identity = _entity_identity(dialog_obj.entity)
        reasons = []
        included = False
        if identity in exclude_keys:
            reasons.append("explicitly_excluded")
        elif identity in pinned_keys:
            included = True
            reasons.append("pinned")
        elif identity in include_keys:
            included = True
            reasons.append("explicitly_included")
        else:
            category = _dialog_category_matches(dialog_obj, definition)
            if category:
                included = True
                reasons.append(category)

        explicitly_included = identity in pinned_keys or identity in include_keys
        if included and not explicitly_included:
            if definition.exclude_archived and bool(
                    getattr(dialog_obj, "archived", False)):
                included = False
                reasons.append("excluded_archived")
            if definition.exclude_muted and _dialog_is_muted(dialog_obj):
                included = False
                reasons.append("excluded_muted")
            if definition.exclude_read and not (
                    getattr(dialog_obj, "unread_count", 0) or 0):
                included = False
                reasons.append("excluded_read")

        candidates.append(TGFolderCandidateData(
            peer=serialize_peer_entity(dialog_obj.entity, dialog_obj),
            included=included,
            reasons=reasons))
    return candidates


async def edit_archive_peers(
        client: TelegramClient,
        peer_refs: List[TGPeerRef],
        archived: bool,
) -> List[TGPeerData]:
    entities, _ = await resolve_peer_refs(client, peer_refs)
    folder_id = ARCHIVE_FOLDER_ID if archived else 0
    input_folder_peers = []
    for entity_obj in entities:
        input_peer = await client.get_input_entity(entity_obj)
        input_folder_peers.append(types.InputFolderPeer(
            peer=input_peer,
            folder_id=folder_id))
    await client(functions.folders.EditPeerFoldersRequest(
        folder_peers=input_folder_peers))
    return [serialize_peer_entity(entity_obj) for entity_obj in entities]


async def get_archive_dialogs(client: TelegramClient, limit: int) -> List[Dict]:
    dialogs = []
    async for dialog_obj in client.iter_dialogs(limit=limit, archived=True):
        dialogs.append(serialize_dialog_item(
            config_name="",
            dialog_obj=dialog_obj))
    return dialogs
