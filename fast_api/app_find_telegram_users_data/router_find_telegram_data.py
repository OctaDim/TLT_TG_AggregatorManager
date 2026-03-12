from fastapi import APIRouter, HTTPException
from starlette import status
from starlette.responses import JSONResponse

from configs.console_colors import CONSOLE_COLORS
from configs.settings import API_OPTIONS, TELETHON_OPTIONS
from fast_api.app_auth.funcs_auth import (
    verify_auth_username_password)
from fast_api.app_auth.scheme_auth import (
    AuthData)
from fast_api.app_find_telegram_users_data.helper_request_tg_users_data import (
    request_tg_users_data_by_phone, request_tg_users_data_by_name,
    get_tg_users_data_by_username)
from fast_api.app_find_telegram_users_data.scheme_find_telegram_data import (
    InFindTelegramUserData)
from fast_api.app_web_account.scheme_web_account import (
    InWebAccountData)
from telethon_manager.telethon_clients_manager import (
    TelethonManagerSingleton)
from utils_specific.get_account_tlt_clients import (
    get_account_only_tlt_clients)

base_url_name = API_OPTIONS.API_BASE_URL_NAME
rtr_find_telegram_users_data = APIRouter(prefix=f"/{base_url_name}",
                                         tags=["TELEGRAM TLT ENDPOINTS"])


@rtr_find_telegram_users_data.post("/find_telegram_user_data")
async def find_telegram_users_data_router(
        auth_data: AuthData,
        web_account_data: InWebAccountData,
        user_data: InFindTelegramUserData
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
        users_by_username = []
        users_by_phone = []
        users_by_name = []
        found_users_ids = []
        found_users_usernames = []

        telethon_manager = TelethonManagerSingleton()  # Singleton
        acc_only_tlt_clients = await get_account_only_tlt_clients(
            telethon_manager=telethon_manager,
            web_account_id=web_account_id,
            web_account_username=web_account_username)
        account_only_configs = list(acc_only_tlt_clients.keys())

        for cur_config_name, cur_tlt_client in acc_only_tlt_clients.items():
            if tg_username:
                users_by_username = await get_tg_users_data_by_username(
                    telethon_client=cur_tlt_client,
                    telethon_config_name=cur_config_name,
                    username=tg_username)
                if users_by_username:
                    found_users_usernames.extend(users_by_username.keys())
                    found_users_ids.extend([usr["id"] for usr in users_by_username.values()])
                    if TELETHON_OPTIONS.USE_FIRST_FOUND_USER_FOR_ALL_TLT_CLIENTS:
                        break  # As exact user has been found in any client by username (first found only)

            if tg_phone:
                users_by_phone = await request_tg_users_data_by_phone(
                    telethon_client=cur_tlt_client,
                    telethon_config_name=cur_config_name,
                    req_phone=tg_phone)
                if users_by_phone:
                    found_users_usernames.extend(users_by_phone.keys())
                    found_users_ids.extend([usr["id"] for usr in users_by_phone.values()])
                    if TELETHON_OPTIONS.USE_FIRST_FOUND_USER_FOR_ALL_TLT_CLIENTS:
                        break  # As exact user has been found in any client by phone (first found only)
            # if True:
            if tg_first_name and tg_last_name:
                users_by_name = await request_tg_users_data_by_name(
                    telethon_client=cur_tlt_client,
                    telethon_config_name=cur_config_name,
                    req_first_name=tg_first_name,
                    req_last_name=tg_last_name)
                if users_by_name:
                    found_users_usernames.extend(users_by_name)
                    found_users_ids.extend([usr["id"] for usr in users_by_name.values()])
                    if TELETHON_OPTIONS.USE_FIRST_FOUND_USERS_BY_NAME_ALL_TLT_CLIENTS:
                        break  # Probable users has been found in any client by name (first found only)

        if found_users_usernames:
            found_users_usernames = list(set(found_users_usernames))
        if found_users_ids:
            found_users_ids = list(set(found_users_ids))

        json_response = JSONResponse(
            content={"message": "Telegram users ids found [OK]",
                     "username": auth_data.username,
                     "web_account_id": web_account_id,
                     "web_account_username": web_account_username,
                     "account_only_configs": account_only_configs,
                     "users_by_username": users_by_username,
                     "users_by_phone": users_by_phone,
                     "users_by_name": users_by_name,
                     "found_users_ids": found_users_ids,
                     "found_users_usernames": found_users_usernames},
            status_code=status.HTTP_200_OK)

        blue_clr = CONSOLE_COLORS.BRIGHT_BLUE
        yellow_clr = CONSOLE_COLORS.BRIGHT_YELLOW
        green_clr = CONSOLE_COLORS.BRIGHT_GREEN
        reset_clr = CONSOLE_COLORS.RESET
        magenta_clr = CONSOLE_COLORS.BRIGHT_MAGENTA
        cyan_clr = CONSOLE_COLORS.BRIGHT_CYAN
        print(f"Response.body: {json_response.body}\n"
              f"Response.status_code: {json_response.status_code}\n"
              f"username: {auth_data.username}\n"
              f"web_account_id: {web_account_id}\n"
              f"web_account_username: {web_account_username}\n"
              f"acc_only_tlt_clients: {acc_only_tlt_clients}\n"
              f"account_only_configs: {account_only_configs}\n"
              f"users_by_username: {magenta_clr}{users_by_username}{reset_clr}\n"
              f"users_by_phone: {green_clr}{users_by_phone}{reset_clr}\n"
              f"users_by_name: {blue_clr}{users_by_name}{reset_clr}\n"
              f"found_users_ids: {cyan_clr}{found_users_ids}{reset_clr}\n"
              f"found_users_usernames: {yellow_clr}{found_users_usernames}{reset_clr}\n")
        return json_response
    except Exception as error:
        log_text = (f"Router find telegram users ids [ERROR]: "
                    f"error: {error}")
        print(log_text)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=log_text)
