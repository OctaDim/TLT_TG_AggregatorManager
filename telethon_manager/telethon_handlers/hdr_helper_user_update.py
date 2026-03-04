from telethon import events, TelegramClient

from configs.settings import TELETHON_OPTIONS
from telethon_manager.telethon_attrs_chains.chain_user_data import (
    get_user_data_attr_chains)
from telethon_manager.telethon_attrs_chains.chain_user_update import (
    get_user_update_attr_chains)
from telethon_manager.telethon_client_config import TelethonConfig
from utils_common.get_obj_attrs_vals_by_attr_chain import (
    get_attrs_values_by_attr_chains)
from utils_specific.handle_all_event_params import (
    send_all_event_params)


async def user_update_handler_helper(
        event: events.MessageDeleted.Event,
        telethon_client: TelegramClient,
        telethon_config: TelethonConfig,
        event_type: str = None
) -> None:
    if not TELETHON_OPTIONS.HANDLE_USER_UPDATE_EVENT:
        log_txt = (f"\nDEBUG: WEBHOOK SKIPPED [ERROR]:\n"
                   f"event_type: {event_type}\n")
        print(log_txt)
        return

    separator = TELETHON_OPTIONS.EVENT_ATTRS_SECTION_SEPARATOR_PREFIX
    handler_specific_params = {}

    # Getting handler specific params
    event_main_params = await get_attrs_values_by_attr_chains(
        base_class_or_obj=event,
        attributes_chains_dict=get_user_update_attr_chains(),
        section_separator_prefix=separator)
    handler_specific_params.update(event_main_params)

    event_user_obj = await event.get_chat()
    user_data_params = await get_attrs_values_by_attr_chains(
        base_class_or_obj=event_user_obj,
        attributes_chains_dict=get_user_data_attr_chains(),
        section_separator_prefix=separator)
    handler_specific_params.update(user_data_params)

    # Separate function because handler function with its own params values
    # is enclosed by add_all_telethon_client_handlers()
    await send_all_event_params(
        event=event,
        telethon_client=telethon_client,
        telethon_config=telethon_config,
        event_type=event_type,
        handler_additional_params=handler_specific_params)
