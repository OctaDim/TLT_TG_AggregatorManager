from idlelib.debugger_r import start_debugger

from fastapi import APIRouter, HTTPException
from starlette import status
from starlette.responses import JSONResponse

from configs.console_colors import CONSOLE_COLORS
from configs.options import API_OPTIONS
from fast_api.app_auth.funcs_auth import (
    verify_auth_username_password)
from fast_api.app_auth.scheme_auth import (
    AuthData)
from fast_api.app_web_account.scheme_web_account import (
    InWebAccountData)
from telethon_manager.telethon_clients_manager import (
    TelethonManagerSingleton)
from utils_specific.get_account_tlt_clients import (
    get_acc_only_started_tlt_clients, get_acc_only_stopped_tlt_configs)

base_url_name = API_OPTIONS.API_BASE_URL_NAME
rtr_tlt_configs_by_web_account = APIRouter(prefix=f"/{base_url_name}",
                                           tags=["TELEGRAM TLT ENDPOINTS"])


@rtr_tlt_configs_by_web_account.post("/get_tg_configs_by_web_acc")
async def tlt_configs_by_web_account_router(
        auth_data: AuthData,
        web_account_data: InWebAccountData,
) -> JSONResponse:
    await verify_auth_username_password(
        username=auth_data.username,
        password=auth_data.password)

    web_account_id = web_account_data.web_account_id
    web_account_username = web_account_data.web_account_username

    try:
        telethon_manager = TelethonManagerSingleton()  # Singleton
        started_tlt_clients_dict = await get_acc_only_started_tlt_clients(
            telethon_manager=telethon_manager,
            web_account_id=web_account_id,
            web_account_username=web_account_username)
        started_tlt_configs_list = list(started_tlt_clients_dict.keys())

        stopped_tlt_configs_dict = await get_acc_only_stopped_tlt_configs(
            telethon_manager=telethon_manager,
            web_account_id=web_account_id,
            web_account_username=web_account_username)
        stopped_tlt_configs_list = list(stopped_tlt_configs_dict.keys())

        all_configs_data = []
        started_configs_total = 0
        stopped_configs_total = 0
        for cur_config in started_tlt_configs_list:
            cur_tlt_client = telethon_manager.clients[cur_config]
            cur_client_is_connected = cur_tlt_client.is_connected()
            cur_client_is_authorised = await cur_tlt_client.is_user_authorized()

            if cur_client_is_connected and cur_client_is_authorised:
                started_tlt_configs_list.remove(cur_config)
                started_configs_total += 1
                status_state = True
            else:
                stopped_tlt_configs_list.append(cur_config)
                stopped_configs_total += 1
                status_state = False

            all_configs_data.append({
                "config_name": cur_config,
                "is_connected": cur_client_is_connected,
                "is_authorised": cur_client_is_authorised,
                "status": status_state})

        for cur_config in stopped_tlt_configs_list:
            stopped_configs_total += 1
            all_configs_data.append({
                "config_name": cur_config,
                "is_connected": False,
                "is_authorised": False,
                "status": False})

        all_configs_total = started_configs_total + stopped_configs_total
        json_response = JSONResponse(
            content={
                "message": "Telegram configurations found [OK]",
                "username": auth_data.username,
                "web_account_id": web_account_id,
                "web_account_username": web_account_username,
                "started_tlt_configs": started_tlt_configs_list,
                "stopped_tlt_configs": stopped_tlt_configs_list,
                "started_configs_total": started_configs_total,
                "stopped_configs_total": stopped_configs_total,
                "all_configs_data": all_configs_data,
                "all_configs_total": all_configs_total},
            status_code=status.HTTP_200_OK)

        blue_clr = CONSOLE_COLORS.BRIGHT_BLUE
        yellow_clr = CONSOLE_COLORS.BRIGHT_YELLOW
        green_clr = CONSOLE_COLORS.BRIGHT_GREEN
        reset_clr = CONSOLE_COLORS.RESET
        magenta_clr = CONSOLE_COLORS.BRIGHT_MAGENTA
        print(f"Response.body: {json_response.body}\n"
              f"Response.status_code: {json_response.status_code}\n"
              f"username: {auth_data.username}\n"
              f"web_account_id: {web_account_id}\n"
              f"web_account_username: {web_account_username}\n"
              f"started_tlt_clients_dict: {yellow_clr}{started_tlt_clients_dict}{yellow_clr}\n"
              f"started_tlt_configs_list: {yellow_clr}{started_tlt_configs_list}{reset_clr}\n"
              f"started_configs_total: {yellow_clr}{started_configs_total}{reset_clr}\n"
              f"stopped_tlt_configs_dict: {magenta_clr}{stopped_tlt_configs_dict}{yellow_clr}\n"
              f"stopped_tlt_configs_list: {magenta_clr}{stopped_tlt_configs_list}{reset_clr}\n"
              f"stopped_configs_total: {magenta_clr}{stopped_configs_total}{reset_clr}\n"
              f"all_configs_data: {blue_clr}{all_configs_data}{reset_clr}\n")

        print(f"\n{yellow_clr}All_started_configs "
              f"[{started_configs_total}]:{reset_clr}")
        for cur_config in started_tlt_configs_list:
            print(f"{yellow_clr}{cur_config}{reset_clr}")

        print(f"\n{magenta_clr}All_stopped_configs "
              f"[{stopped_configs_total}]:{reset_clr}")
        for cur_config in started_tlt_configs_list:
            print(f"{magenta_clr}{cur_config}{reset_clr}")

        print(f"\n{blue_clr}All_configs_data "
              f"[{all_configs_total}]:{reset_clr}")
        for cur_config in all_configs_data:
            print(f"{blue_clr}"
                  f"cur_config: {cur_config['config_name']}, "
                  f"status: {cur_config['status']}, "
                  f"is_connected: {cur_config['is_connected']}, "
                  f"is_authorised: {cur_config['is_authorised']}, "
                  f"{reset_clr}")
        return json_response
    except Exception as error:
        log_text = (f"Router TLT configs by web account [ERROR]: "
                    f"error: {error}")
        print(log_text)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=log_text)
