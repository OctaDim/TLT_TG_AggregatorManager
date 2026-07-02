from fastapi import APIRouter

from configs.options import API_OPTIONS
from fast_api.app_auth.funcs_auth import verify_auth_username_password
from fast_api.app_auth.scheme_auth import AuthData
from fast_api.app_get_telegram_folder.scheme_get_telegram_folder import (
    OutGetTelegramFolderResponse,
)
from fast_api.app_telegram_folders_common.helper_telegram_folders_common import (
    get_folder_filter,
    get_telegram_folder_context,
    raise_telegram_folders_http_error,
    serialize_folder_filter,
)
from fast_api.app_telegram_folders_common.scheme_telegram_folders_common import (
    InFolderIdData,
    TGAccountTLTConfigRef,
)
from fast_api.app_web_account.scheme_web_account import InWebAccountData

rtr_get_telegram_folder = APIRouter(
    prefix=f"/{API_OPTIONS.API_BASE_URL_NAME}",
    tags=["TELEGRAM TLT FOLDERS"])


@rtr_get_telegram_folder.post(
    "/get_telegram_folder",
    response_model=OutGetTelegramFolderResponse)
async def get_telegram_folder_router(
        auth_data: AuthData,
        web_account_data: InWebAccountData,
        tlt_config_ref: TGAccountTLTConfigRef,
        folder_data: InFolderIdData,
) -> OutGetTelegramFolderResponse:
    await verify_auth_username_password(auth_data.username, auth_data.password)
    try:
        client, _, account = await get_telegram_folder_context(
            web_account_data.web_account_id,
            web_account_data.web_account_username,
            tlt_config_ref.config_name)
        filter_obj = await get_folder_filter(client, folder_data.folder_id)
        folder = await serialize_folder_filter(client, filter_obj)
        return OutGetTelegramFolderResponse(
            message="Telegram folder received [OK]",
            account=account,
            folder=folder)
    except Exception as error:
        raise_telegram_folders_http_error(error)
