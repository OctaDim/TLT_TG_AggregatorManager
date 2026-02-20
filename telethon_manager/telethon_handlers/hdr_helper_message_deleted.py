from telethon import events, TelegramClient

from configs.settings import TELETHON_OPTIONS
from telethon_manager.telethon_attrs_chains.chain_delete_message import (
    get_msg_delete_attr_chains)
from telethon_manager.telethon_client_config import TelethonConfig
from utils_common.get_obj_attrs_vals_by_attr_chain import (
    get_attrs_values_by_attr_chains)


async def message_deleted_handler_helper(
        event: events.MessageDeleted.Event,
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

    if telethon_config.bot_token:
        tlt_bot_token_info = telethon_config.bot_token[:10]
    else:
        tlt_bot_token_info = None

    attrs_chains = get_msg_delete_attr_chains()  # MessageDeleted attrs chains
    event_params = {
        "event_type": "MessageDeleted",
        "web_account_id": telethon_config.web_account_id,
        "web_account_username": telethon_config.web_account_username,
        "tlt_account_type": telethon_config.account_type.value,
        "tlt_phone": telethon_config.phone,
        "tlt_bot_token": tlt_bot_token_info,
        "separator": "", }

    new_msg_evnt_data = await get_attrs_values_by_attr_chains(
        base_class_or_obj=event,
        attributes_chains_dict=attrs_chains,
        section_separator_prefix="separator")
    event_params.update(new_msg_evnt_data)

    print(f"\nDELETED MESSAGE EVENT:\n{'=' * 80}")
    for cur_param_str, cur_param_val in event_params.items():
        if cur_param_str.startswith("separator"):
            print(f"\t")
            continue
        if cur_param_val is None:
            print(f"\t{cur_param_str} ==")
        else:
            print(f"\t{cur_param_str} == {cur_param_val} ({type(cur_param_val)})")
    print(f"{'=' * 80}\n{'=' * 80}\n")
