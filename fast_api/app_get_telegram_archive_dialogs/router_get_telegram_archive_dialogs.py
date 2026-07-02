from fastapi import APIRouter

from configs.options import API_OPTIONS
from fast_api.app_auth.funcs_auth import verify_auth_username_password
from fast_api.app_auth.scheme_auth import AuthData
from fast_api.app_get_telegram_archive_dialogs.scheme_get_telegram_archive_dialogs import (
    InGetTelegramArchiveDialogsData,
    OutGetTelegramArchiveDialogsResponse,
)
from fast_api.app_telegram_folders_common.helper_telegram_folders_common import (
    ARCHIVE_FOLDER_ID,
    get_archive_dialogs,
    get_telegram_folder_context,
    raise_telegram_folders_http_error,
)
from fast_api.app_telegram_folders_common.scheme_telegram_folders_common import TGAccountTLTConfigRef
from fast_api.app_web_account.scheme_web_account import InWebAccountData

rtr_get_telegram_archive_dialogs = APIRouter(
    prefix=f"/{API_OPTIONS.API_BASE_URL_NAME}", tags=["TELEGRAM TLT ARCHIVE"])


@rtr_get_telegram_archive_dialogs.post(
    "/get_telegram_archive_dialogs",
    response_model=OutGetTelegramArchiveDialogsResponse)
async def get_telegram_archive_dialogs_router(
        auth_data: AuthData,
        web_account_data: InWebAccountData,
        tlt_config_ref: TGAccountTLTConfigRef,
        archive_data: InGetTelegramArchiveDialogsData,
) -> OutGetTelegramArchiveDialogsResponse:
    await verify_auth_username_password(auth_data.username, auth_data.password)
    try:
        client, _, account = await get_telegram_folder_context(
            web_account_data.web_account_id,
            web_account_data.web_account_username,
            tlt_config_ref.config_name)
        dialogs = await get_archive_dialogs(client, archive_data.dialogs_limit)
        for dialog_data in dialogs:
            dialog_data["config_name"] = tlt_config_ref.config_name
            dialog_data["peer_key"] = "%s:%s:%s" % (
                tlt_config_ref.config_name,
                dialog_data["peer_storage_type"],
                dialog_data["peer_id"])
        return OutGetTelegramArchiveDialogsResponse(
            message="Telegram archive dialogs received [OK]",
            account=account,
            folder_id=ARCHIVE_FOLDER_ID,
            dialogs_limit=archive_data.dialogs_limit,
            returned_count=len(dialogs),
            dialogs=dialogs)
    except Exception as error:
        raise_telegram_folders_http_error(error)
