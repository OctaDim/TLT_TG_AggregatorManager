from telethon import events, TelegramClient

from configs.settings import TELETHON_OPTIONS
from telethon_manager.telethon_attrs_chains.chain_message_deleted import (
    get_msg_delete_attr_chains)
from telethon_manager.telethon_client_config import TelethonConfig
from utils_common.get_obj_attrs_vals_by_attr_chain import (
    get_attrs_values_by_attr_chains)
from utils_specific.handle_all_event_params import (
    send_all_event_params)


async def message_deleted_handler_helper(
        event: events.MessageDeleted.Event,
        telethon_client: TelegramClient,
        telethon_config: TelethonConfig,
        event_type: str = None
) -> None:
    separator = TELETHON_OPTIONS.EVENT_ATTRS_SECTION_SEPARATOR_PREFIX
    handler_specific_params = {}

    # Getting handler specific params
    event_main_params = await get_attrs_values_by_attr_chains(
        base_class_or_obj=event,
        attributes_chains_dict=get_msg_delete_attr_chains(),
        section_separator_prefix=separator)
    handler_specific_params.update(event_main_params)

    # Separate function because handler function with its own params values
    # is enclosed by add_all_telethon_client_handlers()
    await send_all_event_params(
        event=event,
        telethon_client=telethon_client,
        telethon_config=telethon_config,
        event_type=event_type,
        handler_additional_params=handler_specific_params)
