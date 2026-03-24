import os

from telethon import events, TelegramClient
from telethon.tl.types import (
    DocumentAttributeAudio, DocumentAttributeVideo,
    DocumentAttributeFilename, MessageMediaPhoto)

from configs.labels_messages import ACTION_STATUS
from configs.settings import BASE_DIR
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
from telethon_manager.telethon_attrs_chains.chain_reaction_result import (
    get_reaction_result_attr_chains)
from telethon_manager.telethon_client_config import TelethonConfig
from utils_common.clean_str_new_lines_spaces import group_clean_text
from utils_common.get_obj_attrs_vals_by_attr_chain import (
    get_attrs_values_by_attr_chains)
from utils_common.normalized_path import get_full_dir_normal_path
from utils_specific.handle_all_event_params import (
    send_all_event_params)


async def message_edited_handler_helper(
        event: events.MessageEdited.Event,
        telethon_client: TelegramClient,
        telethon_config: TelethonConfig,
        event_type: str = None
) -> None:
    if not TELETHON_OPTIONS.HANDLE_MESSAGE_EDITED_EVENT:
        log_txt = (f"\nDEBUG: WEBHOOK SKIPPED [ERROR]:\n"
                   f"event_type: {event_type}\n")
        print(log_txt)
        return

    separator = TELETHON_OPTIONS.EVENT_ATTRS_SECTION_SEPARATOR_PREFIX
    action_str = ACTION_STATUS.EDIT_MSG_ACTION_STR
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
        if ev_media_photo and TELETHON_OPTIONS.DOWNLOAD_PHOTO_FILE_NAME:
            base_tlt_files_dir = TELETHON_OPTIONS.TEMP_TG_DOWNLOADED_FILES_DIR
            temp_tlt_files_dir = get_full_dir_normal_path(
                [BASE_DIR, base_tlt_files_dir])
            os.makedirs(temp_tlt_files_dir, exist_ok=True)
            temp_file_path = await ev__client.download_media(
                ev_media_photo, file=temp_tlt_files_dir)  # tg file name
            # temp_file_path = await ev__client.download_media(ev_media_photo, file=bytes)
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            file_name_cst = os.path.basename(temp_file_path)
            handler_specific_params.update({"file_name_cst": file_name_cst})
            action_str = f"{action_str}+{ACTION_STATUS.PHOTO_ATTACH_ACTION_STR}"
    elif ev_media_doc_attrs:
        for cur_doc_attr_obj in ev_media_doc_attrs:
            if isinstance(cur_doc_attr_obj, DocumentAttributeVideo):
                video_params = await get_attrs_values_by_attr_chains(
                    base_class_or_obj=cur_doc_attr_obj,
                    attributes_chains_dict=get_doc_attr_video_attr_chains(),
                    section_separator_prefix=separator)
                ev_media_doc = event_main_params["ev_media_document"]
                if (not video_params["doc_attr_file_name"] and ev_media_doc
                        and TELETHON_OPTIONS.DOWNLOAD_VIDEO_FILE_NAME):
                    base_tlt_files_dir = TELETHON_OPTIONS.TEMP_TG_DOWNLOADED_FILES_DIR
                    temp_tlt_files_dir = get_full_dir_normal_path(
                        [BASE_DIR, base_tlt_files_dir])
                    os.makedirs(temp_tlt_files_dir, exist_ok=True)
                    temp_file_path = await ev__client.download_media(
                        ev_media_doc, file=temp_tlt_files_dir)  # tg file name
                    # temp_file_path = await ev__client.download_media(ev_media_doc, file=bytes)
                    if os.path.exists(temp_file_path):
                        os.remove(temp_file_path)
                    file_name_cst = os.path.basename(temp_file_path)
                    video_params.update({"file_name_cst": file_name_cst})
                handler_specific_params.update(video_params)
                action_str = f"{action_str}+{ACTION_STATUS.VIDEO_ATTACH_ACTION_STR}"
            elif isinstance(cur_doc_attr_obj, DocumentAttributeAudio):
                audio_params = await get_attrs_values_by_attr_chains(
                    base_class_or_obj=cur_doc_attr_obj,
                    attributes_chains_dict=get_doc_attr_audio_attr_chains(),
                    section_separator_prefix=separator)
                file_name_cst = audio_params["doc_attr_file_name"]
                audio_params.update({"file_name_cst": file_name_cst})
                handler_specific_params.update(audio_params)
                action_str = f"{action_str}+{ACTION_STATUS.AUDIO_ATTACH_ACTION_STR}"
            elif isinstance(cur_doc_attr_obj, DocumentAttributeFilename):
                document_params = await get_attrs_values_by_attr_chains(
                    base_class_or_obj=cur_doc_attr_obj,
                    attributes_chains_dict=get_doc_attr_file_name_attr_chains(),
                    section_separator_prefix=separator)
                file_name_cst = document_params["doc_attr_file_name"]
                document_params.update({"file_name_cst": file_name_cst})
                handler_specific_params.update(document_params)
                action_str = f"{action_str}+{ACTION_STATUS.DOC_ATTACH_ACTION_STR}"

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

    handler_specific_params.update({"action": action_str})

    # Separate function because handler function with its own params values
    # is enclosed by add_all_telethon_client_handlers()
    await send_all_event_params(
        event=event,
        telethon_client=telethon_client,
        telethon_config=telethon_config,
        event_type=event_type,
        handler_additional_params=handler_specific_params)
