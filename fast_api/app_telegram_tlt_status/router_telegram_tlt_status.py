from fastapi import APIRouter, HTTPException
from starlette import status
from starlette.responses import JSONResponse

from configs.console_colors import CONSOLE_COLORS
from configs.settings import API_OPTIONS
from fast_api.app_auth.funcs_auth import (
    verify_tlt_auth_username_password)
from fast_api.app_auth.scheme_auth import (
    AuthData)
from telethon_manager.telethon_clients_manager import (
    TelethonManagerSingleton)

base_url_name = API_OPTIONS.API_BASE_URL_NAME
rtr_telegram_tlt_status = APIRouter(prefix=f"/{base_url_name}",
                                    tags=["TELEGRAM TLT ENDPOINTS"])


@rtr_telegram_tlt_status.post("/telegram_tlt_status")
async def telegram_tlt_status_router(
        auth_data: AuthData):
    await verify_tlt_auth_username_password(
        username=auth_data.username,
        password=auth_data.password)

    try:
        telethon_manager = TelethonManagerSingleton()  # Singleton

        telethon_clients = list(telethon_manager.clients.keys())
        running_async_tasks = list(telethon_manager.running_tasks.keys())

        json_response = JSONResponse(
            content={"message": "Telethon clients tasks status [OK]",
                     "username": auth_data.username,
                     "telethon_clients": telethon_clients,
                     "running_async_tasks": running_async_tasks},
            status_code=status.HTTP_200_OK)

        blue_clr = CONSOLE_COLORS.BRIGHT_BLUE
        yellow_clr = CONSOLE_COLORS.BRIGHT_YELLOW
        green_clr = CONSOLE_COLORS.BRIGHT_GREEN
        reset_clr = CONSOLE_COLORS.RESET
        print(f"Response.body: {json_response.body}\n"
              f"Response.status_code: {json_response.status_code}\n"
              f"username: {auth_data.username}\n"
              f"telethon_clients: {blue_clr}{telethon_clients}{reset_clr}\n"
              f"running_async_tasks: {yellow_clr}{running_async_tasks}{reset_clr}")
        return json_response
    except Exception as error:
        log_text = (f"Router Telethon clients and async tasks status [ERROR]: "
                    f"error: {error}")
        print(log_text)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=log_text)
