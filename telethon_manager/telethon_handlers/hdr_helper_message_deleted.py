from telethon import events, TelegramClient

from telethon_manager.telethon_client_config import TelethonConfig
from utils_common.clean_str_new_lines_spaces import clean_text
from utils_common.get_obj_attrs_vals_by_attr_chain import (
    get_attrs_values_by_attr_chains, get_attr_value_by_attr_chain)


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

    # new_msg_evnt_params = {}  # print(event.stringify())
    #
    # evnt_message_message = await get_attr_value_by_attr_chain(
    #     base_class_or_obj=event,
    #     attribute_chain="message.message")
    # evnt_message_message = await clean_text(origin_text=evnt_message_message,
    #                                         clean_line_breaks=True,
    #                                         clean_continuous_spaces=True)
    # new_msg_evnt_params["evnt_message_message"] = evnt_message_message
    #
    # evnt_message_text = await get_attr_value_by_attr_chain(
    #     base_class_or_obj=event,
    #     attribute_chain="message.text")
    # evnt_message_text = await clean_text(origin_text=evnt_message_text,
    #                                      clean_line_breaks=True,
    #                                      clean_continuous_spaces=True)
    # new_msg_evnt_params["evnt_message_text"] = evnt_message_text
    #
    # print(f"\n{'=' * 80}\nDELETED MESSAGE EVENT:\n{'=' * 80}")
    # for cur_param_str, cur_param_val in new_msg_evnt_params.items():
    #     print(f"{cur_param_str} = {cur_param_val}")
    # print(f"{'=' * 80}\n{'=' * 80}\n")
