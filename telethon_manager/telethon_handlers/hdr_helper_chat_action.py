from telethon import events, TelegramClient

from telethon_manager.telethon_client_config import TelethonConfig


async def chat_action_handler_helper(
        event: events.NewMessage.Event,
        telethon_client: TelegramClient,
        telethon_config: TelethonConfig
) -> None:
    # print(f"CHAT ACTION EVENT:\n"
    #       f"event: {event}\n")
    return None
