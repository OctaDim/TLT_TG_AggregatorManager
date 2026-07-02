from fastapi import APIRouter

from configs.options import API_OPTIONS
from fast_api.app_auth.funcs_auth import verify_auth_username_password
from fast_api.app_auth.scheme_auth import AuthData
from fast_api.app_preview_folder_candidates.scheme_preview_folder_candidates import (
    InPreviewFolderCandidatesData,
    OutPreviewFolderCandidatesResponse,
)
from fast_api.app_telegram_folders_common.helper_telegram_folders_common import (
    get_telegram_folder_context,
    preview_folder_candidates,
    raise_telegram_folders_http_error,
)
from fast_api.app_telegram_folders_common.scheme_telegram_folders_common import (
    TGAccountTLTConfigRef,
)
from fast_api.app_web_account.scheme_web_account import InWebAccountData

rtr_preview_folder_candidates = APIRouter(
    prefix=f"/{API_OPTIONS.API_BASE_URL_NAME}",
    tags=["TELEGRAM TLT FOLDERS"])


@rtr_preview_folder_candidates.post(
    "/preview_folder_candidates",
    response_model=OutPreviewFolderCandidatesResponse)
async def preview_folder_candidates_router(
        auth_data: AuthData,
        web_account_data: InWebAccountData,
        tlt_config_ref: TGAccountTLTConfigRef,
        preview_data: InPreviewFolderCandidatesData,
) -> OutPreviewFolderCandidatesResponse:
    await verify_auth_username_password(auth_data.username, auth_data.password)
    try:
        client, _, account = await get_telegram_folder_context(
            web_account_data.web_account_id,
            web_account_data.web_account_username,
            tlt_config_ref.config_name)
        candidates = await preview_folder_candidates(
            client,
            preview_data.folder_definition,
            preview_data.dialogs_limit)
        included_count = sum(item.included for item in candidates)
        return OutPreviewFolderCandidatesResponse(
            message="Telegram folder candidates previewed [OK]",
            account=account,
            is_estimate=True,
            dialogs_limit=preview_data.dialogs_limit,
            included_count=included_count,
            excluded_count=len(candidates) - included_count,
            candidates=candidates)
    except Exception as error:
        raise_telegram_folders_http_error(error)
