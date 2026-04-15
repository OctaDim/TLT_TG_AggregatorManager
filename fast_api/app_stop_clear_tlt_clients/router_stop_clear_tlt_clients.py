from typing import Dict

from fastapi import APIRouter
from starlette import status
from starlette.responses import JSONResponse

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

    tlt_configs_names = stop_clients_data.telethon_config_name

    stopped_clients = []
    skipped_clients = []
    stopped_clients_logs: Dict[str, Dict[str, str]] = {}

    tlt_manager = TelethonManagerSingleton()  # Singleton

    for cur_config_name in tlt_configs_names:
        stop_client_res, stop_client_log = await tlt_manager.disconnect_tlt_client(
            config_name=cur_config_name)
        if stop_client_res:
            stopped_clients.append(cur_config_name)
        else:
            skipped_clients.append(cur_config_name)
        stopped_clients_logs[cur_config_name].update({
            "stop_client_log": stop_client_log})

        _, stop_async_task_log = await tlt_manager.cancel_tlt_async_task(
            config_name=cur_config_name)
        stopped_clients_logs[cur_config_name].update({
            "stop_async_task_log": stop_async_task_log})

        tlt_manager.not_started_configs.pop(cur_config_name, None)
        tlt_manager.event_handlers.pop(cur_config_name, None)
        tlt_manager.qrcode_logins.pop(cur_config_name, None)

    if not tlt_configs_names:
        stop_message = "Empty TLT clients configs list to stop [OK]:"
    elif stopped_clients and not skipped_clients:
        stop_message = "All TLT clients stopped successfully [OK]:"
    elif stopped_clients and skipped_clients:
        stop_message = "TLT clients stopped partly [OK]:"
    else:
        stop_message = "All TLT clients not stopped [ERROR]:"

    json_response = JSONResponse(
        content={"stop_message": {stop_message},
                 "username": auth_data.username,
                 "web_account_id": web_account_id,
                 "web_account_username": web_account_username,
                 "tlt_configs_names": tlt_configs_names,
                 "stopped_clients": stopped_clients,
                 "skipped_clients": skipped_clients,
                 "stopped_clients_logs": stopped_clients_logs},
        status_code=status.HTTP_200_OK)
    print(f"{stop_message}\n"
          f"tlt_configs_names: {tlt_configs_names}\n"
          f"stopped_clients: {stopped_clients}\n"
          f"skipped_clients: {skipped_clients}\n"
          f"stopped_clients_logs: {stopped_clients_logs}\n")
    return json_response
