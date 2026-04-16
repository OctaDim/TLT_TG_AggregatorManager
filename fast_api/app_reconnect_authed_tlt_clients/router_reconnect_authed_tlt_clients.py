from typing import Dict

from fastapi import APIRouter
from starlette import status
from starlette.responses import JSONResponse

from configs.console_colors import CONSOLE_COLORS
from configs.options import API_OPTIONS
from db_postgres.postgres_queries.qry_update_telethon_active_status import (
    update_telethon_active_status_qry)
from fast_api.app_auth.funcs_auth import (
    verify_auth_username_password)
from fast_api.app_auth.scheme_auth import (
    AuthData)
from fast_api.app_reconnect_authed_tlt_clients.scheme_reconnect_authed_tlt_clients import (
    InReconnectAuthedTltClients)
from fast_api.app_web_account.scheme_web_account import InWebAccountData
from telethon_manager.telethon_clients_manager import (
    TelethonManagerSingleton)

base_url_name = API_OPTIONS.API_BASE_URL_NAME
rtr_reconnect_authed_tlt_clients = APIRouter(prefix=f"/{base_url_name}",
                                             tags=["TELEGRAM TLT ENDPOINTS"])


@rtr_reconnect_authed_tlt_clients.post("/reconnect_authed_tg_clients")
async def reconnect_authed_tlt_clients_router(
        auth_data: AuthData,
        web_account_data: InWebAccountData,
        reconnect_clients_data: InReconnectAuthedTltClients
) -> JSONResponse:
    await verify_auth_username_password(
        username=auth_data.username,
        password=auth_data.password)

    web_account_id = web_account_data.web_account_id
    web_account_username = web_account_data.web_account_username

    tlt_configs_names = reconnect_clients_data.telethon_configs_names

    connected_clients = []
    skipped_clients = []
    connect_clients_logs: Dict[str, Dict[str, str]] = {}

    tlt_manager = TelethonManagerSingleton()  # Singleton

    for cur_config_name in tlt_configs_names:
        connect_res, connect_log = await tlt_manager.connect_tlt_client(
            config_name=cur_config_name)
        if connect_res:
            connected_clients.append(cur_config_name)
            update_data = {"telethon_is_active": True}
            await update_telethon_active_status_qry(
                telethon_config_name=cur_config_name,
                update_data=update_data)
        else:
            skipped_clients.append(cur_config_name)

        connect_clients_logs[cur_config_name] = {
            "connect_client_log": connect_log}

    blue_clr = CONSOLE_COLORS.BRIGHT_BLUE
    yellow_clr = CONSOLE_COLORS.BRIGHT_YELLOW
    green_clr = CONSOLE_COLORS.BRIGHT_GREEN
    reset_clr = CONSOLE_COLORS.RESET
    magenta_clr = CONSOLE_COLORS.BRIGHT_MAGENTA

    all_configs_total = len(tlt_configs_names)
    print(f"\n{yellow_clr}All connected clients "
          f"[{len(connected_clients)}/{all_configs_total}]:{reset_clr}")
    for cur_stopped_config in connected_clients:
        print(f"{yellow_clr}{cur_stopped_config}{reset_clr}")

    print(f"\n{magenta_clr}All skipped clients "
          f"[{len(skipped_clients)}/{all_configs_total}]:{reset_clr}")
    for cur_skipped_config in skipped_clients:
        print(f"{magenta_clr}{cur_skipped_config}{reset_clr}")

    if not tlt_configs_names:
        connect_message = "Empty TLT clients configs list to connect [OK]:"
    elif connected_clients and not skipped_clients:
        connect_message = "All TLT clients connected successfully [OK]:"
    elif connected_clients and skipped_clients:
        connect_message = "TLT clients connected partly [OK]:"
    else:
        connect_message = "All TLT clients not connected [ERROR]:"

    json_response = JSONResponse(
        content={"connect_message": connect_message,
                 "username": auth_data.username,
                 "web_account_id": web_account_id,
                 "web_account_username": web_account_username,
                 "tlt_configs_names": tlt_configs_names,
                 "connected_clients": connected_clients,
                 "skipped_clients": skipped_clients,
                 "connect_clients_logs": connect_clients_logs},
        status_code=status.HTTP_200_OK)
    print(f"{connect_message}\n"
          f"tlt_configs_names: {tlt_configs_names}\n"
          f"connected_clients: {connected_clients}\n"
          f"skipped_clients: {skipped_clients}\n"
          f"connect_clients_logs: {connect_clients_logs}\n")
    return json_response
