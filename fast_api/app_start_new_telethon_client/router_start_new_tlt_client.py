import asyncio

from fastapi import APIRouter, HTTPException
from starlette import status
from starlette.responses import JSONResponse

from configs.console_colors import CONSOLE_COLORS
from configs.enums import TELEGRAM_ACCOUNT_TYPE
from configs.environments import (
    TELEGRAM_OFFICIAL_APP_API_ID,
    TELEGRAM_OFFICIAL_APP_API_HASH)
from configs.options import API_OPTIONS
from db_postgres.postgres_models.telethon_configs_model import (
    TelethonConfigModel)
from db_postgres.postgres_queries.qry_cache_new_telethon_config_obj import (
    cache_new_telethon_config_qry)
from fast_api.app_auth.funcs_auth import (
    verify_auth_username_password)
from fast_api.app_auth.scheme_auth import (
    AuthData)
from fast_api.app_start_new_telethon_client.scheme_start_new_tlt_client import (
    InStartNewTelethonClient)
from fast_api.app_web_account.scheme_web_account import InWebAccountData
from telethon_manager.telethon_client_config import TelethonConfig
from telethon_manager.telethon_clients_manager import (
    TelethonManagerSingleton)

base_url_name = API_OPTIONS.API_BASE_URL_NAME
rtr_start_new_telethon_client = APIRouter(prefix=f"/{base_url_name}",
                                          tags=["TELEGRAM TLT ENDPOINTS"])


@rtr_start_new_telethon_client.post("/start_new_telegram_tlt_client")
async def start_new_telethon_client_router(
        auth_data: AuthData,
        web_account_data: InWebAccountData,
        new_client_data: InStartNewTelethonClient
) -> JSONResponse:
    await verify_auth_username_password(
        username=auth_data.username,
        password=auth_data.password)

    web_account_id = web_account_data.web_account_id
    web_account_username = web_account_data.web_account_username

    telegram_phone = new_client_data.telegram_phone
    bot_token = new_client_data.telegram_bot_token
    bot_token_info = bot_token[:10] if bot_token else None
    auth_type = new_client_data.authorisation_type

    if telegram_phone:
        account_type = TELEGRAM_ACCOUNT_TYPE.ACCOUNT
    else:
        account_type = TELEGRAM_ACCOUNT_TYPE.BOT
    account_type_str = account_type.value

    new_tlt_config_id = None
    new_config_name = None
    new_client = None

    try:
        new_tlt_config_data = {
            "web_account_id": web_account_id,
            "web_account_username": web_account_username,
            "tg_account_type": account_type_str,
            "tg_api_id": TELEGRAM_OFFICIAL_APP_API_ID,
            "tg_api_hash": TELEGRAM_OFFICIAL_APP_API_HASH,
            "tg_personal_phone": telegram_phone,
            "tg_bot_token": bot_token,
            "telethon_is_active": True,
            "authorisation_type": auth_type}

        new_tlt_config_obj: TelethonConfigModel  # just to fix Pycharm annotation warning bug
        new_tlt_config_obj = await cache_new_telethon_config_qry(
            new_telethon_config_data=new_tlt_config_data)
        new_tlt_config_id = new_tlt_config_obj.id

        tlt_manager = TelethonManagerSingleton()  # Singleton

        new_config_name = await tlt_manager.create_session_name(
            telethon_db_config_id=new_tlt_config_id,
            web_account_id=web_account_id,
            web_account_username=web_account_username,
            telegram_phone=telegram_phone,
            telegram_bot=bot_token_info,
            telethon_account_type=account_type_str)

        new_client_config = TelethonConfig(
            telethon_config_id=new_tlt_config_id,
            web_account_id=web_account_id,
            web_account_username=web_account_username,
            name=new_config_name,
            account_type=account_type,
            api_id=TELEGRAM_OFFICIAL_APP_API_ID,
            api_hash=TELEGRAM_OFFICIAL_APP_API_HASH,
            session_string=None,
            bot_token=bot_token,
            phone=telegram_phone,
            proxy=None,
            is_active=True,
            authorisation_type=auth_type)

        new_client, auth_resp = await tlt_manager.run_telethon_client(
            telethon_config=new_client_config)

        if not new_client:
            print(f"{'>' * 55}\n{'>' * 55}\n"
                  f"New Telethon client not created [ERROR]\n"
                  f"web_account_id: {web_account_id}\n"
                  f"web_account_username: {web_account_username}\n"
                  f"account_type: {account_type}\n"
                  f"account_type_str: {account_type_str}\n"
                  f"new_tlt_config_id: {new_tlt_config_id}\n"
                  f"new_config_name: {new_config_name}\n"
                  f"telegram_phone: {telegram_phone}\n"
                  f"bot_token_info: {bot_token_info}\n"
                  f"new_client: {new_client}\n")

            json_response = JSONResponse(
                content={"message": "Telethon client not created:",
                         "username": auth_data.username,
                         "web_account_id": web_account_id,
                         "web_account_username": web_account_username,
                         "account_type_str": account_type_str,
                         "new_tlt_config_id": new_tlt_config_id,
                         "new_config_name": new_config_name,
                         "telegram_phone": telegram_phone,
                         "bot_token_info": bot_token_info,
                         "new_client": new_client},
                status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
            return json_response

        print(f"{'>' * 55}\n{'>' * 55}\n"
              "New Telethon client created successfully [OK]:\n"
              f"web_account_id: {web_account_id}\n"
              f"web_account_username: {web_account_username}\n"
              f"account_type: {account_type}\n"
              f"account_type_str: {account_type_str}\n"
              f"new_tlt_config_id: {new_tlt_config_id}\n"
              f"new_config_name: {new_config_name}\n"
              f"telegram_phone: {telegram_phone}\n"
              f"telegram_phone: {telegram_phone}\n"
              f"bot_token_info: {bot_token_info}\n"
              f"new_client: {new_client}\n")

        if new_client and auth_resp.is_authorised:
            new_client_task = asyncio.create_task(
                coro=new_client.run_until_disconnected(),
                name=new_config_name,
                context=None)
            tlt_manager.running_tasks[new_config_name] = new_client_task

        tlt_manager_clients = list(tlt_manager.clients.keys())
        json_response = JSONResponse(
            content={"message": "Telethon client authorised and started:",
                     "username": auth_data.username,
                     "web_account_id": web_account_id,
                     "web_account_username": web_account_username,
                     "account_type_str": account_type_str,
                     "new_tlt_config_id": new_tlt_config_id,
                     "new_config_name": new_config_name,
                     "telegram_phone": telegram_phone,
                     "bot_token_info": bot_token_info,
                     "new_client": auth_data.username,
                     "auth_resp.is_authorised": auth_resp.is_authorised,
                     "tlt_manager_clients": tlt_manager_clients},
            status_code=status.HTTP_200_OK)

        blue_clr = CONSOLE_COLORS.BRIGHT_BLUE
        yellow_clr = CONSOLE_COLORS.BRIGHT_YELLOW
        reset_clr = CONSOLE_COLORS.RESET
        print(f"Response.body: {json_response.body}\n"
              f"Response.status_code: {json_response.status_code}\n"
              f"username: {auth_data.username}\n"
              f"web_account_id: {web_account_id}\n",
              f"web_account_username: {web_account_username}\n",
              f"account_type: {account_type}\n",
              f"new_tlt_config_id: {yellow_clr}{new_tlt_config_id}{reset_clr}\n",
              f"new_config_name: {blue_clr}{new_config_name}{reset_clr}\n",
              f"telegram_phone: {telegram_phone}\n",
              f"bot_token_info: {bot_token_info}\n",
              f"new_client: {new_client}\n",
              f"auth_resp.is_authorised: {auth_resp.is_authorised}\n",
              f"tlt_manager_clients: {tlt_manager_clients}\n")
        return json_response
    except Exception as error:
        log_text = (f"Router Start new single Telethon client [ERROR]:\n"
                    f"error: {error}\n"
                    f"web_account_id: {web_account_id}\n"
                    f"web_account_username: {web_account_username}\n"
                    f"account_type: {account_type}\n"
                    f"account_type_str: {account_type_str}\n"
                    f"new_tlt_config_id: {new_tlt_config_id}\n"
                    f"new_config_name: {new_config_name}\n"
                    f"telegram_phone: {telegram_phone}\n"
                    f"bot_token_info: {bot_token_info}\n"
                    f"new_client: {new_client}\n")
        print(log_text)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=log_text)
