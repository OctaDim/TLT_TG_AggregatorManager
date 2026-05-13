import os

import aiofiles
import aioshutil
from aiofiles import os as aiofiles_os

from telethon import events, TelegramClient
from telethon.tl.types import (
    DocumentAttributeAudio, DocumentAttributeVideo,
    DocumentAttributeFilename, MessageMediaPhoto)

from configs.labels_messages import ACTION_STATUS
from configs.environments import BASE_DIR, S3_DEFAULT_BUCKET, S3_API_ENDPOINT, S3_REGION_NAME
from configs.options import TELETHON_OPTIONS
from s3_async_managers.s3_aiobotocore_manager import AioBotoCoreManager
from telethon_manager.telethon_attrs_chains.chain_doc_attr_audio import (
    get_doc_attr_audio_attr_chains)
from telethon_manager.telethon_attrs_chains.chain_doc_attr_file_name import (
    get_doc_attr_file_name_attr_chains)
from telethon_manager.telethon_attrs_chains.chain_doc_attr_video import (
    get_doc_attr_video_attr_chains)
from telethon_manager.telethon_attrs_chains.chain_message_new_edit import (
    get_event_new_edit_msg_attr_chains)
from telethon_manager.telethon_attrs_chains.chain_message_text import (
    get_message_text_attr_chains)
from telethon_manager.telethon_attrs_chains.chain_reaction_result import (
    get_reaction_result_attr_chains)
from telethon_manager.telethon_client_config import TelethonConfig
from utils_common.check_create_s3_bucket import check_create_s3_bucket
from utils_common.clean_str_new_lines_spaces import group_clean_text
from utils_common.get_file_name_extra_part import (
    get_file_name_with_extra_part)
from utils_common.get_obj_attrs_vals_by_attr_chain import (
    get_attrs_values_by_attr_chains)
from utils_common.normalized_path import (
    get_full_dir_normal_path, get_full_file_normal_path)
from utils_specific.handle_all_event_params import (
    send_all_event_params)


async def message_edited_handler_helper(
        event: events.MessageEdited.Event,
        telethon_client: TelegramClient,
        telethon_config: TelethonConfig,
        event_type: str = None
) -> None:
    if not TELETHON_OPTIONS.HANDLE_MESSAGE_EDITED_EVENT:
        if TELETHON_OPTIONS.LOG_SKIPPED_EVENT_HANDLING_ERROR:
            log_txt = (f"\nDEBUG: WEBHOOK SKIPPED [ERROR]:\n"
                       f"event_type: {event_type}\n")
            print(log_txt)
        return

    separator = TELETHON_OPTIONS.EVENT_ATTRS_SECTION_SEPARATOR_PREFIX
    action_str = ACTION_STATUS.EDIT_MSG_ACTION_STR
    archive_file_prefix = TELETHON_OPTIONS.DOWNLOADED_ARCHIVE_FILES_PREFIX
    handler_specific_params = {}

    # Getting edited message event text params
    event_texts_params = await get_attrs_values_by_attr_chains(
        base_class_or_obj=event,
        attributes_chains_dict=get_message_text_attr_chains(),
        section_separator_prefix=separator)
    cleaned_texts_params = await group_clean_text(
        origin_texts=event_texts_params,
        strip_spaces=True,
        clean_line_breaks=True,
        clean_continuous_spaces=True)
    handler_specific_params.update(cleaned_texts_params)

    # Getting edited message event handler specific params
    event_main_params = await get_attrs_values_by_attr_chains(
        base_class_or_obj=event,
        attributes_chains_dict=get_event_new_edit_msg_attr_chains(),
        section_separator_prefix=separator)
    handler_specific_params.update(event_main_params)

    ev__client = event_main_params["ev__client"]
    ev_media = event_main_params["ev_media"]
    ev_media_doc_attrs = event_main_params["ev_media_document_attributes"]

    if isinstance(ev_media, MessageMediaPhoto):
        ev_media_photo = event_main_params["ev_media_photo"]
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
            handler_specific_params.update(file_name_params)

            s3_aws_params = {"s3_bucket": s3_bucket,
                             "s3_key": s3_key,
                             "s3_endpoint": s3_endpoint,
                             "s3_uri": s3_uri}
            handler_specific_params.update(s3_aws_params)

            if await aiofiles_os.path.exists(temp_file_path):
                await aiofiles_os.remove(temp_file_path)
            action_str = (f"{action_str}+{ACTION_STATUS.PHOTO_ATTACH_ACTION_STR}"
                          f"{extra_saved_mark}")
    elif ev_media_doc_attrs:
        for cur_doc_attr_obj in ev_media_doc_attrs:
            if isinstance(cur_doc_attr_obj, DocumentAttributeVideo):
                ev_media_doc = event_main_params["ev_media_document"]
                video_params = await get_attrs_values_by_attr_chains(
                    base_class_or_obj=cur_doc_attr_obj,
                    attributes_chains_dict=get_doc_attr_video_attr_chains(),
                    section_separator_prefix=separator)
                handler_specific_params.update(video_params)

                if (video_params["doc_attr_file_name"]
                        and not TELETHON_OPTIONS.SERVER_SAVE_MESSAGE_VIDEO_FILE):
                    file_name_cst = video_params["doc_attr_file_name"]
                    extra_file_name = None
                    file_name_params = {"file_name_cst": file_name_cst,
                                        "extra_file_name_cst": extra_file_name}
                    handler_specific_params.update(file_name_params)
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
                    handler_specific_params.update(file_name_params)

                    s3_aws_params = {"s3_bucket": s3_bucket,
                                     "s3_key": s3_key,
                                     "s3_endpoint": s3_endpoint,
                                     "s3_uri": s3_uri}
                    handler_specific_params.update(s3_aws_params)

                    if await aiofiles_os.path.exists(temp_file_path):
                        await aiofiles_os.remove(temp_file_path)
                    action_str = (f"{action_str}+{ACTION_STATUS.VIDEO_ATTACH_ACTION_STR}"
                                  f"{extra_saved_mark}")
            elif isinstance(cur_doc_attr_obj, DocumentAttributeAudio):
                ev_media_doc = event_main_params["ev_media_document"]
                audio_params = await get_attrs_values_by_attr_chains(
                    base_class_or_obj=cur_doc_attr_obj,
                    attributes_chains_dict=get_doc_attr_audio_attr_chains(),
                    section_separator_prefix=separator)
                handler_specific_params.update(audio_params)

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
                handler_specific_params.update(file_name_params)

                s3_aws_params = {"s3_bucket": s3_bucket,
                                 "s3_key": s3_key,
                                 "s3_endpoint": s3_endpoint,
                                 "s3_uri": s3_uri}
                handler_specific_params.update(s3_aws_params)

                if await aiofiles_os.path.exists(temp_file_path):
                    await aiofiles_os.remove(temp_file_path)
                action_str = (f"{action_str}+{ACTION_STATUS.VIDEO_ATTACH_ACTION_STR}"
                              f"{extra_saved_mark}")
            elif isinstance(cur_doc_attr_obj, DocumentAttributeFilename):
                ev_media_doc = event_main_params["ev_media_document"]
                document_params = await get_attrs_values_by_attr_chains(
                    base_class_or_obj=cur_doc_attr_obj,
                    attributes_chains_dict=get_doc_attr_file_name_attr_chains(),
                    section_separator_prefix=separator)
                handler_specific_params.update(document_params)

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
                handler_specific_params.update(file_name_params)

                s3_aws_params = {"s3_bucket": s3_bucket,
                                 "s3_key": s3_key,
                                 "s3_endpoint": s3_endpoint,
                                 "s3_uri": s3_uri}
                handler_specific_params.update(s3_aws_params)

                if await aiofiles_os.path.exists(temp_file_path):
                    await aiofiles_os.remove(temp_file_path)
                action_str = (f"{action_str}+{ACTION_STATUS.VIDEO_ATTACH_ACTION_STR}"
                              f"{extra_saved_mark}")

    # Getting edited message event reactions params
    ev_reactions_results = event_main_params["ev_reactions_results"]
    if ev_reactions_results:
        ev_reactions_custom = {}
        emoji_emoticons_list, emoji_doc_id_list = [], []

        for cur_react_res_obj in ev_reactions_results:
            cur_react_res_dict = await get_attrs_values_by_attr_chains(
                base_class_or_obj=cur_react_res_obj,
                attributes_chains_dict=get_reaction_result_attr_chains(),
                section_separator_prefix=separator)

            emj_emoticon = cur_react_res_dict["ev_reaction_result_reaction_emoticon"]
            emj_doc_id = cur_react_res_dict["ev_reaction_result_reaction_document_id"]
            emj_count = cur_react_res_dict["ev_reaction_result_reaction_count"]
            emj_chosen_order = cur_react_res_dict["ev_reaction_result_reaction_chosen_order"]

            if emj_emoticon:
                emoji_key = emj_emoticon
                emoji_emoticons_list.append(emj_emoticon)
            else:
                emoji_key = emj_doc_id
                emoji_doc_id_list.append(emj_doc_id)

            ev_reactions_custom[emoji_key] = {
                "emoji_emoticon": emj_emoticon,
                "emoji_doc_id": emj_doc_id,
                "emoji_count": emj_count,
                "emoji_chosen_order": emj_chosen_order, }

        handler_specific_params.update({
            "reactions_total_cst": ev_reactions_custom,
            "reactions_total_count_cst": len(ev_reactions_results),
            "reactions_emoticon_cst": emoji_emoticons_list,
            "reactions_emoticon_count_cst": len(emoji_emoticons_list),
            "reactions_doc_id_cst": emoji_doc_id_list,
            "reactions_doc_id_count_cst": len(emoji_doc_id_list), })
        action_str = f"{action_str}+{ACTION_STATUS.EMOJI_ATTACH_ACTION_STR}"

    handler_specific_params.update({
        "action": action_str,
        # "telethon_config_name": telethon_config.telethon_config_name,
        "tlt_config_name": telethon_config.name})

    # Separate function because handler function with its own params values
    # is enclosed by add_all_telethon_client_handlers()
    await send_all_event_params(
        event=event,
        telethon_client=telethon_client,
        telethon_config=telethon_config,
        event_type=event_type,
        handler_additional_params=handler_specific_params)
