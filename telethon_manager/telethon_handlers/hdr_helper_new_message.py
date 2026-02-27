from telethon import events, TelegramClient

from telethon_manager.telethon_client_config import TelethonConfig
from telethon_manager.telethon_handlers.hdr_func_new_edit_message import (
    new_edit_message_handler_func)


async def new_message_handler_helper(
        event: events.NewMessage.Event,
        telethon_client: TelegramClient,
        telethon_config: TelethonConfig,
        event_type: str = None
) -> None:
    # Separate function because handler function with its own params values
    # is enclosed by add_all_telethon_client_handlers()
    await new_edit_message_handler_func(event=event,
                                        telethon_client=telethon_client,
                                        telethon_config=telethon_config,
                                        event_type=event_type)
