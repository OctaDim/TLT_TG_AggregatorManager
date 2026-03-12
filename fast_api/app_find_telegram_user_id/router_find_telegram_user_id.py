from fastapi import APIRouter, HTTPException
from starlette import status
from starlette.responses import JSONResponse

from configs.console_colors import CONSOLE_COLORS
from configs.settings import API_OPTIONS
from fast_api.app_auth.funcs_auth import (
    verify_auth_username_password)
from fast_api.app_auth.scheme_auth import (
    AuthData)
from fast_api.app_find_telegram_user_id.hlpr_get_user_ids_requests import (
    request_tg_users_ids_by_phone, request_tg_users_ids_by_name,
    get_tg_users_ids_by_username)
from fast_api.app_find_telegram_user_id.scheme_find_telegram_user_id import (
    InFindTgUserData)
from fast_api.app_web_account.scheme_web_account import (
    InWebAccountData)
from telethon_manager.telethon_clients_manager import (
    TelethonManagerSingleton)
from utils_specific.get_account_tlt_clients import (
    get_account_only_tlt_clients)

base_url_name = API_OPTIONS.API_BASE_URL_NAME
rtr_find_telegram_user_id = APIRouter(prefix=f"/{base_url_name}",
                                      tags=["TELEGRAM TLT ENDPOINTS"])


@rtr_find_telegram_user_id.post("/find_telegram_user_data")
async def find_telegram_user_id_router(
        auth_data: AuthData,
        web_account_data: InWebAccountData,
        user_data: InFindTgUserData
) -> JSONResponse:
    await verify_auth_username_password(
        username=auth_data.username,
        password=auth_data.password)

    web_account_id = web_account_data.web_account_id
    web_account_username = web_account_data.web_account_username
    # telegram_phone = web_account_data.telegram_phone
    # bot_token = web_account_data.telegram_bot_token
    # bot_token_info = bot_token[:10] if bot_token else None

    tg_username = user_data.tg_username
    tg_first_name = user_data.tg_first_name
    tg_last_name = user_data.tg_last_name
    tg_phone = user_data.tg_phone

    try:
        users_ids_by_username = []
        users_ids_by_phone = []
        users_ids_by_name = []
        all_found_users_ids = []

        telethon_manager = TelethonManagerSingleton()  # Singleton
        acc_only_tlt_clients = await get_account_only_tlt_clients(
            telethon_manager=telethon_manager,
            web_account_id=web_account_id,
            web_account_username=web_account_username)
        account_only_configs = list(acc_only_tlt_clients.keys())

        for cur_config_name, cur_tlt_client in acc_only_tlt_clients.items():
            if tg_username:
                users_ids_by_username = await get_tg_users_ids_by_username(
                    telethon_client=cur_tlt_client,
                    telethon_config_name=cur_config_name,
                    username=tg_username)
                if users_ids_by_username:
                    all_found_users_ids.extend(users_ids_by_username)
                    # break  # As it's exact user by username

            if tg_phone:
                users_ids_by_phone = await request_tg_users_ids_by_phone(
                    telethon_client=cur_tlt_client,
                    telethon_config_name=cur_config_name,
                    req_phone=tg_phone)
                if users_ids_by_phone:
                    all_found_users_ids.extend(users_ids_by_phone)
                    # break  # As it's exact user by phone

            # if True:
            if tg_first_name and tg_last_name:
                users_ids_by_name = await request_tg_users_ids_by_name(
                    telethon_client=cur_tlt_client,
                    telethon_config_name=cur_config_name,
                    req_first_name=tg_first_name,
                    req_last_name=tg_last_name)
                if users_ids_by_name:
                    all_found_users_ids.extend(users_ids_by_name)
                    # continue  # As it's probable and not exact user by name

        if all_found_users_ids:
            all_found_users_ids = list(set(all_found_users_ids))
        json_response = JSONResponse(
            content={"message": "Telegram users ids found [OK]",
                     "username": auth_data.username,
                     "web_account_id": web_account_id,
                     "web_account_username": web_account_username,
                     "account_only_configs": account_only_configs,
                     "users_ids_by_username": users_ids_by_username,
                     "users_ids_by_phone": users_ids_by_phone,
                     "users_ids_by_name": users_ids_by_name,
                     "all_found_users_ids": all_found_users_ids},
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
              f"account_only_configs: {account_only_configs}\n"
              f"users_ids_by_username: {magenta_clr}{users_ids_by_username}{reset_clr}\n"
              f"users_ids_by_phone: {green_clr}{users_ids_by_phone}{reset_clr}\n"
              f"users_ids_by_name: {blue_clr}{users_ids_by_name}{reset_clr}\n"
              f"all_found_users_ids: {yellow_clr}{all_found_users_ids}{reset_clr}\n")
        return json_response
    except Exception as error:
        log_text = (f"Router find telegram users ids [ERROR]: "
                    f"error: {error}")
        print(log_text)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=log_text)
