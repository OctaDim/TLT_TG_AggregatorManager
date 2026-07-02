import time

from fastapi import APIRouter, HTTPException
from starlette import status
from telethon import types

from configs.options import API_OPTIONS
from fast_api.app_auth.funcs_auth import verify_auth_username_password
from fast_api.app_auth.scheme_auth import AuthData
from fast_api.app_get_telegram_folder_dialogs.helper_get_telegram_folder_dialogs import (
    get_matching_folder_dialogs,
)
from fast_api.app_get_telegram_folder_dialogs.scheme_get_telegram_folder_dialogs import (
    InGetTelegramFolderDialogsData,
    OutGetTelegramFolderDialogsResponse,
)
from fast_api.app_telegram_folders_common.helper_telegram_folders_common import (
    get_folder_filter,
    get_telegram_folder_context,
    raise_telegram_folders_http_error,
    serialize_folder_filter,
)
from fast_api.app_telegram_folders_common.scheme_telegram_folders_common import (
    TGAccountTLTConfigRef,
)
from fast_api.app_web_account.scheme_web_account import InWebAccountData

rtr_get_telegram_folder_dialogs = APIRouter(
    prefix=f"/{API_OPTIONS.API_BASE_URL_NAME}",
    tags=["TELEGRAM TLT FOLDERS"])


@rtr_get_telegram_folder_dialogs.post(
    "/get_telegram_folder_dialogs",
    response_model=OutGetTelegramFolderDialogsResponse)
async def get_telegram_folder_dialogs_router(
        auth_data: AuthData,
        web_account_data: InWebAccountData,
        tlt_config_ref: TGAccountTLTConfigRef,
        folder_data: InGetTelegramFolderDialogsData,
) -> OutGetTelegramFolderDialogsResponse:
    await verify_auth_username_password(auth_data.username, auth_data.password)
    request_started = time.monotonic()
    try:
        client, _, account = await get_telegram_folder_context(
            web_account_data.web_account_id,
            web_account_data.web_account_username,
            tlt_config_ref.config_name)
        filter_obj = await get_folder_filter(client, folder_data.folder_id)
        if not isinstance(filter_obj, (
                types.DialogFilter, types.DialogFilterChatlist)):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Folder does not contain a user dialog filter [ERROR]")

        dialogs, scanned_count, metrics = await get_matching_folder_dialogs(
            client=client,
            filter_obj=filter_obj,
            config_name=tlt_config_ref.config_name,
            dialogs_limit=folder_data.dialogs_limit)
        folder = await serialize_folder_filter(client, filter_obj)
        total_processing_ms = round(
            (time.monotonic() - request_started) * 1000, 3)
        return OutGetTelegramFolderDialogsResponse(
            message="Telegram folder dialogs received [OK]",
            account=account,
            folder=folder,
            dialogs_limit=folder_data.dialogs_limit,
            scanned_dialogs_count=scanned_count,
            returned_count=len(dialogs),
            membership_source="telegram_dialog_filter_snapshot",
            snapshot_source=metrics["snapshot_source"],
            snapshot_age_ms=metrics["snapshot_age_ms"],
            snapshot_wait_ms=metrics["snapshot_wait_ms"],
            snapshot_scan_ms=metrics["snapshot_scan_ms"],
            membership_filter_ms=metrics["membership_filter_ms"],
            total_processing_ms=total_processing_ms,
            dialogs=dialogs)
    except Exception as error:
        raise_telegram_folders_http_error(error)
