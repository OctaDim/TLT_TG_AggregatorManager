from telethon import events, TelegramClient

from configs.settings import TELETHON_OPTIONS
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
from utils_specific.handle_all_event_params import (
    send_all_event_params)


async def message_edited_handler_helper(
        event: events.MessageEdited.Event,
        telethon_client: TelegramClient,
        telethon_config: TelethonConfig,
        event_type: str = None
) -> None:
    separator = TELETHON_OPTIONS.EVENT_ATTRS_SECTION_SEPARATOR_PREFIX
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

            emoji_emoticon = cur_react_res_dict["ev_reaction_result_reaction_emoticon"]
            emoji_doc_id = cur_react_res_dict["ev_reaction_result_reaction_document_id"]
            emoji_count = cur_react_res_dict["ev_reaction_result_reaction_count"]
            emoji_chosen_order = cur_react_res_dict["ev_reaction_result_reaction_chosen_order"]

            if emoji_emoticon:
                emoji_key = emoji_emoticon
                emoji_emoticons_list.append(emoji_emoticon)
            else:
                emoji_key = emoji_doc_id
                emoji_doc_id_list.append(emoji_doc_id)

            ev_reactions_custom[emoji_key] = {
                "emoji_emoticon": emoji_emoticon,
                "emoji_doc_id": emoji_doc_id,
                "emoji_count": emoji_count,
                "emoji_chosen_order": emoji_chosen_order, }

        handler_specific_params.update({
            "reactions_total_custom": ev_reactions_custom,
            "reactions_total_count_custom": len(ev_reactions_results),
            "reactions_emoticon_custom": emoji_emoticons_list,
            "reactions_emoticon_count_custom": len(emoji_emoticons_list),
            "reactions_doc_id_custom": emoji_doc_id_list,
            "reactions_doc_id_count_custom": len(emoji_doc_id_list), })
    else:
        handler_specific_params.update({
            "reactions_total_custom": None,
            "reactions_total_count_custom": None,
            "reactions_emoticon_custom": None,
            "reactions_emoticon_count_custom": None,
            "reactions_doc_id_custom": None,
            "reactions_doc_id_count_custom": None})

    # Separate function because handler function with its own params values
    # is enclosed by add_all_telethon_client_handlers()
    await send_all_event_params(
        event=event,
        telethon_client=telethon_client,
        telethon_config=telethon_config,
        event_type=event_type,
        handler_additional_params=handler_specific_params)
