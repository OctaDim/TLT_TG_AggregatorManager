from telethon import events, TelegramClient

from telethon_manager.telethon_client_config import TelethonConfig


async def album_event_handler_helper(
        event: events.Album.Event,
        telethon_client: TelegramClient,
        telethon_config: TelethonConfig,
        event_type: str = None
) -> None:
    if None in (telethon_client, telethon_config):
        print(f"Deleted Telethon object(s), not handled event [ERROR]:\n"
              f"telethon_client: {telethon_client}\n"
              f"telethon_config: {telethon_config}\n")
        return

    # print(f"\n{'=' * 80}\n{'=' * 80}")
    # print("ALBUM EVENT:")
    # print(event.stringify())
    # print(f"{'=' * 80}\n{'=' * 80}\n")
