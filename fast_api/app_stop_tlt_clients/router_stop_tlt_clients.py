from fastapi import APIRouter
from starlette import status
from starlette.responses import JSONResponse

from configs.options import API_OPTIONS
from fast_api.app_auth.funcs_auth import (
    verify_auth_username_password)
from fast_api.app_auth.scheme_auth import (
    AuthData)
from fast_api.app_stop_tlt_clients.scheme_stop_tlt_clients import (
    InStopTltClients)
from fast_api.app_web_account.scheme_web_account import InWebAccountData
from telethon_manager.telethon_clients_manager import (
    TelethonManagerSingleton)

base_url_name = API_OPTIONS.API_BASE_URL_NAME
rtr_stop_tlt_clients = APIRouter(prefix=f"/{base_url_name}",
                                 tags=["TELEGRAM TLT ENDPOINTS"])


@rtr_stop_tlt_clients.post("/stop_tg_clients")
async def stop_tlt_clients_router(
        auth_data: AuthData,
        web_account_data: InWebAccountData,
        stop_clients_data: InStopTltClients
) -> JSONResponse:
    await verify_auth_username_password(
        username=auth_data.username,
        password=auth_data.password)

    web_account_id = web_account_data.web_account_id
    web_account_username = web_account_data.web_account_username

    tlt_configs_names = stop_clients_data.telethon_config_name

    stopped_clients = []
    skipped_clients = []
    cur_config_name = None

    try:
        tlt_manager = TelethonManagerSingleton()  # Singleton

        for cur_config_name in tlt_configs_names:
            cur_tlt_client = tlt_manager.clients.get(cur_config_name)
            if cur_tlt_client:
                await cur_tlt_client.disconnect()
                stopped_clients.append(cur_config_name)
                tlt_manager.clients.pop(cur_config_name)
            else:
                skipped_clients.append(cur_config_name)

        stop_message = "Telethon clients stopped [OK]"
        json_response = JSONResponse(
            content={"stop_msg": {stop_message},
                     "username": auth_data.username,
                     "web_account_id": web_account_id,
                     "web_account_username": web_account_username,
                     "tlt_configs_names": tlt_configs_names,
                     "stopped_clients": stopped_clients,
                     "skipped_clients": skipped_clients},
            status_code=status.HTTP_200_OK)
        print(f"{stop_message}\n"
              f"tlt_configs_names: {tlt_configs_names}\n"
              f"stopped_clients: {stopped_clients}"
              f"skipped_clients: {skipped_clients}\n")
        return json_response
    except Exception as error:
        error_message = (f"Router Stop TLT clients error: \n"
                         f"error: {error}\n")
        json_response = JSONResponse(
            content={"error_message": error_message,
                     "username": auth_data.username,
                     "web_account_id": web_account_id,
                     "web_account_username": web_account_username,
                     "tlt_configs_names": tlt_configs_names,
                     "cur_config_name": cur_config_name,
                     "stopped_clients": stopped_clients,
                     "skipped_clients": skipped_clients},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        print(error_message)
        return json_response
