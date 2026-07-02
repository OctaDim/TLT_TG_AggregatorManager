from fastapi import APIRouter, HTTPException
from starlette import status
from telethon import functions

from configs.options import API_OPTIONS
from fast_api.app_auth.funcs_auth import verify_auth_username_password
from fast_api.app_auth.scheme_auth import AuthData
from fast_api.app_reorder_telegram_folders.scheme_reorder_telegram_folders import (
    InReorderTelegramFoldersData,
    OutReorderTelegramFoldersResponse,
)
from fast_api.app_telegram_folders_common.helper_telegram_folders_common import (
    get_dialog_filters,
    get_serialized_folders,
    get_telegram_folder_context,
    raise_telegram_folders_http_error,
)
from fast_api.app_telegram_folders_common.scheme_telegram_folders_common import (
    TGAccountTLTConfigRef,
)
from fast_api.app_web_account.scheme_web_account import InWebAccountData

rtr_reorder_telegram_folders = APIRouter(
    prefix=f"/{API_OPTIONS.API_BASE_URL_NAME}",
    tags=["TELEGRAM TLT FOLDERS"])


@rtr_reorder_telegram_folders.post(
    "/reorder_telegram_folders",
    response_model=OutReorderTelegramFoldersResponse)
async def reorder_telegram_folders_router(
        auth_data: AuthData,
        web_account_data: InWebAccountData,
        tlt_config_ref: TGAccountTLTConfigRef,
        reorder_data: InReorderTelegramFoldersData,
) -> OutReorderTelegramFoldersResponse:
    await verify_auth_username_password(auth_data.username, auth_data.password)
    try:
        client, _, account = await get_telegram_folder_context(
            web_account_data.web_account_id,
            web_account_data.web_account_username,
            tlt_config_ref.config_name)
        filters, _ = await get_dialog_filters(client)
        existing_ids = [getattr(item, "id", None) for item in filters]
        existing_ids = [item for item in existing_ids if item is not None]
        unknown_ids = set(reorder_data.folder_ids).difference(existing_ids)
        if unknown_ids:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Telegram folders were not found: %s [ERROR]" % (
                    sorted(unknown_ids),))
        final_order = reorder_data.folder_ids + [
            item for item in existing_ids if item not in reorder_data.folder_ids]
        await client(functions.messages.UpdateDialogFiltersOrderRequest(
            order=final_order))
        folders, _ = await get_serialized_folders(client)
        return OutReorderTelegramFoldersResponse(
            message="Telegram folders reordered [OK]",
            account=account,
            folder_ids=[item.folder_id for item in folders
                        if item.folder_id != 0],
            folders=folders)
    except Exception as error:
        raise_telegram_folders_http_error(error)
