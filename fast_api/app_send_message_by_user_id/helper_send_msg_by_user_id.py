from typing import Dict

from telethon import TelegramClient
from telethon.tl.types import Message

from configs.options import TELETHON_OPTIONS


async def send_tg_message_by_user_id(
        telethon_client: TelegramClient,
        user_id: int,
        message_text: str,
        telethon_config_name: str = None,
) -> Dict[str, Message | str]:
    message_obj = None
    message_error = ""

    try:
        user_entity = await telethon_client.get_entity(entity=user_id)
        message_obj = await telethon_client.send_message(
            entity=user_entity,
            message=message_text,
            parse_mode=TELETHON_OPTIONS.MESSAGES_PARSING_MODE)
    except ValueError as direct_entity_error:
        message_error = (f"Direct message via entity by user_id [ERROR]:\n"
                         f"direct_entity_error: {direct_entity_error}\n"
                         f"user_id: {user_id}\n")
        print(message_error)

    if not message_obj:
        try:
            async for cur_dialog in telethon_client.iter_dialogs():
                if cur_dialog.entity.id == user_id:
                    message_obj = await telethon_client.send_message(
                        entity=cur_dialog.entity,
                        message=message_text,
                        parse_mode=TELETHON_OPTIONS.MESSAGES_PARSING_MODE)
                    break
            if not message_obj:
                message_error = (
                    f"{message_error}\n"
                    f"User_id not found in all dialogs [ERROR]:\n"
                    f"user_id: {user_id}\n")
                print(message_error)
        except Exception as dialogs_entity_error:
            message_error = (
                f"{message_error}\n"
                f"Message via entity by user_id in dialogs [ERROR]:\n"
                f"dialogs_entity_error: {dialogs_entity_error}\n"
                f"user_id: {user_id}\n")

    if not message_obj and TELETHON_OPTIONS.TRY_SEND_MSG_VIA_GROUP_USER_ID:
        try:
            search_limit_opt = TELETHON_OPTIONS.TRY_SEND_MSG_VIA_GROUP_LIMIT
            exit_ext_loop_flag = False
            async for cur_dialog in telethon_client.iter_dialogs():
                if exit_ext_loop_flag:
                    break
                async for members in telethon_client.iter_participants(
                        entity=cur_dialog.entity,
                        limit=search_limit_opt):
                    if members.id == user_id:
                        message_obj = await telethon_client.send_message(
                            entity=members,
                            message=message_text,
                            parse_mode=TELETHON_OPTIONS.MESSAGES_PARSING_MODE)
                        exit_ext_loop_flag = True
                        break
            if not message_obj:
                message_error = (
                    f"{message_error}\n"
                    f"User_id not found in all groups-channels [ERROR]:\n"
                    f"user_id: {user_id}\n"
                    f"search_limit_opt: {search_limit_opt}\n")
                print(message_error)
        except Exception as groups_entity_error:
            message_error = (
                f"{message_error}\n"
                f"Message via entity by user_id in groups-channels [ERROR]:\n"
                f"groups_entity_error: {groups_entity_error}\n"
                f"user_id: {user_id}\n")

    if message_obj and TELETHON_OPTIONS.LOG_TG_SEND_MSG_BY_USERNAME:
        print(f"\nTelegram message sent BY USER_ID [OK]:\n"
              f"telethon_config_name: {telethon_config_name}\n"
              f"user_id: {user_id}\n"
              f"message_text: {message_text}\n"
              f"message_obj: {message_obj}\n")
    else:
        message_error = (f"{message_error}\n"
                         f"telethon_client: {telethon_client}\n"
                         f"tlt_config_name: {telethon_config_name}\n"
                         f"user_id: {user_id}\n"
                         f"message_text: {message_text}\n"
                         f"message_obj: {message_obj}\n")

    sent_msg_result = {"message_object": message_obj,
                       "message_error": message_error}
    return sent_msg_result
