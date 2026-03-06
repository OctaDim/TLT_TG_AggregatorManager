from telethon import events, TelegramClient
from telethon.tl.types import (
    MessageActionChatAddUser, MessageActionChatDeleteUser,
    MessageActionChatCreate, MessageActionChatEditTitle)

from configs.labels_messages import ACTION_STATUS
from configs.settings import TELETHON_OPTIONS
from telethon_manager.telethon_attrs_chains.chain_chat_action import (
    get_chat_action_attr_chains)
from telethon_manager.telethon_attrs_chains.chain_user_data import (
    get_user_data_attr_chains)
from telethon_manager.telethon_client_config import TelethonConfig
from utils_common.get_obj_attrs_vals_by_attr_chain import (
    get_attrs_values_by_attr_chains)
from utils_specific.handle_all_event_params import (
    send_all_event_params)


async def chat_action_handler_helper(
        event: events.ChatAction.Event,
        telethon_client: TelegramClient,
        telethon_config: TelethonConfig,
        event_type: str = None
) -> None:
    if not TELETHON_OPTIONS.HANDLE_CHAT_ACTION_EVENT:
        log_txt = (f"\nDEBUG: WEBHOOK SKIPPED [ERROR]:\n"
                   f"event_type: {event_type}\n")
        print(log_txt)
        return

    separator = TELETHON_OPTIONS.EVENT_ATTRS_SECTION_SEPARATOR_PREFIX
    handler_specific_params = {}

    # Getting handler specific params
    event_main_params = await get_attrs_values_by_attr_chains(
        base_class_or_obj=event,
        attributes_chains_dict=get_chat_action_attr_chains(),
        section_separator_prefix=separator)
    handler_specific_params.update(event_main_params)

    event_client_obj = event_main_params["ev__client"]
    from_id_user = event_main_params["ev_act_msg_from_id"]
    entity_user_obj = await event_client_obj.get_entity(from_id_user)
    user_data_params = await get_attrs_values_by_attr_chains(
        base_class_or_obj=entity_user_obj,
        attributes_chains_dict=get_user_data_attr_chains(),
        section_separator_prefix=separator)
    handler_specific_params.update({
        "user_username": user_data_params["user_username"],
        "user_first_name": user_data_params["user_first_name"],
        "user_last_name": user_data_params["user_last_name"],
        "user_phone": user_data_params["user_phone"],
        "user_bot": user_data_params["user_bot"], })

    ev_act_msg_action = event_main_params["ev_act_msg_action"]
    if isinstance(ev_act_msg_action, MessageActionChatAddUser):
        action_field_str = ACTION_STATUS.CHAT_USER_ADDED_ACTION_STR
    elif isinstance(ev_act_msg_action, MessageActionChatDeleteUser):
        action_field_str = ACTION_STATUS.CHAT_USER_DELETED_ACTION_STR
    elif isinstance(ev_act_msg_action, MessageActionChatEditTitle):
        action_field_str = ACTION_STATUS.CHAT_TITLE_RENAMED_ACTION_STR
    elif isinstance(ev_act_msg_action, MessageActionChatCreate):
        action_field_str = ACTION_STATUS.CHAT_NEW_CREATED_ACTION_STR
    else:
        action_field_str = ACTION_STATUS.CHAT_UNDEFINED_ACTION_STR
    handler_specific_params.update({"action": action_field_str})

    # Separate function because handler function with its own params values
    # is enclosed by add_all_telethon_client_handlers()
    await send_all_event_params(
        event=event,
        telethon_client=telethon_client,
        telethon_config=telethon_config,
        event_type=event_type,
        handler_additional_params=handler_specific_params)
