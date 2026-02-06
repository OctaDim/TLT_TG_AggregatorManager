from telethon import events, TelegramClient

from telethon_manager.telethon_client_config import TelethonConfig


async def message_read_handler_helper(
        event: events.NewMessage.Event,
        telethon_client: TelegramClient,
        telethon_config: TelethonConfig
) -> None:
    # print(f"MESSAGE READ EVENT:\n"
    #       f"event: {event}\n")
    return None
