from fastapi import APIRouter

from configs.options import API_OPTIONS
from fast_api.app_auth.funcs_auth import verify_auth_username_password
from fast_api.app_auth.scheme_auth import AuthData
from fast_api.app_get_telegram_folder_dialogs.helper_get_telegram_folder_dialogs import (
    schedule_dialogs_snapshot_warmup,
)
from fast_api.app_get_telegram_folders.scheme_get_telegram_folders import (
    OutGetTelegramFoldersResponse,
)
from fast_api.app_telegram_folders_common.helper_telegram_folders_common import (
    get_serialized_folders,
    get_telegram_folder_context,
    raise_telegram_folders_http_error,
)
from fast_api.app_telegram_folders_common.scheme_telegram_folders_common import (
    TGAccountTLTConfigRef,
)
from fast_api.app_web_account.scheme_web_account import InWebAccountData

rtr_get_telegram_folders = APIRouter(
    prefix=f"/{API_OPTIONS.API_BASE_URL_NAME}",
    tags=["TELEGRAM TLT FOLDERS"])


@rtr_get_telegram_folders.post(
    "/get_telegram_folders",
    response_model=OutGetTelegramFoldersResponse)
async def get_telegram_folders_router(
        auth_data: AuthData,
        web_account_data: InWebAccountData,
        tlt_config_ref: TGAccountTLTConfigRef,
) -> OutGetTelegramFoldersResponse:
    await verify_auth_username_password(auth_data.username, auth_data.password)
    try:
        client, _, account = await get_telegram_folder_context(
            web_account_data.web_account_id,
            web_account_data.web_account_username,
            tlt_config_ref.config_name)
        schedule_dialogs_snapshot_warmup(
            client=client,
            config_name=tlt_config_ref.config_name)
        folders, tags_enabled = await get_serialized_folders(client)
        return OutGetTelegramFoldersResponse(
            message="Telegram folders received [OK]",
            account=account,
            tags_enabled=tags_enabled,
            folders=folders)
    except Exception as error:
        raise_telegram_folders_http_error(error)
