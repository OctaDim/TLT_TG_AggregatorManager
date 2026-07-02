from fastapi import APIRouter, HTTPException
from starlette import status
from telethon import functions

from configs.options import API_OPTIONS
from fast_api.app_auth.funcs_auth import verify_auth_username_password
from fast_api.app_auth.scheme_auth import AuthData
from fast_api.app_create_telegram_folder.scheme_create_telegram_folder import (
    InCreateTelegramFolderData,
    OutCreateTelegramFolderResponse,
)
from fast_api.app_telegram_folders_common.helper_telegram_folders_common import (
    build_dialog_filter,
    get_dialog_filters,
    get_folder_filter,
    get_next_folder_id,
    get_telegram_folder_context,
    raise_telegram_folders_http_error,
    serialize_folder_filter,
)
from fast_api.app_telegram_folders_common.scheme_telegram_folders_common import (
    TGAccountTLTConfigRef,
)
from fast_api.app_web_account.scheme_web_account import InWebAccountData

rtr_create_telegram_folder = APIRouter(
    prefix=f"/{API_OPTIONS.API_BASE_URL_NAME}",
    tags=["TELEGRAM TLT FOLDERS"])


@rtr_create_telegram_folder.post(
    "/create_telegram_folder",
    response_model=OutCreateTelegramFolderResponse)
async def create_telegram_folder_router(
        auth_data: AuthData,
        web_account_data: InWebAccountData,
        tlt_config_ref: TGAccountTLTConfigRef,
        folder_data: InCreateTelegramFolderData,
) -> OutCreateTelegramFolderResponse:
    await verify_auth_username_password(auth_data.username, auth_data.password)
    try:
        client, _, account = await get_telegram_folder_context(
            web_account_data.web_account_id,
            web_account_data.web_account_username,
            tlt_config_ref.config_name)
        folder_id = folder_data.folder_id or await get_next_folder_id(client)
        filters, _ = await get_dialog_filters(client)
        if any(getattr(item, "id", None) == folder_id for item in filters):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Telegram folder ID already exists [ERROR]")
        filter_obj = await build_dialog_filter(
            client, folder_id, folder_data.folder_definition)
        await client(functions.messages.UpdateDialogFilterRequest(
            id=folder_id,
            filter=filter_obj))
        saved_filter = await get_folder_filter(client, folder_id)
        return OutCreateTelegramFolderResponse(
            message="Telegram folder created [OK]",
            account=account,
            folder=await serialize_folder_filter(client, saved_filter))
    except Exception as error:
        raise_telegram_folders_http_error(error)
