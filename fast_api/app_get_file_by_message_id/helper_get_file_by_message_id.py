from typing import Dict

from aiofiles import os as aiofiles_os
from telethon import TelegramClient

from configs.environments import BASE_DIR
from configs.options import TELETHON_OPTIONS
from utils_common.normalized_path import get_full_dir_normal_path


async def get_tg_file_by_message_id(
        file_message_id: int,
        file_owner_peer_id: int,
        telethon_client: TelegramClient,
        telethon_config_name: str,
) -> Dict[str, str]:
    """Note: file_owner_peer_id can be channel_id, chat_id or user_id"""

    orig_is_connected = telethon_client.is_connected()

    try:
        if not orig_is_connected:
            await telethon_client.connect()
        after_conn_is_connected = telethon_client.is_connected()

        if not after_conn_is_connected:
            get_file_error = (
                "Not connectable TLT telegram client [ERROR]: \n"
                f"file_message_id: {file_message_id} \n"
                f"file_owner_peer_id: {file_owner_peer_id} \n"
                f"orig_is_connected: {orig_is_connected} \n"
                f"after_conn_is_connected: {after_conn_is_connected} \n"
                f"telethon_config_name: {telethon_config_name} \n")
            print(get_file_error)
            get_file_result = {"file path": "",
                               "get_file_error": get_file_error}
            return get_file_result

        try:
            peer_id_msgs_objs = await telethon_client.get_messages(
                file_owner_peer_id, ids=file_message_id)
        except (ValueError, Exception) as get_msg_error:
            await telethon_client.get_dialogs()
            peer_id_msgs_objs = await telethon_client.get_messages(
                file_owner_peer_id, ids=file_message_id)

        if isinstance(peer_id_msgs_objs, list):
            peer_id_msg_obj = peer_id_msgs_objs[0]
        else:
            peer_id_msg_obj = peer_id_msgs_objs

        if not peer_id_msg_obj:
            get_file_error = (
                "Peer ID Message object not found [ERROR]: \n"
                f"file_message_id: {file_message_id} \n"
                f"file_owner_peer_id: {file_owner_peer_id} \n"
                f"telethon_config_name: {telethon_config_name} \n"
                f"peer_id_msgs_objs: {peer_id_msgs_objs} \n"
                f"peer_id_msg_obj: {peer_id_msg_obj} \n")
            print(get_file_error)
            get_file_result = {"file path": "",
                               "get_file_error": get_file_error}
            return get_file_result

        if not hasattr(peer_id_msg_obj, "media") or not peer_id_msg_obj.media:
            get_file_error = (
                "Media attribute empty or not found [ERROR]: \n"
                f"file_message_id: {file_message_id} \n"
                f"file_owner_peer_id: {file_owner_peer_id} \n"
                f"telethon_config_name: {telethon_config_name} \n"
                f"peer_id_msg_obj: {peer_id_msg_obj} \n"
                f"peer_id_msg_obj.media: {peer_id_msg_obj.media} \n")
            print(get_file_error)
            get_file_result = {"file path": "",
                               "get_file_error": get_file_error}
            return get_file_result

        base_tlt_files_dir = TELETHON_OPTIONS.TEMP_TG_DOWNLOADED_FILES_DIR
        temp_tlt_files_dir = get_full_dir_normal_path(
            all_dir_str_parts=[BASE_DIR, base_tlt_files_dir])
        await aiofiles_os.makedirs(temp_tlt_files_dir, exist_ok=True)

        media_file_path = await telethon_client.download_media(
            peer_id_msg_obj, file=temp_tlt_files_dir)  # tg file name
        # media_file_path = await ev__client.download_media(peer_id_msg_obj, file=bytes)  # To memory
        get_file_result = {"file path": media_file_path,
                           "get_file_error": ""}
        return get_file_result
    except Exception as get_file_error:
        message_error = (
            f"Downloading File from Message by Peer ID [ERROR]: \n"
            f"get_file_error: {get_file_error} \n"
            f"file_message_id: {file_message_id} \n"
            f"file_owner_peer_id: {file_owner_peer_id} \n"
            f"telethon_config_name: {telethon_config_name} \n")
        print(message_error)
        get_file_result = {"file path": "",
                           "get_file_error": get_file_error}
        return get_file_result
    finally:
        telethon_client.disconnect() if not orig_is_connected else None
