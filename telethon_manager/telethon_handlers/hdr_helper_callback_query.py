from telethon import events, TelegramClient

from telethon_manager.telethon_client_config import TelethonConfig


async def callback_query_handler_helper(
        event: events.CallbackQuery.Event,
        telethon_client: TelegramClient,
        telethon_config: TelethonConfig
) -> None:
    # print(f"CALLBACK QUERY EVENT:\n"
    #       f"event: {event}\n")
    return None
