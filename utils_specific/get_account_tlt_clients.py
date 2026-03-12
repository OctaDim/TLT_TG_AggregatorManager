from typing import Dict

from telethon import TelegramClient

from telethon_manager.telethon_clients_manager import (
    TelethonManagerSingleton)


async def get_account_only_tlt_clients(
        telethon_manager: TelethonManagerSingleton,
        web_account_id: str,
        web_account_username: str
) -> Dict[str, TelegramClient]:
    tlt_manager_clients = telethon_manager.clients
    config_partly_name = f"_{web_account_id}_{web_account_username}"
    account_only_clients = {}

    for cur_config_name, cur_tlt_client in tlt_manager_clients.items():
        if config_partly_name in cur_config_name:
            account_only_clients[cur_config_name] = cur_tlt_client
    return account_only_clients
