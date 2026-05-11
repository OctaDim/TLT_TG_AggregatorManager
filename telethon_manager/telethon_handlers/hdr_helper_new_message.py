import os

import aioshutil
from aiofiles import os as aiofiles_os
from telethon import events, TelegramClient
from telethon.tl.types import (
    DocumentAttributeAudio, DocumentAttributeFilename,
    DocumentAttributeVideo, MessageMediaPhoto)

from configs.environments import BASE_DIR
from configs.labels_messages import ACTION_STATUS
from configs.options import TELETHON_OPTIONS
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
from telethon_manager.telethon_client_config import TelethonConfig
from utils_common.clean_str_new_lines_spaces import group_clean_text
from utils_common.get_file_name_extra_part import (
    get_file_name_with_extra_part)
from utils_common.get_obj_attrs_vals_by_attr_chain import (
    get_attrs_values_by_attr_chains)
from utils_common.normalized_path import (
    get_full_dir_normal_path, get_full_file_normal_path)
from utils_specific.handle_all_event_params import (
    send_all_event_params)


async def new_message_handler_helper(
        event: events.NewMessage.Event,
        telethon_client: TelegramClient,
        telethon_config: TelethonConfig,
        event_type: str = None
) -> None:
    if not TELETHON_OPTIONS.HANDLE_NEW_MESSAGE_EVENT:
        if TELETHON_OPTIONS.LOG_SKIPPED_EVENT_HANDLING_ERROR:
            log_txt = (f"\nDEBUG: WEBHOOK SKIPPED [ERROR]:\n"
                       f"event_type: {event_type}\n")
            print(log_txt)
        return

    separator = TELETHON_OPTIONS.EVENT_ATTRS_SECTION_SEPARATOR_PREFIX
    action_str = ACTION_STATUS.NEW_MSG_ACTION_STR
    archive_file_prefix = TELETHON_OPTIONS.DOWNLOADED_ARCHIVE_FILES_PREFIX
    handler_specific_params = {}

    # Getting event text params
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

    # Getting handler specific params
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

            if TELETHON_OPTIONS.SERVER_SAVE_MESSAGE_PHOTO_FILE:
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
                await aioshutil.copy2(src=temp_file_path,
                                      dst=arch_file_extra_path)
                extra_file_name = os.path.basename(arch_file_extra_path)
                extra_saved_mark = TELETHON_OPTIONS.SERVER_SAVED_FILE_ACTION_MARK
            else:
                extra_file_name = None
                extra_saved_mark = ""

            if await aiofiles_os.path.exists(temp_file_path):
                await aiofiles_os.remove(temp_file_path)
            file_name_cst = os.path.basename(temp_file_path)
            file_name_params = {"file_name_cst": file_name_cst,
                                "extra_file_name_cst": extra_file_name}
            handler_specific_params.update(file_name_params)
            action_str = (f"{action_str}+"
                          f"{ACTION_STATUS.PHOTO_ATTACH_ACTION_STR}"
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
                    action_str = (
                        f"{action_str}+{ACTION_STATUS.VIDEO_ATTACH_ACTION_STR}")
                elif ev_media_doc and TELETHON_OPTIONS.DOWNLOAD_VIDEO_TO_GET_FILE_NAME:
                    base_tlt_files_dir = TELETHON_OPTIONS.TEMP_TG_DOWNLOADED_FILES_DIR
                    temp_tlt_files_dir = get_full_dir_normal_path(
                        [BASE_DIR, base_tlt_files_dir])
                    await aiofiles_os.makedirs(temp_tlt_files_dir, exist_ok=True)
                    temp_file_path = await ev__client.download_media(
                        ev_media_doc, file=temp_tlt_files_dir)  # tg file name
                    # temp_file_path = await ev__client.download_media(ev_media_doc, file=bytes)  # To memory

                    if TELETHON_OPTIONS.SERVER_SAVE_MESSAGE_VIDEO_FILE:
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
                        await aioshutil.copy2(src=temp_file_path,
                                              dst=arch_file_extra_path)
                        extra_file_name = os.path.basename(arch_file_extra_path)
                        extra_saved_mark = TELETHON_OPTIONS.SERVER_SAVED_FILE_ACTION_MARK
                    else:
                        extra_file_name = None
                        extra_saved_mark = ""

                    if await aiofiles_os.path.exists(temp_file_path):
                        await aiofiles_os.remove(temp_file_path)
                    file_name_cst = os.path.basename(temp_file_path)
                    file_name_params = {"file_name_cst": file_name_cst,
                                        "extra_file_name_cst": extra_file_name}
                    handler_specific_params.update(file_name_params)
                    action_str = (f"{action_str}+"
                                  f"{ACTION_STATUS.VIDEO_ATTACH_ACTION_STR}"
                                  f"{extra_saved_mark}")
            elif isinstance(cur_doc_attr_obj, DocumentAttributeAudio):
                ev_media_doc = event_main_params["ev_media_document"]
                audio_params = await get_attrs_values_by_attr_chains(
                    base_class_or_obj=cur_doc_attr_obj,
                    attributes_chains_dict=get_doc_attr_audio_attr_chains(),
                    section_separator_prefix=separator)
                handler_specific_params.update(audio_params)

                if TELETHON_OPTIONS.SERVER_SAVE_MESSAGE_AUDIO_FILE:
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
                    await aioshutil.copy2(src=temp_file_path,
                                          dst=arch_file_extra_path)

                    if await aiofiles_os.path.exists(temp_file_path):
                        await aiofiles_os.remove(temp_file_path)

                    extra_file_name = os.path.basename(arch_file_extra_path)
                    extra_saved_mark = TELETHON_OPTIONS.SERVER_SAVED_FILE_ACTION_MARK
                else:
                    extra_file_name = None
                    extra_saved_mark = ""

                file_name_cst = audio_params["doc_attr_file_name"]
                file_name_params = {"file_name_cst": file_name_cst,
                                    "extra_file_name_cst": extra_file_name}
                handler_specific_params.update(file_name_params)
                action_str = (f"{action_str}+"
                              f"{ACTION_STATUS.AUDIO_ATTACH_ACTION_STR}"
                              f"{extra_saved_mark}")
            elif isinstance(cur_doc_attr_obj, DocumentAttributeFilename):
                ev_media_doc = event_main_params["ev_media_document"]
                document_params = await get_attrs_values_by_attr_chains(
                    base_class_or_obj=cur_doc_attr_obj,
                    attributes_chains_dict=get_doc_attr_file_name_attr_chains(),
                    section_separator_prefix=separator)
                handler_specific_params.update(document_params)

                if TELETHON_OPTIONS.SERVER_SAVE_MESSAGE_DOC_FILE:
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
                    await aioshutil.copy2(src=temp_file_path,
                                          dst=arch_file_extra_path)

                    if await aiofiles_os.path.exists(temp_file_path):
                        await aiofiles_os.remove(temp_file_path)

                    extra_file_name = os.path.basename(arch_file_extra_path)
                    extra_saved_mark = TELETHON_OPTIONS.SERVER_SAVED_FILE_ACTION_MARK
                else:
                    extra_file_name = None
                    extra_saved_mark = ""

                file_name_cst = document_params["doc_attr_file_name"]
                file_name_params = {"file_name_cst": file_name_cst,
                                    "extra_file_name_cst": extra_file_name}
                handler_specific_params.update(file_name_params)
                action_str = (f"{action_str}+{ACTION_STATUS.DOC_ATTACH_ACTION_STR}"
                              f"{extra_saved_mark}")

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
