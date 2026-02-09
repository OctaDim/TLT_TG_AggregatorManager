from telethon import events, TelegramClient

from telethon_manager.telethon_client_config import TelethonConfig


async def raw_event_handler_helper(
        event: events.Raw,
        telethon_client: TelegramClient,
        telethon_config: TelethonConfig
) -> None:
    # print(f"RAW EVENT:\n"
    #       f"event: {event}\n")
    return None
