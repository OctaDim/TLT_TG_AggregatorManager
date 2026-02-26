from telethon import events, TelegramClient

from configs.aggregator_api_urls import AGGREGATOR_API_WEBHOOKS_URL
from configs.settings import TELETHON_OPTIONS, AGGREGATOR_API_OPTIONS
from telethon_manager.telethon_attrs_chains.chain_message_text import (
    get_message_text_attr_chains)
from telethon_manager.telethon_attrs_chains.chain_new_edit_message import (
    get_event_new_edit_msg_attr_chains)
from telethon_manager.telethon_attrs_chains.chain_reaction_result import (
    get_reaction_result_attr_chains)
from telethon_manager.telethon_client_config import TelethonConfig
from utils_common.clean_str_new_lines_spaces import group_clean_text
from utils_common.get_obj_attrs_vals_by_attr_chain import (
    get_attrs_values_by_attr_chains)
from utils_common.serialize_custom_json import get_only_jsonable_values
from utils_specific.event_params_detailed_log import (
    log_all_event_params)
from utils_specific.send_event_data_webhook import (
    send_event_data_webhook_req)


async def message_edited_handler_helper(
        event: events.MessageEdited.Event,
        telethon_client: TelegramClient,
        telethon_config: TelethonConfig,
        event_type: str = None
) -> None:
    if None in (telethon_client, telethon_config):
        print(f"Deleted Telethon object(s), not handled event [ERROR]:\n"
              f"telethon_client: {telethon_client}\n"
              f"telethon_config: {telethon_config}\n")
        return

    if TELETHON_OPTIONS.LOG_ALL_EVENT_STRINGIFY_PARAMS:
        print(event.stringify())

    separator = TELETHON_OPTIONS.EVENT_ATTRS_SECTION_SEPARATOR_PREFIX

    if telethon_config.bot_token:
        tlt_bot_token_info = telethon_config.bot_token[:10]
    else:
        tlt_bot_token_info = None

    all_event_params = {
        "event_type": event_type,
        "web_account_id": telethon_config.web_account_id,
        "web_account_username": telethon_config.web_account_username,
        "tlt_account_type": telethon_config.account_type.value,
        "tlt_phone": telethon_config.phone,
        "tlt_bot_token": tlt_bot_token_info,
        separator: ""}

    # Getting event texts
    event_texts_params = await get_attrs_values_by_attr_chains(
        base_class_or_obj=event,
        attributes_chains_dict=get_message_text_attr_chains(),
        section_separator_prefix=separator)
    cleaned_texts_params = await group_clean_text(
        origin_texts=event_texts_params,
        strip_spaces=True,
        clean_line_breaks=True,
        clean_continuous_spaces=True)
    all_event_params.update(cleaned_texts_params)

    event_main_params = await get_attrs_values_by_attr_chains(
        base_class_or_obj=event,
        attributes_chains_dict=get_event_new_edit_msg_attr_chains(),
        section_separator_prefix=separator)
    all_event_params.update(event_main_params)

    # Getting event reactions list data and creating custom reactions dict
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

        all_event_params.update({
            "reactions_total_custom": ev_reactions_custom,
            "reactions_total_count_custom": len(ev_reactions_results),
            "reactions_emoticon_custom": emoji_emoticons_list,
            "reactions_emoticon_count_custom": len(emoji_emoticons_list),
            "reactions_doc_id_custom": emoji_doc_id_list,
            "reactions_doc_id_count_custom": len(emoji_doc_id_list), })
    else:
        all_event_params.update({
            "reactions_total_custom": None,
            "reactions_total_count_custom": None,
            "reactions_emoticon_custom": None,
            "reactions_emoticon_count_custom": None,
            "reactions_doc_id_custom": None,
            "reactions_doc_id_count_custom": None})

    if TELETHON_OPTIONS.LOG_ALL_BEFORE_JSON_EVENT_PARAMS:
        await log_all_event_params(
            log_title=f"EVENT: {event_type} [PRELIMINARY]",
            event_params_dict=all_event_params)

    jsonable_event_params = await get_only_jsonable_values(
        all_values=all_event_params,
        separator=TELETHON_OPTIONS.EVENT_ATTRS_SECTION_SEPARATOR_PREFIX)

    if TELETHON_OPTIONS.LOG_ALL_AFTER_JSON_EVENT_PARAMS:
        await log_all_event_params(
            log_title=f"EVENT: {event_type} [JSONABLE]",
            event_params_dict=jsonable_event_params)

    await send_event_data_webhook_req(
        new_event_data=jsonable_event_params,
        source=AGGREGATOR_API_OPTIONS.SOURCE_STRING_FOR_EXT_AGGREGATOR,
        operation=event_type,
        aggregator_url=AGGREGATOR_API_WEBHOOKS_URL)
