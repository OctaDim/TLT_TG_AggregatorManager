from telethon import events, TelegramClient
from telethon.tl.types import (
    UserStatusOnline, UserStatusOffline, UserStatusRecently,
    UserStatusLastWeek, UserStatusLastMonth, UserStatusEmpty,
    SendMessageTypingAction)

from configs.labels_messages import ACTION_STATUS
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

    event_client_obj = event_main_params["ev__client"]
    ev_orig_upd_user_id = event_main_params["ev_orig_upd_user_id"]
    ev_orig_upd_from_id = event_main_params["ev_orig_upd_from_id"]
    user_data_params = {}
    if ev_orig_upd_user_id:
        try:
            entity_user_obj = await event_client_obj.get_entity(ev_orig_upd_user_id)
            user_data_params = await get_attrs_values_by_attr_chains(
                base_class_or_obj=entity_user_obj,
                attributes_chains_dict=get_user_data_attr_chains(),
                section_separator_prefix=separator)
        except (ValueError, Exception):
            pass
    elif ev_orig_upd_from_id:
        try:
            entity_user_obj = await event_client_obj.get_entity(ev_orig_upd_user_id)
            user_data_params = await get_attrs_values_by_attr_chains(
                base_class_or_obj=entity_user_obj,
                attributes_chains_dict=get_user_data_attr_chains(),
                section_separator_prefix=separator)
        except (ValueError, Exception):
            pass
    else:
        try:
            event_user_obj = await event.get_chat()
            user_data_params = await get_attrs_values_by_attr_chains(
                base_class_or_obj=event_user_obj,
                attributes_chains_dict=get_user_data_attr_chains(),
                section_separator_prefix=separator)
        except Exception:
            pass
    if user_data_params:
        handler_specific_params.update({
            "user_username": user_data_params["user_username"],
            "user_first_name": user_data_params["user_first_name"],
            "user_last_name": user_data_params["user_last_name"],
            "user_phone": user_data_params["user_phone"],
            "user_bot": user_data_params["user_bot"], })

    ev_status = event_main_params["ev_status"]
    ev_action = event_main_params["ev_action"]
    # ev_status
    if isinstance(ev_status, UserStatusOnline):
        action_field_str = ACTION_STATUS.USER_ONLINE_UPDATE_STATUS_STR
    elif isinstance(ev_status, UserStatusOffline):
        action_field_str = ACTION_STATUS.USER_OFFLINE_UPDATE_STATUS_STR
    elif isinstance(ev_status, UserStatusRecently):
        action_field_str = ACTION_STATUS.USER_RECENTLY_UPDATE_STATUS_STR
    elif isinstance(ev_status, UserStatusLastWeek):
        action_field_str = ACTION_STATUS.USER_LAST_WEEK_UPDATE_STATUS_STR
    elif isinstance(ev_status, UserStatusLastMonth):
        action_field_str = ACTION_STATUS.USER_LAST_MONTH_UPDATE_STATUS_STR
    elif isinstance(ev_status, UserStatusEmpty):
        action_field_str = ACTION_STATUS.USER_UNDEFINED_UPDATE_STR
    # ev_action
    elif isinstance(ev_action, SendMessageTypingAction):
        action_field_str = ACTION_STATUS.USER_TYPING_UPDATE_ACTION_STR
    else:
        action_field_str = ACTION_STATUS.USER_UNDEFINED_UPDATE_STR
    handler_specific_params.update({"action": action_field_str})

    # Separate function because handler function with its own params values
    # is enclosed by add_all_telethon_client_handlers()
    await send_all_event_params(
        event=event,
        telethon_client=telethon_client,
        telethon_config=telethon_config,
        event_type=event_type,
        handler_additional_params=handler_specific_params)
