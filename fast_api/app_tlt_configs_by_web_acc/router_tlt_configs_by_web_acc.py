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
    get_account_only_tlt_clients, get_acc_only_not_started_configs)

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
        acc_only_tlt_clients = await get_account_only_tlt_clients(
            telethon_manager=telethon_manager,
            web_account_id=web_account_id,
            web_account_username=web_account_username)
        account_only_configs = list(acc_only_tlt_clients.keys())

        not_started_configs = await get_acc_only_not_started_configs(
            telethon_manager=telethon_manager,
            web_account_id=web_account_id,
            web_account_username=web_account_username)

        all_configs_data = []
        for cur_config in account_only_configs:
            all_configs_data.append({"config_name": cur_config,
                                     "status": True})
        for cur_config in not_started_configs.keys():
            all_configs_data.append({"config_name": cur_config,
                                     "status": False})

        json_response = JSONResponse(
            content={
                "message": "Telegram configurations found [OK]",
                "username": auth_data.username,
                "web_account_id": web_account_id,
                "web_account_username": web_account_username,
                "account_only_configs": account_only_configs,
                "all_configs_data": all_configs_data},
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
              f"acc_only_tlt_clients: {acc_only_tlt_clients}\n"
              f"account_only_configs: {yellow_clr}{account_only_configs}{reset_clr}\n"
              f"all_configs_data: {magenta_clr}{all_configs_data}{reset_clr}\n")
        print(f"\n{yellow_clr}All_running_configs:{reset_clr}")
        for cur_config in account_only_configs:
            print(f"{yellow_clr}{cur_config}{reset_clr}")

        print(f"\n{magenta_clr}All_configs_data:{reset_clr}")
        for cur_config in all_configs_data:
            print(f"{magenta_clr}"
                  f"cur_config: {cur_config['config_name']}, "
                  f"status: {cur_config['status']}"
                  f"{reset_clr}")
        return json_response
    except Exception as error:
        log_text = (f"Router TLT configs by web account [ERROR]: "
                    f"error: {error}")
        print(log_text)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=log_text)
