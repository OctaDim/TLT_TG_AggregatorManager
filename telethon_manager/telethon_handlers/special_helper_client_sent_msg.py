import os

import aiofiles
import aioshutil
from aiofiles import os as aiofiles_os
from telethon.tl.patched import Message
from telethon.tl.types import (
    MessageMediaPhoto, DocumentAttributeVideo, DocumentAttributeAudio,
    DocumentAttributeFilename)

from configs.aggregator_api_urls import AGGREGATOR_API_WEBHOOKS_URL
from configs.environments import (
    BASE_DIR, S3_DEFAULT_BUCKET, S3_REGION_NAME, S3_API_ENDPOINT)
from configs.labels_messages import ACTION_STATUS
from configs.options import AGGREGATOR_API_OPTIONS, TELETHON_OPTIONS
from s3_async_managers.s3_aiobotocore_manager import AioBotoCoreManager
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
from utils_common.check_create_s3_bucket import check_create_s3_bucket
from utils_common.clean_str_new_lines_spaces import group_clean_text
from utils_common.get_file_name_extra_part import get_file_name_with_extra_part
from utils_common.get_obj_attrs_vals_by_attr_chain import (
    get_attrs_values_by_attr_chains)
from utils_common.normalized_path import get_full_dir_normal_path, get_full_file_normal_path
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
    archive_file_prefix = TELETHON_OPTIONS.DOWNLOADED_ARCHIVE_FILES_PREFIX
    event_type = "ClientSentNewMessage"
    tlt_sent_msg_spec_params = {}

    # Getting TLT sent message object text params
    tlt_sent_msg_obj_text_params = await get_attrs_values_by_attr_chains(
        base_class_or_obj=message_object,
        attributes_chains_dict=get_client_sent_msg_text_attr_chains(),
        section_separator_prefix=separator)
    cleaned_texts_params = await group_clean_text(
        origin_texts=tlt_sent_msg_obj_text_params,
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
        if ev_media_photo and TELETHON_OPTIONS.DOWNLOAD_PHOTO_TO_GET_FILE_NAME:
            base_tlt_files_dir = TELETHON_OPTIONS.TEMP_TG_DOWNLOADED_FILES_DIR
            temp_tlt_files_dir = get_full_dir_normal_path(
                [BASE_DIR, base_tlt_files_dir])
            await aiofiles_os.makedirs(temp_tlt_files_dir, exist_ok=True)
            temp_file_path = await ev__client.download_media(
                ev_media_photo, file=temp_tlt_files_dir)  # tg file name
            # temp_file_path = await ev__client.download_media(ev_media_photo, file=bytes)  # To memory

            arch_file_extra_path = ""
            extra_saved_mark = ""
            if (TELETHON_OPTIONS.SERVER_SAVE_MESSAGE_PHOTO_FILE
                    or TELETHON_OPTIONS.S3_SAVE_MESSAGE_PHOTO_FILE):
                base_arch_files_dir = TELETHON_OPTIONS.ARCHIVE_TLT_TG_FILES_DIR
                arch_tlt_files_dir = get_full_dir_normal_path(
                    [BASE_DIR, base_arch_files_dir])
                await aiofiles_os.makedirs(arch_tlt_files_dir,
                                           exist_ok=True)

                temp_arch_file_name = os.path.basename(temp_file_path)
                temp_arch_file_path = get_full_file_normal_path(
                    all_dir_str_parts=[arch_tlt_files_dir],
                    file_name_with_ext=temp_arch_file_name)

                arch_file_extra_path = get_file_name_with_extra_part(
                    orig_file_full_path=temp_arch_file_path,
                    filename_prefix=archive_file_prefix)
                extra_file_name = os.path.basename(arch_file_extra_path)
            else:
                extra_file_name = None

            if TELETHON_OPTIONS.SERVER_SAVE_MESSAGE_PHOTO_FILE:
                await aioshutil.copy2(src=temp_file_path,
                                      dst=arch_file_extra_path)
                server_saved_mark = TELETHON_OPTIONS.SERVER_SAVED_FILE_ACTION_MARK
                extra_saved_mark = f"{extra_saved_mark}{server_saved_mark}"

            s3_bucket, s3_key, s3_endpoint, s3_uri = "", "", "", ""
            if TELETHON_OPTIONS.S3_SAVE_MESSAGE_PHOTO_FILE:
                async with AioBotoCoreManager() as s3_manager:
                    s3_client = await s3_manager.get_client()
                    s3_bucket_res = await check_create_s3_bucket(
                        s3_client=s3_client,
                        s3_bucket_name=S3_DEFAULT_BUCKET,
                        s3_region_name=S3_REGION_NAME)

                    if s3_bucket_res.valid_bucket:
                        async with aiofiles.open(
                                file=temp_file_path, mode="rb") as f_obj:
                            file_data = await f_obj.read()
                            await s3_client.put_object(
                                # ContentType='image/jpeg'
                                Bucket=S3_DEFAULT_BUCKET,
                                Key=extra_file_name,
                                Body=file_data)

                        s3_bucket = S3_DEFAULT_BUCKET
                        s3_key = extra_file_name
                        s3_endpoint = (f"{S3_API_ENDPOINT}/"
                                       f"{S3_DEFAULT_BUCKET}/"
                                       f"{extra_file_name}")
                        s3_uri = (f"s3://{S3_DEFAULT_BUCKET}/"
                                  f"{extra_file_name}")

                        s3_saved_mark = TELETHON_OPTIONS.S3_SAVED_FILE_ACTION_MARK
                        extra_saved_mark = f"{extra_saved_mark}{s3_saved_mark}"

            file_name_cst = os.path.basename(temp_file_path)
            file_name_params = {"file_name_cst": file_name_cst,
                                "extra_file_name_cst": extra_file_name}
            tlt_sent_msg_spec_params.update(file_name_params)

            s3_aws_params = {"s3_bucket": s3_bucket,
                             "s3_key": s3_key,
                             "s3_endpoint": s3_endpoint,
                             "s3_uri": s3_uri}
            tlt_sent_msg_spec_params.update(s3_aws_params)

            if await aiofiles_os.path.exists(temp_file_path):
                await aiofiles_os.remove(temp_file_path)
            action_str = (f"{action_str}+{ACTION_STATUS.PHOTO_ATTACH_ACTION_STR}"
                          f"{extra_saved_mark}")
    elif ev_media_doc_attrs:
        for cur_doc_attr_obj in ev_media_doc_attrs:
            if isinstance(cur_doc_attr_obj, DocumentAttributeVideo):
                ev_media_doc = tlt_sent_msg_obj_main_params["ev_media_document"]
                video_params = await get_attrs_values_by_attr_chains(
                    base_class_or_obj=cur_doc_attr_obj,
                    attributes_chains_dict=get_doc_attr_video_attr_chains(),
                    section_separator_prefix=separator)
                tlt_sent_msg_spec_params.update(video_params)

                if (video_params["doc_attr_file_name"]
                        and not TELETHON_OPTIONS.SERVER_SAVE_MESSAGE_VIDEO_FILE):
                    file_name_cst = video_params["doc_attr_file_name"]
                    extra_file_name = None
                    file_name_params = {"file_name_cst": file_name_cst,
                                        "extra_file_name_cst": extra_file_name}
                    tlt_sent_msg_spec_params.update(file_name_params)
                    action_str = f"{action_str}+{ACTION_STATUS.VIDEO_ATTACH_ACTION_STR}"
                elif ev_media_doc and TELETHON_OPTIONS.DOWNLOAD_VIDEO_TO_GET_FILE_NAME:
                    base_tlt_files_dir = TELETHON_OPTIONS.TEMP_TG_DOWNLOADED_FILES_DIR
                    temp_tlt_files_dir = get_full_dir_normal_path(
                        [BASE_DIR, base_tlt_files_dir])
                    await aiofiles_os.makedirs(temp_tlt_files_dir, exist_ok=True)
                    temp_file_path = await ev__client.download_media(
                        ev_media_doc, file=temp_tlt_files_dir)  # tg file name
                    # temp_file_path = await ev__client.download_media(ev_media_doc, file=bytes)  # To memory

                    arch_file_extra_path = ""
                    extra_saved_mark = ""
                    if (TELETHON_OPTIONS.SERVER_SAVE_MESSAGE_VIDEO_FILE
                            or TELETHON_OPTIONS.S3_SAVE_MESSAGE_VIDEO_FILE):
                        base_arch_files_dir = TELETHON_OPTIONS.ARCHIVE_TLT_TG_FILES_DIR
                        arch_tlt_files_dir = get_full_dir_normal_path(
                            [BASE_DIR, base_arch_files_dir])
                        await aiofiles_os.makedirs(arch_tlt_files_dir,
                                                   exist_ok=True)

                        temp_arch_file_name = os.path.basename(temp_file_path)
                        temp_arch_file_path = get_full_file_normal_path(
                            all_dir_str_parts=[arch_tlt_files_dir],
                            file_name_with_ext=temp_arch_file_name)

                        arch_file_extra_path = get_file_name_with_extra_part(
                            orig_file_full_path=temp_arch_file_path,
                            filename_prefix=archive_file_prefix)
                        extra_file_name = os.path.basename(arch_file_extra_path)
                    else:
                        extra_file_name = None

                    if TELETHON_OPTIONS.SERVER_SAVE_MESSAGE_VIDEO_FILE:
                        await aioshutil.copy2(src=temp_file_path,
                                              dst=arch_file_extra_path)
                        server_saved_mark = TELETHON_OPTIONS.SERVER_SAVED_FILE_ACTION_MARK
                        extra_saved_mark = f"{extra_saved_mark}{server_saved_mark}"

                    s3_bucket, s3_key, s3_endpoint, s3_uri = "", "", "", ""
                    if TELETHON_OPTIONS.S3_SAVE_MESSAGE_VIDEO_FILE:
                        async with AioBotoCoreManager() as s3_manager:
                            s3_client = await s3_manager.get_client()
                            s3_bucket_res = await check_create_s3_bucket(
                                s3_client=s3_client,
                                s3_bucket_name=S3_DEFAULT_BUCKET,
                                s3_region_name=S3_REGION_NAME)

                            if s3_bucket_res.valid_bucket:
                                async with aiofiles.open(
                                        file=temp_file_path, mode="rb") as f_obj:
                                    file_data = await f_obj.read()
                                    await s3_client.put_object(
                                        # ContentType='image/jpeg'
                                        Bucket=S3_DEFAULT_BUCKET,
                                        Key=extra_file_name,
                                        Body=file_data)

                                s3_bucket = S3_DEFAULT_BUCKET
                                s3_key = extra_file_name
                                s3_endpoint = (f"{S3_API_ENDPOINT}/"
                                               f"{S3_DEFAULT_BUCKET}/"
                                               f"{extra_file_name}")
                                s3_uri = (f"s3://{S3_DEFAULT_BUCKET}/"
                                          f"{extra_file_name}")

                                s3_saved_mark = TELETHON_OPTIONS.S3_SAVED_FILE_ACTION_MARK
                                extra_saved_mark = f"{extra_saved_mark}{s3_saved_mark}"

                    file_name_cst = os.path.basename(temp_file_path)
                    file_name_params = {"file_name_cst": file_name_cst,
                                        "extra_file_name_cst": extra_file_name}
                    tlt_sent_msg_spec_params.update(file_name_params)

                    s3_aws_params = {"s3_bucket": s3_bucket,
                                     "s3_key": s3_key,
                                     "s3_endpoint": s3_endpoint,
                                     "s3_uri": s3_uri}
                    tlt_sent_msg_spec_params.update(s3_aws_params)

                    if await aiofiles_os.path.exists(temp_file_path):
                        await aiofiles_os.remove(temp_file_path)
                    action_str = (f"{action_str}+{ACTION_STATUS.VIDEO_ATTACH_ACTION_STR}"
                                  f"{extra_saved_mark}")
            elif isinstance(cur_doc_attr_obj, DocumentAttributeAudio):
                ev_media_doc = tlt_sent_msg_obj_main_params["ev_media_document"]
                audio_params = await get_attrs_values_by_attr_chains(
                    base_class_or_obj=cur_doc_attr_obj,
                    attributes_chains_dict=get_doc_attr_audio_attr_chains(),
                    section_separator_prefix=separator)
                tlt_sent_msg_spec_params.update(audio_params)

                temp_file_path = ""
                arch_file_extra_path = ""
                extra_saved_mark = ""
                if (TELETHON_OPTIONS.SERVER_SAVE_MESSAGE_AUDIO_FILE
                        or TELETHON_OPTIONS.S3_SAVE_MESSAGE_AUDIO_FILE):
                    base_tlt_files_dir = TELETHON_OPTIONS.TEMP_TG_DOWNLOADED_FILES_DIR
                    temp_tlt_files_dir = get_full_dir_normal_path(
                        [BASE_DIR, base_tlt_files_dir])
                    await aiofiles_os.makedirs(temp_tlt_files_dir, exist_ok=True)
                    temp_file_path = await ev__client.download_media(
                        ev_media_doc, file=temp_tlt_files_dir)  # tg file name
                    # temp_file_path = await ev__client.download_media(ev_media_doc, file=bytes)  # To memory

                    base_arch_files_dir = TELETHON_OPTIONS.ARCHIVE_TLT_TG_FILES_DIR
                    arch_tlt_files_dir = get_full_dir_normal_path(
                        [BASE_DIR, base_arch_files_dir])
                    await aiofiles_os.makedirs(arch_tlt_files_dir,
                                               exist_ok=True)

                    temp_arch_file_name = os.path.basename(temp_file_path)
                    temp_arch_file_path = get_full_file_normal_path(
                        all_dir_str_parts=[arch_tlt_files_dir],
                        file_name_with_ext=temp_arch_file_name)

                    arch_file_extra_path = get_file_name_with_extra_part(
                        orig_file_full_path=temp_arch_file_path,
                        filename_prefix=archive_file_prefix)
                    extra_file_name = os.path.basename(arch_file_extra_path)
                else:
                    extra_file_name = None

                if TELETHON_OPTIONS.SERVER_SAVE_MESSAGE_AUDIO_FILE:
                    await aioshutil.copy2(src=temp_file_path,
                                          dst=arch_file_extra_path)
                    server_saved_mark = TELETHON_OPTIONS.SERVER_SAVED_FILE_ACTION_MARK
                    extra_saved_mark = f"{extra_saved_mark}{server_saved_mark}"

                s3_bucket, s3_key, s3_endpoint, s3_uri = "", "", "", ""
                if TELETHON_OPTIONS.S3_SAVE_MESSAGE_AUDIO_FILE:
                    async with AioBotoCoreManager() as s3_manager:
                        s3_client = await s3_manager.get_client()
                        s3_bucket_res = await check_create_s3_bucket(
                            s3_client=s3_client,
                            s3_bucket_name=S3_DEFAULT_BUCKET,
                            s3_region_name=S3_REGION_NAME)

                        if s3_bucket_res.valid_bucket:
                            async with aiofiles.open(
                                    file=temp_file_path, mode="rb") as f_obj:
                                file_data = await f_obj.read()
                                await s3_client.put_object(
                                    # ContentType='image/jpeg'
                                    Bucket=S3_DEFAULT_BUCKET,
                                    Key=extra_file_name,
                                    Body=file_data)

                            s3_bucket = S3_DEFAULT_BUCKET
                            s3_key = extra_file_name
                            s3_endpoint = (f"{S3_API_ENDPOINT}/"
                                           f"{S3_DEFAULT_BUCKET}/"
                                           f"{extra_file_name}")
                            s3_uri = (f"s3://{S3_DEFAULT_BUCKET}/"
                                      f"{extra_file_name}")

                            s3_saved_mark = TELETHON_OPTIONS.S3_SAVED_FILE_ACTION_MARK
                            extra_saved_mark = f"{extra_saved_mark}{s3_saved_mark}"

                file_name_cst = os.path.basename(temp_file_path)
                file_name_params = {"file_name_cst": file_name_cst,
                                    "extra_file_name_cst": extra_file_name}
                tlt_sent_msg_spec_params.update(file_name_params)

                s3_aws_params = {"s3_bucket": s3_bucket,
                                 "s3_key": s3_key,
                                 "s3_endpoint": s3_endpoint,
                                 "s3_uri": s3_uri}
                tlt_sent_msg_spec_params.update(s3_aws_params)

                if await aiofiles_os.path.exists(temp_file_path):
                    await aiofiles_os.remove(temp_file_path)
                action_str = (f"{action_str}+{ACTION_STATUS.VIDEO_ATTACH_ACTION_STR}"
                              f"{extra_saved_mark}")
            elif isinstance(cur_doc_attr_obj, DocumentAttributeFilename):
                ev_media_doc = tlt_sent_msg_obj_main_params["ev_media_document"]
                document_params = await get_attrs_values_by_attr_chains(
                    base_class_or_obj=cur_doc_attr_obj,
                    attributes_chains_dict=get_doc_attr_file_name_attr_chains(),
                    section_separator_prefix=separator)
                tlt_sent_msg_spec_params.update(document_params)

                temp_file_path = ""
                arch_file_extra_path = ""
                extra_saved_mark = ""
                if (TELETHON_OPTIONS.SERVER_SAVE_MESSAGE_DOC_FILE
                        or TELETHON_OPTIONS.S3_SAVE_MESSAGE_DOC_FILE):
                    base_tlt_files_dir = TELETHON_OPTIONS.TEMP_TG_DOWNLOADED_FILES_DIR
                    temp_tlt_files_dir = get_full_dir_normal_path(
                        [BASE_DIR, base_tlt_files_dir])
                    await aiofiles_os.makedirs(temp_tlt_files_dir, exist_ok=True)
                    temp_file_path = await ev__client.download_media(
                        ev_media_doc, file=temp_tlt_files_dir)  # tg file name
                    # temp_file_path = await ev__client.download_media(ev_media_doc, file=bytes)  # To memory

                    base_arch_files_dir = TELETHON_OPTIONS.ARCHIVE_TLT_TG_FILES_DIR
                    arch_tlt_files_dir = get_full_dir_normal_path(
                        [BASE_DIR, base_arch_files_dir])
                    await aiofiles_os.makedirs(arch_tlt_files_dir,
                                               exist_ok=True)

                    temp_arch_file_name = os.path.basename(temp_file_path)
                    temp_arch_file_path = get_full_file_normal_path(
                        all_dir_str_parts=[arch_tlt_files_dir],
                        file_name_with_ext=temp_arch_file_name)

                    arch_file_extra_path = get_file_name_with_extra_part(
                        orig_file_full_path=temp_arch_file_path,
                        filename_prefix=archive_file_prefix)
                    extra_file_name = os.path.basename(arch_file_extra_path)
                else:
                    extra_file_name = None

                if TELETHON_OPTIONS.SERVER_SAVE_MESSAGE_DOC_FILE:
                    await aioshutil.copy2(src=temp_file_path,
                                          dst=arch_file_extra_path)
                    server_saved_mark = TELETHON_OPTIONS.SERVER_SAVED_FILE_ACTION_MARK
                    extra_saved_mark = f"{extra_saved_mark}{server_saved_mark}"

                s3_bucket, s3_key, s3_endpoint, s3_uri = "", "", "", ""
                if TELETHON_OPTIONS.S3_SAVE_MESSAGE_DOC_FILE:
                    async with AioBotoCoreManager() as s3_manager:
                        s3_client = await s3_manager.get_client()
                        s3_bucket_res = await check_create_s3_bucket(
                            s3_client=s3_client,
                            s3_bucket_name=S3_DEFAULT_BUCKET,
                            s3_region_name=S3_REGION_NAME)

                        if s3_bucket_res.valid_bucket:
                            async with aiofiles.open(
                                    file=temp_file_path, mode="rb") as f_obj:
                                file_data = await f_obj.read()
                                await s3_client.put_object(
                                    # ContentType='image/jpeg'
                                    Bucket=S3_DEFAULT_BUCKET,
                                    Key=extra_file_name,
                                    Body=file_data)

                            s3_bucket = S3_DEFAULT_BUCKET
                            s3_key = extra_file_name
                            s3_endpoint = (f"{S3_API_ENDPOINT}/"
                                           f"{S3_DEFAULT_BUCKET}/"
                                           f"{extra_file_name}")
                            s3_uri = (f"s3://{S3_DEFAULT_BUCKET}/"
                                      f"{extra_file_name}")

                            s3_saved_mark = TELETHON_OPTIONS.S3_SAVED_FILE_ACTION_MARK
                            extra_saved_mark = f"{extra_saved_mark}{s3_saved_mark}"

                file_name_cst = os.path.basename(temp_file_path)
                file_name_params = {"file_name_cst": file_name_cst,
                                    "extra_file_name_cst": extra_file_name}
                tlt_sent_msg_spec_params.update(file_name_params)

                s3_aws_params = {"s3_bucket": s3_bucket,
                                 "s3_key": s3_key,
                                 "s3_endpoint": s3_endpoint,
                                 "s3_uri": s3_uri}
                tlt_sent_msg_spec_params.update(s3_aws_params)

                if await aiofiles_os.path.exists(temp_file_path):
                    await aiofiles_os.remove(temp_file_path)
                action_str = (f"{action_str}+{ACTION_STATUS.VIDEO_ATTACH_ACTION_STR}"
                              f"{extra_saved_mark}")

    tlt_sent_msg_spec_params.update({
        "action": action_str,
        "tlt_config_name": telethon_config.name,
        "telethon_config_name": telethon_config.telethon_config_name})

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
