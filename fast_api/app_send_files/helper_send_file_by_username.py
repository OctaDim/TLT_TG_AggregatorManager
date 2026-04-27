from typing import Dict

from telethon import TelegramClient
from telethon.tl.types import Message

from configs.options import TELETHON_OPTIONS


async def send_tg_file_by_username(
        telethon_client: TelegramClient,
        username: str,
        file_name: str,
        file_content: bytes,
        file_mime_type: str = None,
        telethon_config_name: str = None,
        force_document: bool = False
) -> Dict[str, Message | str]:
    username = (username or "").lstrip("@").lower()
    message_obj = None
    message_error = ""

    try:
        caption_prefix = TELETHON_OPTIONS.SEND_FILE_MESSAGE_CAPTION_PREFIX
        file_msg_caption = f"{caption_prefix} {file_name}" if file_name else None

        message_obj = await telethon_client.send_file(
            entity=username,
            file=file_content,
            caption=file_msg_caption,
            mime_type=file_mime_type,
            force_document=force_document
            # parse_mode=TELETHON_OPTIONS.MESSAGES_PARSING_MODE
        )
        if TELETHON_OPTIONS.LOG_TG_SEND_MSG_BY_USERNAME:
            print(f"\nTelegram file sent BY USERNAME [OK]:\n"
                  f"telethon_config_name: {telethon_config_name}\n"
                  f"username: {username}\n"
                  f"file_name: {file_name}\n"
                  f"message_obj: {message_obj}\n")
    except Exception as error:
        print(f"Sending telegram file by username [ERROR]:\n"
              f"error: {error}\n"
              f"telethon_client: {telethon_client}\n"
              f"tlt_config_name: {telethon_config_name}\n"
              f"username: {username}\n"
              f"file_name: {file_name}\n"
              f"message_obj: {message_obj}\n")
        message_error = str(error)

    sent_msg_result = {"message_object": message_obj,
                       "message_error": message_error}
    return sent_msg_result
