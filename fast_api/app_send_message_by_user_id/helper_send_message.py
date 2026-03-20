from typing import Dict

from telethon import TelegramClient
from telethon.tl.types import Message

from configs.settings import TELETHON_OPTIONS


async def send_tg_message_by_username(
        telethon_client: TelegramClient,
        username: str,
        message_text: str,
        telethon_config_name: str = None,
) -> Dict[str, Message | str]:
    username = (username or "").lstrip("@").lower()
    message_obj = None
    message_error = ""

    try:
        message_obj = await telethon_client.send_message(
            entity=username, message=message_text)
        if TELETHON_OPTIONS.LOG_TG_SEND_MSG_BY_USERNAME:
            print(f"\nTelegram message sent BY USERNAME [OK]:\n"
                  f"telethon_config_name: {telethon_config_name}\n"
                  f"username: {username}\n"
                  f"message_text: {message_text}\n"
                  f"message_obj: {message_obj}\n")
    except Exception as error:
        print(f"Sending telegram message by username [ERROR]:\n"
              f"error: {error}\n"
              f"telethon_client: {telethon_client}\n"
              f"tlt_config_name: {telethon_config_name}\n"
              f"username: {username}\n"
              f"message_text: {message_text}\n"
              f"message_obj: {message_obj}\n")
        message_error = error

    sent_msg_result = {"message_object": message_obj,
                       "sent_msg_error": message_error}
    return sent_msg_result


async def send_tg_message_by_user_id(
        telethon_client: TelegramClient,
        user_id: int,
        message_text: str,
        telethon_config_name: str = None,
) -> Dict[str, Message | str]:
    message_obj = None
    message_error = ""

    try:
        message_obj = await telethon_client.send_message(
            entity=user_id, message=message_text)
        if TELETHON_OPTIONS.LOG_TG_SEND_MSG_BY_USERNAME:
            print(f"\nTelegram message sent BY USER_ID [OK]:\n"
                  f"telethon_config_name: {telethon_config_name}\n"
                  f"user_id: {user_id}\n"
                  f"message_text: {message_text}\n"
                  f"message_obj: {message_obj}\n")
    except Exception as error:
        print(f"Sending telegram message by user_id [ERROR]:\n"
              f"error: {error}\n"
              f"telethon_client: {telethon_client}\n"
              f"tlt_config_name: {telethon_config_name}\n"
              f"user_id: {user_id}\n"
              f"message_text: {message_text}\n"
              f"message_obj: {message_obj}\n")
        message_error = error

    sent_msg_result = {"message_object": message_obj,
                       "sent_msg_error": message_error}
    return sent_msg_result
