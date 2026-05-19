from typing import Dict, List

from telethon import TelegramClient

from telethon_manager.telethon_client_config import TelethonConfig
from telethon_manager.telethon_clients_manager import (
    TelethonManagerSingleton)


async def get_acc_only_started_tlt_clients(
        telethon_manager: TelethonManagerSingleton,
        web_account_id: str,
        web_account_username: str,
        skip_disconnected: bool = False,
        allowed_configs: List[str] = None,
) -> Dict[str, TelegramClient]:
    tlt_manager_clients = telethon_manager.clients
    config_partly_name = f"_{web_account_id}_{web_account_username}"

    acc_only_clients = {}
    for cur_config_name, cur_tlt_client in tlt_manager_clients.items():
        if config_partly_name in cur_config_name:
            if not skip_disconnected or cur_tlt_client.is_connected():
                acc_only_clients[cur_config_name] = cur_tlt_client

    if allowed_configs:
        allowed_only_clients = {}
        for cur_config_name, cur_tlt_client in acc_only_clients.items():
            if cur_config_name in allowed_configs:
                allowed_only_clients[cur_config_name] = cur_tlt_client
        acc_only_clients = allowed_only_clients
    return acc_only_clients


async def get_acc_only_stopped_tlt_configs(
        telethon_manager: TelethonManagerSingleton,
        web_account_id: str,
        web_account_username: str
) -> Dict[str, TelethonConfig]:
    tlt_not_started_configs = telethon_manager.not_started_configs
    config_partly_name = f"_{web_account_id}_{web_account_username}"
    acc_only_stopped_configs = {}

    for cur_config_name, cur_tlt_config in tlt_not_started_configs.items():
        if config_partly_name in cur_config_name:
            acc_only_stopped_configs[cur_config_name] = cur_tlt_config
    return acc_only_stopped_configs
