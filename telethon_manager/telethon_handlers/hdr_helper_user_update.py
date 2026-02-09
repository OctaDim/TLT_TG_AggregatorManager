from telethon import events, TelegramClient

from telethon_manager.telethon_client_config import TelethonConfig


async def user_update_handler_helper(
        event: events.UserUpdate.Event,
        telethon_client: TelegramClient,
        telethon_config: TelethonConfig
) -> None:
    # print(f"USER UPDATE EVENT:\n"
    #       f"event: {event}\n")
    return None
