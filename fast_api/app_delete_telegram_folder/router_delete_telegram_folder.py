from fastapi import APIRouter
from telethon import functions

from configs.options import API_OPTIONS
from fast_api.app_auth.funcs_auth import verify_auth_username_password
from fast_api.app_auth.scheme_auth import AuthData
from fast_api.app_delete_telegram_folder.scheme_delete_telegram_folder import (
    OutDeleteTelegramFolderResponse,
)
from fast_api.app_telegram_folders_common.helper_telegram_folders_common import (
    _ensure_custom_filter,
    get_dialog_filters,
    get_folder_filter,
    get_telegram_folder_context,
    raise_telegram_folders_http_error,
)
from fast_api.app_telegram_folders_common.scheme_telegram_folders_common import (
    InFolderIdData,
    TGAccountTLTConfigRef,
)
from fast_api.app_web_account.scheme_web_account import InWebAccountData

rtr_delete_telegram_folder = APIRouter(
    prefix=f"/{API_OPTIONS.API_BASE_URL_NAME}",
    tags=["TELEGRAM TLT FOLDERS"])


@rtr_delete_telegram_folder.post(
    "/delete_telegram_folder",
    response_model=OutDeleteTelegramFolderResponse)
async def delete_telegram_folder_router(
        auth_data: AuthData,
        web_account_data: InWebAccountData,
        tlt_config_ref: TGAccountTLTConfigRef,
        folder_data: InFolderIdData,
) -> OutDeleteTelegramFolderResponse:
    await verify_auth_username_password(auth_data.username, auth_data.password)
    try:
        client, _, account = await get_telegram_folder_context(
            web_account_data.web_account_id,
            web_account_data.web_account_username,
            tlt_config_ref.config_name)
        existing_filter = await get_folder_filter(client, folder_data.folder_id)
        _ensure_custom_filter(existing_filter)
        await client(functions.messages.UpdateDialogFilterRequest(
            id=folder_data.folder_id))
        filters, _ = await get_dialog_filters(client)
        deleted = not any(getattr(item, "id", None) == folder_data.folder_id
                          for item in filters)
        return OutDeleteTelegramFolderResponse(
            message="Telegram folder deleted [OK]",
            account=account,
            folder_id=folder_data.folder_id,
            deleted=deleted)
    except Exception as error:
        raise_telegram_folders_http_error(error)
