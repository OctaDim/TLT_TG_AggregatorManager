from fastapi import APIRouter
from starlette import status
from starlette.responses import JSONResponse

from configs.options import API_OPTIONS
from fast_api.app_auth.funcs_auth import verify_auth_username_password
from fast_api.app_auth.scheme_auth import AuthData
from fast_api.app_dialogs_by_configs.scheme_dialogs_by_configs import (
    InDialogsByConfigsData)
from fast_api.app_dialogs_common.helper_dialogs_common import (
    get_allowed_started_account_clients,
    serialize_dialog_item,
    validate_messenger_type)
from fast_api.app_web_account.scheme_web_account import InWebAccountData
from telethon_manager.telethon_clients_manager import (
    TelethonManagerSingleton)

base_url_name = API_OPTIONS.API_BASE_URL_NAME
rtr_get_dialogs_by_configs = APIRouter(
    prefix=f"/{base_url_name}",
    tags=["TELEGRAM TLT DIALOGS"])


@rtr_get_dialogs_by_configs.post("/get_dialogs_by_configs")
async def get_dialogs_by_configs_router(
        auth_data: AuthData,
        web_account_data: InWebAccountData,
        dialogs_request_data: InDialogsByConfigsData,
) -> JSONResponse:
    await verify_auth_username_password(
        username=auth_data.username,
        password=auth_data.password)

    messenger_type = validate_messenger_type(
        dialogs_request_data.messenger_type)
    selected_configs = dialogs_request_data.selected_configs
    dialogs_limit_per_config = dialogs_request_data.dialogs_limit_per_config

    web_account_id = web_account_data.web_account_id
    web_account_username = web_account_data.web_account_username

    telethon_manager = TelethonManagerSingleton()
    account_clients = await get_allowed_started_account_clients(
        telethon_manager=telethon_manager,
        web_account_id=web_account_id,
        web_account_username=web_account_username,
        allowed_configs=selected_configs)

    dialogs_by_config = {}
    missing_configs = []

    for config_name in selected_configs:
        cur_tlt_client = account_clients.get(config_name)
        if not cur_tlt_client:
            dialogs_by_config[config_name] = []
            missing_configs.append(config_name)
            continue

        if not cur_tlt_client.is_connected():
            await cur_tlt_client.connect()

        cur_dialogs = []
        async for dialog_obj in cur_tlt_client.iter_dialogs(
                limit=dialogs_limit_per_config):
            cur_dialogs.append(serialize_dialog_item(
                config_name=config_name,
                dialog_obj=dialog_obj))

        dialogs_by_config[config_name] = cur_dialogs

    response_content = {
        "message": "Dialogs by configs received [OK]",
        "messenger_type": messenger_type,
        "web_account_id": web_account_id,
        "web_account_username": web_account_username,
        "selected_configs": selected_configs,
        "missing_configs": missing_configs,
        "dialogs_by_config": dialogs_by_config,
    }
    return JSONResponse(
        content=response_content,
        status_code=status.HTTP_200_OK)

