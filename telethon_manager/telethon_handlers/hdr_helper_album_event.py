from telethon import events, TelegramClient

from telethon_manager.telethon_client_config import TelethonConfig


async def album_event_handler_helper(
        event: events.Album.Event,
        telethon_client: TelegramClient,
        telethon_config: TelethonConfig
) -> None:
    # print(f"ALBUM EVENT:\n"
    #       f"event: {event}\n")
    return None
