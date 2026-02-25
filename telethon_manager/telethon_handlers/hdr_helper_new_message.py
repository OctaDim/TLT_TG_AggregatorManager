from telethon import events, TelegramClient

from configs.aggregator_api_urls import AGGREGATOR_API_WEBHOOKS_URL
from configs.settings import TELETHON_OPTIONS
from telethon_manager.telethon_attrs_chains.chain_new_edit_message import (
    get_event_new_edit_msg_attr_chains)
from telethon_manager.telethon_client_config import TelethonConfig
from utils_common.clean_str_new_lines_spaces import clean_text
from utils_common.get_obj_attrs_vals_by_attr_chain import (
    get_attr_value_by_attr_chain, get_attrs_values_by_attr_chains)
from utils_common.serialize_custom_json import get_jsonable_value
from utils_specific.event_params_detailed_log import log_all_event_params
from utils_specific.send_event_data_webhook import (
    send_event_data_webhook_req)


async def new_message_handler_helper(
        event: events.NewMessage.Event,
        telethon_client: TelegramClient,
        telethon_config: TelethonConfig
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

    attrs_chains = get_event_new_edit_msg_attr_chains()  # NewMessage attrs chains
    all_event_params = {
        "event_type": "NewMessage",
        "web_account_id": telethon_config.web_account_id,
        "web_account_username": telethon_config.web_account_username,
        "tlt_account_type": telethon_config.account_type.value,
        "tlt_phone": telethon_config.phone,
        "tlt_bot_token": tlt_bot_token_info,
        separator: ""}

    evnt_msg_msg = await get_attr_value_by_attr_chain(
        base_class_or_obj=event,
        attribute_chain="message.message")
    evnt_msg_msg = await clean_text(
        origin_text=evnt_msg_msg,
        clean_line_breaks=True,
        clean_continuous_spaces=True)

    evnt_msg_text = await get_attr_value_by_attr_chain(
        base_class_or_obj=event,
        attribute_chain="message.text")
    evnt_msg_text = await clean_text(
        origin_text=evnt_msg_text,
        clean_line_breaks=True,
        clean_continuous_spaces=True)

    evnt_msg_raw_text = await get_attr_value_by_attr_chain(
        base_class_or_obj=event,
        attribute_chain="message.raw_text")
    evnt_msg_raw_text = await clean_text(origin_text=evnt_msg_raw_text,
                                         clean_line_breaks=True,
                                         clean_continuous_spaces=True)

    event_messages = {"ev_message_message": evnt_msg_msg,
                      "ev_message_text": evnt_msg_text,
                      "ev_message_raw_text": evnt_msg_raw_text,
                      f"{separator}_msgs": ""}
    all_event_params.update(event_messages)

    new_msg_evnt_data = await get_attrs_values_by_attr_chains(
        base_class_or_obj=event,
        attributes_chains_dict=attrs_chains,
        section_separator_prefix=separator)
    all_event_params.update(new_msg_evnt_data)

    if TELETHON_OPTIONS.LOG_NEW_MESSAGE_EVENT_PARAMS:
        await log_all_event_params(log_title="NEW MESSAGE EVENT",
                                   event_params_dict=all_event_params)

    webhook_event_data = {}
    for cur_param_name, cur_param_value in all_event_params.items():
        jsonable_result = await get_jsonable_value(
            orig_object=cur_param_value,
            object_log_name=cur_param_name,
            log_invalid_json=TELETHON_OPTIONS.LOG_NON_JSON_SERIALIZABLE_OBJ)

        if not jsonable_result:
            continue

        if cur_param_name.startswith(
                TELETHON_OPTIONS.EVENT_ATTRS_SECTION_SEPARATOR_PREFIX):
            continue

        webhook_event_data[cur_param_name] = jsonable_result[1]

    await send_event_data_webhook_req(
        new_event_data=webhook_event_data,
        source="tlt_tg_aggregator_manager",
        operation="new message event",
        aggregator_url=AGGREGATOR_API_WEBHOOKS_URL)
