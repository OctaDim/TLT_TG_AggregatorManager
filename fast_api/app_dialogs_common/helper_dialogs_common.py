from datetime import datetime
from io import BytesIO
from typing import Dict, List, Optional, Tuple

from fastapi import HTTPException
from starlette import status
from telethon import TelegramClient
from telethon.tl.custom import Dialog
from telethon.tl.patched import Message
from telethon.tl.types import Channel, Chat, User

from configs.options import TELETHON_OPTIONS
from telethon_manager.telethon_client_config import TelethonConfig
from telethon_manager.telethon_clients_manager import (
    TelethonManagerSingleton)
from utils_specific.get_account_tlt_clients import (
    get_acc_only_started_tlt_clients)

SUPPORTED_MESSENGER_TYPES = ("telegram",)
SUPPORTED_PEER_STORAGE_TYPES = ("user", "chat", "channel")
SUPPORTED_PEER_TYPES = ("user", "chat", "group", "channel", "bot")


def validate_messenger_type(messenger_type: str) -> str:
    normalized_value = (messenger_type or "").strip().lower()
    if normalized_value not in SUPPORTED_MESSENGER_TYPES:
        error_log = (
            "Unsupported messenger_type passed [ERROR]:\n"
            "Supported values: {supported}\n"
            "messenger_type: {messenger_type}\n"
        ).format(
            supported=SUPPORTED_MESSENGER_TYPES,
            messenger_type=messenger_type,
        )
        print(error_log)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_log)
    return normalized_value


def validate_peer_type(peer_type: str) -> str:
    normalized_value = (peer_type or "").strip().lower()
    if normalized_value not in SUPPORTED_PEER_TYPES:
        error_log = (
            "Unsupported peer_type passed [ERROR]:\n"
            "Supported values: {supported}\n"
            "peer_type: {peer_type}\n"
        ).format(
            supported=SUPPORTED_PEER_TYPES,
            peer_type=peer_type,
        )
        print(error_log)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_log)
    return normalized_value


def validate_peer_storage_type(peer_storage_type: str) -> str:
    normalized_value = (peer_storage_type or "").strip().lower()
    if normalized_value not in SUPPORTED_PEER_STORAGE_TYPES:
        error_log = (
            "Unsupported peer_storage_type passed [ERROR]:\n"
            "Supported values: {supported}\n"
            "peer_storage_type: {peer_storage_type}\n"
        ).format(
            supported=SUPPORTED_PEER_STORAGE_TYPES,
            peer_storage_type=peer_storage_type,
        )
        print(error_log)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_log)
    return normalized_value


def _dt_to_iso(dt_value: datetime) -> Optional[str]:
    if not dt_value:
        return None
    return dt_value.isoformat()


def _message_text(message_obj: Message) -> str:
    if not message_obj:
        return ""
    return message_obj.message or message_obj.raw_text or ""


def _detect_media_type(message_obj: Message) -> Optional[str]:
    if not message_obj:
        return None
    if getattr(message_obj, "photo", None):
        return "photo"
    if getattr(message_obj, "video", None):
        return "video"
    if getattr(message_obj, "voice", None):
        return "voice"
    if getattr(message_obj, "audio", None):
        return "audio"
    if getattr(message_obj, "sticker", None):
        return "sticker"
    if getattr(message_obj, "document", None):
        return "document"
    if getattr(message_obj, "media", None):
        return "media"
    return None


def _get_peer_storage_type(entity_obj) -> str:
    if isinstance(entity_obj, User):
        return "user"
    if isinstance(entity_obj, Chat):
        return "chat"
    if isinstance(entity_obj, Channel):
        return "channel"

    if getattr(entity_obj, "user_id", None):
        return "user"
    if getattr(entity_obj, "chat_id", None):
        return "chat"
    return "channel"


def _get_peer_type(entity_obj) -> str:
    if isinstance(entity_obj, User):
        if getattr(entity_obj, "bot", False):
            return "bot"
        return "user"
    if isinstance(entity_obj, Chat):
        return "chat"
    if isinstance(entity_obj, Channel):
        if getattr(entity_obj, "megagroup", False):
            return "group"
        return "channel"

    if getattr(entity_obj, "bot", False):
        return "bot"
    if getattr(entity_obj, "megagroup", False):
        return "group"

    peer_storage_type = _get_peer_storage_type(entity_obj)
    if peer_storage_type == "user":
        return "user"
    if peer_storage_type == "chat":
        return "chat"
    return "channel"


def _get_peer_title(entity_obj, dialog_obj: Dialog = None) -> str:
    if dialog_obj and getattr(dialog_obj, "title", None):
        return dialog_obj.title

    if isinstance(entity_obj, User):
        first_name = getattr(entity_obj, "first_name", "") or ""
        last_name = getattr(entity_obj, "last_name", "") or ""
        full_name = ("%s %s" % (first_name, last_name)).strip()
        return (full_name or
                getattr(entity_obj, "username", None) or
                getattr(entity_obj, "phone", None) or
                "User %s" % (getattr(entity_obj, "id", ""),))

    return (getattr(entity_obj, "title", None) or
            getattr(entity_obj, "username", None) or
            "Peer %s" % (getattr(entity_obj, "id", ""),))


def can_send_to_entity(entity_obj) -> bool:
    if isinstance(entity_obj, User):
        return True

    if isinstance(entity_obj, Chat):
        return True

    if isinstance(entity_obj, Channel):
        if getattr(entity_obj, "megagroup", False):
            return True

        if getattr(entity_obj, "broadcast", False):
            admin_rights = getattr(entity_obj, "admin_rights", None)
            return bool(
                getattr(entity_obj, "creator", False) or
                getattr(admin_rights, "post_messages", False) or
                getattr(admin_rights, "send_messages", False))
        return True

    return True


async def get_allowed_started_account_clients(
        telethon_manager: TelethonManagerSingleton,
        web_account_id: str,
        web_account_username: str,
        allowed_configs: List[str],
) -> Dict[str, TelegramClient]:
    return await get_acc_only_started_tlt_clients(
        telethon_manager=telethon_manager,
        web_account_id=web_account_id,
        web_account_username=web_account_username,
        skip_disconnected=False,
        allowed_configs=allowed_configs)


async def get_single_account_client(
        telethon_manager: TelethonManagerSingleton,
        web_account_id: str,
        web_account_username: str,
        config_name: str,
) -> Tuple[TelegramClient, TelethonConfig]:
    acc_only_tlt_clients = await get_allowed_started_account_clients(
        telethon_manager=telethon_manager,
        web_account_id=web_account_id,
        web_account_username=web_account_username,
        allowed_configs=[config_name])

    telethon_client = acc_only_tlt_clients.get(config_name)
    telethon_config = telethon_manager.clients_configs.get(config_name)

    if not telethon_client or not telethon_config:
        error_log = (
            "Telethon configuration not found for web account [ERROR]:\n"
            "config_name: {config_name}\n"
            "web_account_id: {web_account_id}\n"
            "web_account_username: {web_account_username}\n"
        ).format(
            config_name=config_name,
            web_account_id=web_account_id,
            web_account_username=web_account_username,
        )
        print(error_log)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_log)

    if not telethon_client.is_connected():
        await telethon_client.connect()

    if not await telethon_client.is_user_authorized():
        error_log = (
            "Telethon client is not authorized [ERROR]:\n"
            "config_name: {config_name}\n"
        ).format(config_name=config_name)
        print(error_log)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=error_log)

    return telethon_client, telethon_config


async def resolve_dialog_entity(
        telethon_client: TelegramClient,
        peer_id: int,
        peer_storage_type: str,
):
    peer_storage_type = validate_peer_storage_type(peer_storage_type)

    try:
        entity_obj = await telethon_client.get_entity(entity=peer_id)
        if _get_peer_storage_type(entity_obj) == peer_storage_type:
            return entity_obj
    except Exception as direct_entity_error:
        print("Direct peer resolving skipped [INFO]: %s" % (
            direct_entity_error,))

    async for cur_dialog in telethon_client.iter_dialogs():
        cur_entity = cur_dialog.entity
        if getattr(cur_entity, "id", None) != peer_id:
            continue
        if _get_peer_storage_type(cur_entity) == peer_storage_type:
            return cur_entity

    error_log = (
        "Dialog peer entity not found [ERROR]:\n"
        "peer_id: {peer_id}\n"
        "peer_storage_type: {peer_storage_type}\n"
    ).format(
        peer_id=peer_id,
        peer_storage_type=peer_storage_type,
    )
    print(error_log)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=error_log)


def serialize_dialog_item(
        config_name: str,
        dialog_obj: Dialog,
) -> Dict[str, object]:
    entity_obj = dialog_obj.entity
    peer_id = getattr(entity_obj, "id", None)
    last_message_obj = getattr(dialog_obj, "message", None)
    peer_type = _get_peer_type(entity_obj)
    peer_storage_type = _get_peer_storage_type(entity_obj)

    return {
        "config_name": config_name,
        "peer_id": peer_id,
        "peer_type": peer_type,
        "peer_storage_type": peer_storage_type,
        "peer_key": "%s:%s:%s" % (config_name, peer_storage_type, peer_id),
        "peer_title": _get_peer_title(entity_obj=entity_obj,
                                       dialog_obj=dialog_obj),
        "peer_username": getattr(entity_obj, "username", None),
        "peer_first_name": getattr(entity_obj, "first_name", None),
        "peer_last_name": getattr(entity_obj, "last_name", None),
        "peer_phone": getattr(entity_obj, "phone", None),
        "peer_is_bot": bool(getattr(entity_obj, "bot", False)),
        "can_send": can_send_to_entity(entity_obj),
        "unread_count": getattr(dialog_obj, "unread_count", 0) or 0,
        "is_pinned": bool(getattr(dialog_obj, "pinned", False)),
        "last_message_id": getattr(last_message_obj, "id", None),
        "last_message_date": _dt_to_iso(getattr(last_message_obj, "date", None)),
        "last_message_text": _message_text(last_message_obj),
        "last_message_out": bool(getattr(last_message_obj, "out", False)),
        "has_draft": bool(getattr(dialog_obj, "draft", None)),
    }


def serialize_live_message(
        config_name: str,
        peer_id: int,
        peer_type: str,
        peer_storage_type: str,
        message_obj: Message,
) -> Dict[str, object]:
    file_data = getattr(message_obj, "file", None)
    reply_to_obj = getattr(message_obj, "reply_to", None)

    return {
        "config_name": config_name,
        "peer_id": peer_id,
        "peer_type": peer_type,
        "peer_storage_type": peer_storage_type,
        "message_id": getattr(message_obj, "id", None),
        "sender_id": getattr(message_obj, "sender_id", None),
        "date": _dt_to_iso(getattr(message_obj, "date", None)),
        "edit_date": _dt_to_iso(getattr(message_obj, "edit_date", None)),
        "text": _message_text(message_obj),
        "raw_text": getattr(message_obj, "raw_text", None) or "",
        "out": bool(getattr(message_obj, "out", False)),
        "from_me": bool(getattr(message_obj, "out", False)),
        "reply_to_msg_id": getattr(reply_to_obj, "reply_to_msg_id", None),
        "has_media": bool(getattr(message_obj, "media", None)),
        "media_type": _detect_media_type(message_obj),
        "file_name": getattr(file_data, "name", None),
        "file_mime_type": getattr(file_data, "mime_type", None),
        "file_size": getattr(file_data, "size", None),
    }


async def send_text_to_dialog_entity(
        telethon_client: TelegramClient,
        entity_obj,
        message_text: str,
):
    return await telethon_client.send_message(
        entity=entity_obj,
        message=message_text,
        parse_mode=TELETHON_OPTIONS.MESSAGES_PARSING_MODE)


async def send_files_to_dialog_entity(
        telethon_client: TelegramClient,
        entity_obj,
        files_data: List[Dict[str, object]],
        caption_text: str = "",
):
    sent_messages = []
    caption_prefix = TELETHON_OPTIONS.SEND_FILE_MESSAGE_CAPTION_PREFIX

    for file_data in files_data:
        file_name = file_data["file_name"]
        file_content = file_data["file_content"]
        file_mime_type = file_data.get("file_mime_type")

        file_obj = BytesIO(file_content)
        file_obj.name = file_name

        file_caption = caption_text or ""
        if not file_caption and file_name:
            file_caption = "%s %s" % (caption_prefix, file_name)

        message_obj = await telethon_client.send_file(
            entity=entity_obj,
            file=file_obj,
            file_name=file_name,
            caption=file_caption,
            mime_type=file_mime_type,
            force_document=TELETHON_OPTIONS.SEND_FILE_FORCE_AS_DOCUMENT)
        sent_messages.append(message_obj)

    return sent_messages

