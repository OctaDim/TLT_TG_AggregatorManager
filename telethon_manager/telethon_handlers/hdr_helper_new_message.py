import re

from telethon import events, TelegramClient

from telethon_manager.telethon_client_config import TelethonConfig
from utils_common.get_object_value_by_attrs import get_obj_value_by_attrs_chain


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

    evt_message = get_obj_value_by_attrs_chain(
        base_class_or_obj=event,
        all_attributes_chain="message.text")
    message_text = re.sub(pattern=r"(\n)|(\r)", repl=" ", string=evt_message)

    evt_peer_id = get_obj_value_by_attrs_chain(
        base_class_or_obj=event,
        all_attributes_chain="message.peer_id")

    print(f"\n{'=' * 80}\n{'=' * 80}")
    print("NEW MESSAGE EVENT:")
    print(message_text)
    print(evt_peer_id)
    # print(event.stringify())
    print(f"{'=' * 80}\n{'=' * 80}\n")
