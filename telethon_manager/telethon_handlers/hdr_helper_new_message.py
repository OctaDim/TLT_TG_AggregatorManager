from telethon import events, TelegramClient

from telethon_manager.telethon_client_config import TelethonConfig


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

    telethon_config_id = telethon_config.telethon_config_id
    config_name = telethon_config.name
    config_phone = telethon_config.phone
    config_bot_token = telethon_config.bot_token
    config_bot_token = config_bot_token[:10] if config_bot_token else None
    telethon_account_type = telethon_config.account_type
    web_account_id = telethon_config.web_account_id
    web_account_username = telethon_config.web_account_username
    event_id = event.id
    event_client_id = id(event.client) if hasattr(event, "client") else None
    telethon_client_id = id(telethon_client)
    event_client = event.client
    telethon_client = telethon_client  # Just for info
    sender = await event.get_sender()
    chat = await event.get_chat()
    message_txt = event.message.text
    message_txt = message_txt if len(message_txt) <= 10 else f"{message_txt[:10]}..."
    chat_title = getattr(chat, "title", "")

    sender_first_name = getattr(sender, "first_name", "")
    sender_last_name = getattr(sender, "last_name", "")
    sender_username = getattr(sender, "username", "")
    sender_phone = getattr(sender, "phone", "")
    sender_is_bot = getattr(sender, "bot", "")
    if sender_first_name and sender_last_name:
        sender_name = f"{sender_first_name} {sender_last_name}"
    elif sender_first_name or sender_last_name:
        sender_name = sender_first_name or sender_last_name
    else:
        sender_name = ""

    event_data = {"message_txt": message_txt,
                  "telethon_config_id": telethon_config_id,
                  "config_name": config_name,
                  "config_phone": config_phone,
                  "config_bot_token": config_bot_token,
                  "telethon_account_type": telethon_account_type,
                  "web_account_id": web_account_id,
                  "web_account_username": web_account_username,
                  "event_id": event_id,
                  "event_client_id": event_client_id,
                  "telethon_client_id": telethon_client_id,
                  "event_client": event_client,
                  "telethon_client": telethon_client,
                  "sender": sender,
                  "chat": chat,
                  "chat_title": chat_title,
                  "sender_name": sender_name,
                  "sender_username": sender_username,
                  "sender_phone": sender_phone,
                  "sender_is_bot": sender_is_bot, }

    print()
    for cur_name, cur_val in event_data.items():
        print(f"\t\t{cur_name} = {cur_val}")
    print()
