import asyncio
import mimetypes
import os
from typing import Dict

from aiofiles import os as aiofiles_os
from telethon import TelegramClient
from telethon.tl.types import DocumentAttributeFilename

from configs.console_colors import CONSOLE_COLORS
from configs.environments import BASE_DIR
from configs.options import TELETHON_OPTIONS
from fast_api.app_get_file_by_message_id.chain_message_doc_attrs import (
    get_tg_msg_doc_attrs)
from fast_api.app_get_file_by_message_id.chain_message_file_name import (
    get_tg_msg_file_name)
from fast_api.app_get_file_by_message_id.chain_message_mime_type import (
    get_tg_msg_file_mime_type)
from utils_common.get_obj_attrs_vals_by_attr_chain import (
    get_attrs_values_by_attr_chains)
from utils_common.normalized_path import get_full_dir_normal_path


async def get_tg_file_by_message_id(
        file_message_id: int,
        file_owner_peer_id: int,
        telethon_client: TelegramClient,
        telethon_config_name: str,
        custom_file_name: str = None
) -> Dict[str, str] | None:
    """Note: file_owner_peer_id can be channel_id, chat_id or user_id"""

    orig_is_connected = telethon_client.is_connected()
    file_result = {"file_path": "",
                   "file_name": "",
                   "file_mime_type": "",
                   "get_file_error": ""}
    try:
        if not orig_is_connected:
            await telethon_client.connect()
        after_conn_is_connected = telethon_client.is_connected()

        if not after_conn_is_connected:
            get_file_error = (
                f"Not connectable TLT telegram client [ERROR]: \n"
                f"file_message_id: {file_message_id} \n"
                f"file_owner_peer_id: {file_owner_peer_id} \n"
                f"orig_is_connected: {orig_is_connected} \n"
                f"after_conn_is_connected: {after_conn_is_connected} \n"
                f"telethon_config_name: {telethon_config_name} \n")
            print(get_file_error)
            file_result.update({"get_file_error": get_file_error})
            return file_result

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
                f"Peer ID Message object not found [ERROR]: \n"
                f"file_message_id: {file_message_id} \n"
                f"file_owner_peer_id: {file_owner_peer_id} \n"
                f"telethon_config_name: {telethon_config_name} \n"
                f"peer_id_msgs_objs: {peer_id_msgs_objs} \n"
                f"peer_id_msg_obj: {peer_id_msg_obj} \n")
            print(get_file_error)
            file_result.update({"get_file_error": get_file_error})
            return file_result

        if not hasattr(peer_id_msg_obj, "media") or not peer_id_msg_obj.media:
            get_file_error = (
                f"Media attribute empty or not found [ERROR]: \n"
                f"file_message_id: {file_message_id} \n"
                f"file_owner_peer_id: {file_owner_peer_id} \n"
                f"telethon_config_name: {telethon_config_name} \n"
                f"peer_id_msg_obj: {peer_id_msg_obj} \n"
                f"peer_id_msg_obj.media: {peer_id_msg_obj.media} \n")
            print(get_file_error)
            file_result.update({"get_file_error": get_file_error})
            return file_result

        base_tlt_files_dir = TELETHON_OPTIONS.TEMP_TG_DOWNLOADED_FILES_DIR
        temp_tlt_files_dir = get_full_dir_normal_path(
            all_dir_str_parts=[BASE_DIR, base_tlt_files_dir])
        await aiofiles_os.makedirs(temp_tlt_files_dir, exist_ok=True)

        try:
            async_task_fut_obj = telethon_client.download_media(
                message=peer_id_msg_obj,
                file=temp_tlt_files_dir)  # tg file name
            # TODO: Make separate thread or background_task execution
            media_file_path = await asyncio.wait_for(
                fut=async_task_fut_obj,
                timeout=TELETHON_OPTIONS.WAIT_FOR_DOWNLOAD_MEDIA_TIMEOUT_SEC)
        except asyncio.TimeoutError as download_timeout_error:
            get_file_error = (
                f"Download Telegram media timeout [ERROR]: \n"
                f"download_timeout_error: {download_timeout_error} \n"
                f"file_message_id: {file_message_id} \n"
                f"file_owner_peer_id: {file_owner_peer_id} \n"
                f"telethon_config_name: {telethon_config_name} \n"
                f"peer_id_msg_obj: {peer_id_msg_obj} \n"
                f"peer_id_msg_obj.media: {peer_id_msg_obj.media} \n"
                f"temp_tlt_files_dir: {temp_tlt_files_dir}")
            print(get_file_error)
            file_result.update({"get_file_error": get_file_error})
            return file_result
        except Exception as media_download_error:
            get_file_error = (
                f"Download Telegram media [ERROR]: \n"
                f"media_download_error: {media_download_error} \n"
                f"file_message_id: {file_message_id} \n"
                f"file_owner_peer_id: {file_owner_peer_id} \n"
                f"telethon_config_name: {telethon_config_name} \n"
                f"peer_id_msg_obj: {peer_id_msg_obj} \n"
                f"peer_id_msg_obj.media: {peer_id_msg_obj.media} \n"
                f"temp_tlt_files_dir: {temp_tlt_files_dir}")
            print(get_file_error)
            file_result.update({"get_file_error": get_file_error})
            return file_result

        # Mime type from message object
        separator = TELETHON_OPTIONS.EVENT_ATTRS_SECTION_SEPARATOR_PREFIX
        mime_type_params = await get_attrs_values_by_attr_chains(
            base_class_or_obj=peer_id_msg_obj,
            attributes_chains_dict=get_tg_msg_file_mime_type(),
            section_separator_prefix=separator)
        msg_media_doc_mime_type = mime_type_params["msg_media_doc_mime_type"]
        if msg_media_doc_mime_type:
            file_mime_type = msg_media_doc_mime_type
        else:
            file_mime_type, encoding = mimetypes.guess_type(
                url=media_file_path,
                strict=True)
            if not file_mime_type:
                file_mime_type = "application/octet-stream"

        # File name from custom file name
        if custom_file_name:
            file_name = custom_file_name
        else:
            file_name = ""

        # File name from message object
        if not file_name:
            file_name_params = await get_attrs_values_by_attr_chains(
                base_class_or_obj=peer_id_msg_obj,
                attributes_chains_dict=get_tg_msg_file_name(),
                section_separator_prefix=separator)
            msg_file_name = file_name_params["msg_file_name"]
            if msg_file_name:
                file_name = msg_file_name

        # File name from message attributes
        if not file_name:
            doc_attrs_params = await get_attrs_values_by_attr_chains(
                base_class_or_obj=peer_id_msg_obj,
                attributes_chains_dict=get_tg_msg_doc_attrs(),
                section_separator_prefix=separator)
            msg_media_doc_attrs = doc_attrs_params["msg_media_doc_attrs"]
            if msg_media_doc_attrs:
                for cur_attr in msg_media_doc_attrs:
                    if isinstance(cur_attr, DocumentAttributeFilename):
                        file_name = cur_attr.file_name
                        break

        # File name from download path
        if not file_name:
            file_name = os.path.basename(media_file_path)

        file_result.update({"file_path": media_file_path,
                            "file_name": file_name,
                            "file_mime_type": file_mime_type})
        yellow_clr = CONSOLE_COLORS.BRIGHT_YELLOW
        magenta_clr = CONSOLE_COLORS.BRIGHT_MAGENTA
        reset_color = CONSOLE_COLORS.RESET
        print(f"Message object file received successfully [OK]:\n"
              f"file_path: {media_file_path}\n"
              f"file_path: {file_mime_type}\n"
              f"file_path: {yellow_clr}{file_name}{reset_color}\n")
        return file_result
    except Exception as error:
        message_error = (f"Download File from Msg by Peer ID [ERROR]: \n"
                         f"error: {error} \n"
                         f"file_message_id: {file_message_id} \n"
                         f"file_owner_peer_id: {file_owner_peer_id} \n"
                         f"telethon_config_name: {telethon_config_name} \n")
        print(message_error)
        file_result.update({"get_file_error": message_error})
        return file_result
    finally:
        # TODO: Temporary unattach handlers not to get or not to send msgs by client
        if not orig_is_connected:
            telethon_client.disconnect()
