from typing import Dict

from fastapi import APIRouter
from starlette import status
from starlette.responses import JSONResponse

from configs.console_colors import CONSOLE_COLORS
from configs.options import API_OPTIONS
from fast_api.app_auth.funcs_auth import (
    verify_auth_username_password)
from fast_api.app_auth.scheme_auth import (
    AuthData)
from fast_api.app_stop_clear_tlt_clients.scheme_stop_clear_tlt_clients import (
    InStopClearTltClients)
from fast_api.app_web_account.scheme_web_account import InWebAccountData
from telethon_manager.telethon_clients_manager import (
    TelethonManagerSingleton)

base_url_name = API_OPTIONS.API_BASE_URL_NAME
rtr_stop_clear_tlt_clients = APIRouter(prefix=f"/{base_url_name}",
                                       tags=["TELEGRAM TLT ENDPOINTS"])


@rtr_stop_clear_tlt_clients.post("/stop_clear_tg_clients")
async def stop_clear_tlt_clients_router(
        auth_data: AuthData,
        web_account_data: InWebAccountData,
        stop_clients_data: InStopClearTltClients
) -> JSONResponse:
    await verify_auth_username_password(
        username=auth_data.username,
        password=auth_data.password)

    web_account_id = web_account_data.web_account_id
    web_account_username = web_account_data.web_account_username

    tlt_configs_names = stop_clients_data.telethon_configs_names

    stopped_clients = []
    skipped_clients = []
    stopped_async_tasks = []
    skipped_async_tasks = []
    stopped_clients_logs: Dict[str, Dict[str, str]] = {}

    tlt_manager = TelethonManagerSingleton()  # Singleton

    for cur_config_name in tlt_configs_names:
        stop_client_res, stop_client_log = await tlt_manager.disconnect_tlt_client(
            config_name=cur_config_name)
        if stop_client_res:
            stopped_clients.append(cur_config_name)
        else:
            skipped_clients.append(cur_config_name)

        stop_async_res, stop_async_log = await tlt_manager.cancel_tlt_async_task(
            config_name=cur_config_name)
        if stop_async_res:
            stopped_async_tasks.append(cur_config_name)
        else:
            skipped_async_tasks.append(cur_config_name)

        stopped_clients_logs[cur_config_name] = {
            "stop_client_log": stop_client_log,
            "stop_async_log": stop_async_log}

        tlt_manager.not_started_configs.pop(cur_config_name, None)
        tlt_manager.event_handlers.pop(cur_config_name, None)
        tlt_manager.qrcode_logins.pop(cur_config_name, None)

    blue_clr = CONSOLE_COLORS.BRIGHT_BLUE
    yellow_clr = CONSOLE_COLORS.BRIGHT_YELLOW
    green_clr = CONSOLE_COLORS.BRIGHT_GREEN
    reset_clr = CONSOLE_COLORS.RESET
    magenta_clr = CONSOLE_COLORS.BRIGHT_MAGENTA

    all_configs_total = len(tlt_configs_names)
    print(f"\n{yellow_clr}All stopped clients "
          f"[{len(stopped_clients)}/{all_configs_total}]:{reset_clr}")
    for cur_stopped_config in stopped_clients:
        print(f"{yellow_clr}{cur_stopped_config}{reset_clr}")

    print(f"\n{magenta_clr}All skipped clients "
          f"[{len(skipped_clients)}/{all_configs_total}]:{reset_clr}")
    for cur_skipped_config in skipped_clients:
        print(f"{magenta_clr}{cur_skipped_config}{reset_clr}")

    print(f"\n{blue_clr}All stopped async tasks "
          f"[{len(stopped_async_tasks)}/{all_configs_total}]:{reset_clr}")
    for cur_stopped_async_task in stopped_async_tasks:
        print(f"{blue_clr}{cur_stopped_async_task}{reset_clr}")

    print(f"\n{green_clr}All skipped async tasks "
          f"[{len(skipped_async_tasks)}/{all_configs_total}]:{reset_clr}")
    for cur_skipped_async_task in skipped_async_tasks:
        print(f"{green_clr}{cur_skipped_async_task}{reset_clr}")

    if not tlt_configs_names:
        stop_message = "Empty TLT clients configs list to stop [OK]:"
    elif stopped_clients and not skipped_clients:
        stop_message = "All TLT clients stopped successfully [OK]:"
    elif stopped_clients and skipped_clients:
        stop_message = "TLT clients stopped partly [OK]:"
    else:
        stop_message = "All TLT clients not stopped [ERROR]:"

    json_response = JSONResponse(
        content={"stop_message": stop_message,
                 "username": auth_data.username,
                 "web_account_id": web_account_id,
                 "web_account_username": web_account_username,
                 "tlt_configs_names": tlt_configs_names,
                 "stopped_clients": stopped_clients,
                 "skipped_clients": skipped_clients,
                 "stopped_async_tasks": stopped_async_tasks,
                 "skipped_async_tasks": skipped_async_tasks,
                 "stopped_clients_logs": stopped_clients_logs},
        status_code=status.HTTP_200_OK)
    print(f"{stop_message}\n"
          f"tlt_configs_names: {tlt_configs_names}\n"
          f"stopped_clients: {stopped_clients}\n"
          f"skipped_clients: {skipped_clients}\n"
          f"stopped_async_tasks: {stopped_async_tasks}\n"
          f"skipped_async_tasks: {skipped_async_tasks}\n"
          f"stopped_clients_logs: {stopped_clients_logs}\n")
    return json_response
