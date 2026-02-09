from telethon import events, TelegramClient

from telethon_manager.telethon_client_config import TelethonConfig


async def message_deleted_handler_helper(
        event: events.MessageDeleted.Event,
        telethon_client: TelegramClient,
        telethon_config: TelethonConfig
) -> None:
    # print(f"MESSAGE DELETED EVENT:\n"
    #       f"event: {event}\n")
    return None
