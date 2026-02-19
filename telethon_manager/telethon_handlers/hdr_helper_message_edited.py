from telethon import events, TelegramClient

from configs.settings import TELETHON_OPTIONS
from telethon_manager.telethon_attrs_chains.chain_new_edit_message import (
    get_event_new_edit_msg_attr_chains)
from telethon_manager.telethon_client_config import TelethonConfig
from utils_common.clean_str_new_lines_spaces import clean_text
from utils_common.get_obj_attrs_vals_by_attr_chain import (
    get_attrs_values_by_attr_chains, get_attr_value_by_attr_chain)


async def message_edited_handler_helper(
        event: events.MessageEdited.Event,
        telethon_client: TelegramClient,
        telethon_config: TelethonConfig
) -> None:
    if None in (telethon_client, telethon_config):
        print(f"Deleted Telethon object(s), not handled event [ERROR]:\n"
              f"telethon_client: {telethon_client}\n"
              f"telethon_config: {telethon_config}\n")
        return

    if TELETHON_OPTIONS.LOG_EVENT_STRINGIFY:
        print(event.stringify())

    if telethon_config.bot_token:
        tlt_bot_token_info = telethon_config.bot_token[:10]
    else:
        tlt_bot_token_info = None

    attrs_chains = get_event_new_edit_msg_attr_chains()  # MessageEdited attrs chains
    event_params = {
        "event_type": "MessageEdited",
        "web_account_id": telethon_config.web_account_id,
        "web_account_username": telethon_config.web_account_username,
        "tlt_account_type": telethon_config.account_type.value,
        "tlt_phone": telethon_config.phone,
        "tlt_bot_token": tlt_bot_token_info,
        "separator": "", }

    evnt_msg_msg = await get_attr_value_by_attr_chain(
        base_class_or_obj=event,
        attribute_chain="message.message")
    evnt_msg_msg = await clean_text(
        origin_text=evnt_msg_msg,
        clean_line_breaks=True,
        clean_continuous_spaces=True)
    event_params["event_message_message"] = evnt_msg_msg

    evnt_msg_text = await get_attr_value_by_attr_chain(
        base_class_or_obj=event,
        attribute_chain="message.text")
    evnt_msg_text = await clean_text(
        origin_text=evnt_msg_text,
        clean_line_breaks=True,
        clean_continuous_spaces=True)
    event_params["event_message_text"] = evnt_msg_text

    evnt_msg_raw_text = await get_attr_value_by_attr_chain(
        base_class_or_obj=event,
        attribute_chain="message.raw_text")
    evnt_msg_raw_text = await clean_text(origin_text=evnt_msg_raw_text,
                                         clean_line_breaks=True,
                                         clean_continuous_spaces=True)
    event_params["event_message_raw_text"] = evnt_msg_raw_text

    new_msg_evnt_data = await get_attrs_values_by_attr_chains(
        base_class_or_obj=event,
        attributes_chains_dict=attrs_chains,
        section_separator_prefix="separator")
    event_params.update(new_msg_evnt_data)

    print(f"\nEDITED MESSAGE EVENT:\n{'=' * 80}")
    for cur_param_str, cur_param_val in event_params.items():
        if cur_param_str.startswith("separator"):
            print(f"\t")
            continue
        if cur_param_val is None:
            print(f"\t{cur_param_str} ==")
        else:
            print(f"\t{cur_param_str} == {cur_param_val} ({type(cur_param_val)})")
    print(f"{'=' * 80}\n{'=' * 80}\n")
