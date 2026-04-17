import os
from aiofiles import os as aiofiles_os

from telethon.tl.patched import Message
from telethon.tl.types import (
    MessageMediaPhoto, DocumentAttributeVideo, DocumentAttributeAudio,
    DocumentAttributeFilename)

from configs.aggregator_api_urls import AGGREGATOR_API_WEBHOOKS_URL
from configs.environments import BASE_DIR
from configs.labels_messages import ACTION_STATUS
from configs.options import AGGREGATOR_API_OPTIONS, TELETHON_OPTIONS
from fast_api.app_web_account.scheme_web_account import InWebAccountData
from telethon_manager.telethon_attrs_chains.chain_doc_attr_audio import (
    get_doc_attr_audio_attr_chains)
from telethon_manager.telethon_attrs_chains.chain_doc_attr_file_name import (
    get_doc_attr_file_name_attr_chains)
from telethon_manager.telethon_attrs_chains.chain_doc_attr_video import (
    get_doc_attr_video_attr_chains)
from telethon_manager.telethon_attrs_chains.chain_message_client_sent_text import (
    get_client_sent_msg_text_attr_chains)
from telethon_manager.telethon_attrs_chains.chain_message_new_edit import (
    get_event_new_edit_msg_attr_chains)
from telethon_manager.telethon_client_config import TelethonConfig
from utils_common.clean_str_new_lines_spaces import group_clean_text
from utils_common.get_obj_attrs_vals_by_attr_chain import (
    get_attrs_values_by_attr_chains)
from utils_common.normalized_path import get_full_dir_normal_path
from utils_common.serialize_custom_json import get_only_jsonable_values
from utils_specific.event_params_detailed_log import log_all_event_params
from utils_specific.send_event_data_webhook import (
    send_event_data_webhook_req)


async def tlt_client_sent_msg_special_helper(
        message_object: Message,
        telethon_config: TelethonConfig,
) -> None:
    separator = TELETHON_OPTIONS.EVENT_ATTRS_SECTION_SEPARATOR_PREFIX
    action_str = ACTION_STATUS.TLT_CLIENT_SENT_NEW_MSG_ACTION_STR
    event_type = "ClientSentNewMessage"
    tlt_sent_msg_spec_params = {}

    # Getting TLT sent message object text params
    tlt_sent_msg_obj_texts_params = await get_attrs_values_by_attr_chains(
        base_class_or_obj=message_object,
        attributes_chains_dict=get_client_sent_msg_text_attr_chains(),
        section_separator_prefix=separator)
    cleaned_texts_params = await group_clean_text(
        origin_texts=tlt_sent_msg_obj_texts_params,
        strip_spaces=True,
        clean_line_breaks=True,
        clean_continuous_spaces=True)
    tlt_sent_msg_spec_params.update(cleaned_texts_params)
    
    # Getting TLT sent message object specific params
    tlt_sent_msg_obj_main_params = await get_attrs_values_by_attr_chains(
        base_class_or_obj=message_object,
        attributes_chains_dict=get_event_new_edit_msg_attr_chains(),
        section_separator_prefix=separator)
    tlt_sent_msg_spec_params.update(tlt_sent_msg_obj_main_params)

    ev__client = tlt_sent_msg_obj_main_params["ev__client"]
    ev_media = tlt_sent_msg_obj_main_params["ev_media"]
    ev_media_doc_attrs = tlt_sent_msg_obj_main_params["ev_media_document_attributes"]

    if isinstance(ev_media, MessageMediaPhoto):
        ev_media_photo = tlt_sent_msg_obj_main_params["ev_media_photo"]
        if ev_media_photo and TELETHON_OPTIONS.DOWNLOAD_PHOTO_FILE_NAME:
            base_tlt_files_dir = TELETHON_OPTIONS.TEMP_TG_DOWNLOADED_FILES_DIR
            temp_tlt_files_dir = get_full_dir_normal_path(
                [BASE_DIR, base_tlt_files_dir])
            await aiofiles_os.makedirs(temp_tlt_files_dir, exist_ok=True)
            # os.makedirs(temp_tlt_files_dir, exist_ok=True)  # Sync
            temp_file_path = await ev__client.download_media(
                ev_media_photo, file=temp_tlt_files_dir)  # tg file name
            # temp_file_path = await ev__client.download_media(ev_media_photo, file=bytes)
            if await aiofiles_os.path.exists(temp_file_path):
            # if os.path.exists(temp_file_path):  # Sync
                await aiofiles_os.remove(temp_file_path)
                # os.remove(temp_file_path)  # Sync
            file_name_cst = os.path.basename(temp_file_path)
            tlt_sent_msg_spec_params.update({"file_name_cst": file_name_cst})
            action_str = f"{action_str}+{ACTION_STATUS.PHOTO_ATTACH_ACTION_STR}"
    elif ev_media_doc_attrs:
        for cur_doc_attr_obj in ev_media_doc_attrs:
            if isinstance(cur_doc_attr_obj, DocumentAttributeVideo):
                video_params = await get_attrs_values_by_attr_chains(
                    base_class_or_obj=cur_doc_attr_obj,
                    attributes_chains_dict=get_doc_attr_video_attr_chains(),
                    section_separator_prefix=separator)
                ev_media_doc = tlt_sent_msg_obj_main_params["ev_media_document"]
                if (not video_params["doc_attr_file_name"] and ev_media_doc
                        and TELETHON_OPTIONS.DOWNLOAD_VIDEO_FILE_NAME):
                    base_tlt_files_dir = TELETHON_OPTIONS.TEMP_TG_DOWNLOADED_FILES_DIR
                    temp_tlt_files_dir = get_full_dir_normal_path(
                        [BASE_DIR, base_tlt_files_dir])
                    await aiofiles_os.makedirs(temp_tlt_files_dir, exist_ok=True)
                    # os.makedirs(temp_tlt_files_dir, exist_ok=True)  # Sync
                    temp_file_path = await ev__client.download_media(
                        ev_media_doc, file=temp_tlt_files_dir)  # tg file name
                    # temp_file_path = await ev__client.download_media(ev_media_doc, file=bytes)
                    if await aiofiles_os.path.exists(temp_file_path):
                    # if os.path.exists(temp_file_path):  # Sync
                        await aiofiles_os.remove(temp_file_path)
                        # os.remove(temp_file_path)  # Sync
                    file_name_cst = os.path.basename(temp_file_path)
                    video_params.update({"file_name_cst": file_name_cst})
                tlt_sent_msg_spec_params.update(video_params)
                action_str = f"{action_str}+{ACTION_STATUS.VIDEO_ATTACH_ACTION_STR}"
            elif isinstance(cur_doc_attr_obj, DocumentAttributeAudio):
                audio_params = await get_attrs_values_by_attr_chains(
                    base_class_or_obj=cur_doc_attr_obj,
                    attributes_chains_dict=get_doc_attr_audio_attr_chains(),
                    section_separator_prefix=separator)
                file_name_cst = audio_params["doc_attr_file_name"]
                audio_params.update({"file_name_cst": file_name_cst})
                tlt_sent_msg_spec_params.update(audio_params)
                action_str = f"{action_str}+{ACTION_STATUS.AUDIO_ATTACH_ACTION_STR}"
            elif isinstance(cur_doc_attr_obj, DocumentAttributeFilename):
                document_params = await get_attrs_values_by_attr_chains(
                    base_class_or_obj=cur_doc_attr_obj,
                    attributes_chains_dict=get_doc_attr_file_name_attr_chains(),
                    section_separator_prefix=separator)
                file_name_cst = document_params["doc_attr_file_name"]
                document_params.update({"file_name_cst": file_name_cst})
                tlt_sent_msg_spec_params.update(document_params)
                action_str = f"{action_str}+{ACTION_STATUS.DOC_ATTACH_ACTION_STR}"

    tlt_sent_msg_spec_params.update({"action": action_str})

    if telethon_config.bot_token:
        tlt_bot_token_info = telethon_config.bot_token[:10]
    else:
        tlt_bot_token_info = None

    all_tlt_sent_msg_params = {
        "event_type": event_type,
        "web_account_id": telethon_config.web_account_id,
        "web_account_username": telethon_config.web_account_username,
        "tlt_account_type": telethon_config.account_type.value,
        "tlt_phone": telethon_config.phone,
        "tlt_bot_token": tlt_bot_token_info,
        separator: ""}

    all_tlt_sent_msg_params.update(tlt_sent_msg_spec_params)

    if TELETHON_OPTIONS.LOG_ALL_BEFORE_JSON_EVENT_PARAMS:
        await log_all_event_params(
            log_title=f"EVENT: {event_type} [PRELIMINARY]",
            event_params_dict=all_tlt_sent_msg_params)

    jsonable_event_params = await get_only_jsonable_values(
        all_values=all_tlt_sent_msg_params,
        separator=TELETHON_OPTIONS.EVENT_ATTRS_SECTION_SEPARATOR_PREFIX,
        log_invalid_json=TELETHON_OPTIONS.LOG_NON_JSON_SERIALIZABLE_OBJ)

    if TELETHON_OPTIONS.LOG_ALL_AFTER_JSON_EVENT_PARAMS:
        await log_all_event_params(
            log_title=f"EVENT: {event_type} [JSONABLE]",
            event_params_dict=jsonable_event_params)

    # Direct sending Message object params to MessageAggregator API as it
    # doesn't initiate event with Event when sending message directly through TLT client
    await send_event_data_webhook_req(
        new_event_data=jsonable_event_params,
        source=AGGREGATOR_API_OPTIONS.SOURCE_STRING_FOR_EXT_AGGREGATOR,
        operation="TLTClientSentNewMessage",
        aggregator_url=AGGREGATOR_API_WEBHOOKS_URL)
