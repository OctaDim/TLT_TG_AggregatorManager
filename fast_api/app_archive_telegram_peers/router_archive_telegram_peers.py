from fastapi import APIRouter

from configs.options import API_OPTIONS
from fast_api.app_archive_telegram_peers.scheme_archive_telegram_peers import OutArchiveTelegramPeersResponse
from fast_api.app_auth.funcs_auth import verify_auth_username_password
from fast_api.app_auth.scheme_auth import AuthData
from fast_api.app_telegram_folders_common.helper_telegram_folders_common import (
    ARCHIVE_FOLDER_ID,
    edit_archive_peers,
    get_telegram_folder_context,
    raise_telegram_folders_http_error,
)
from fast_api.app_telegram_folders_common.scheme_telegram_folders_common import (
    InFolderPeersData,
    TGAccountTLTConfigRef,
)
from fast_api.app_web_account.scheme_web_account import InWebAccountData

rtr_archive_telegram_peers = APIRouter(
    prefix=f"/{API_OPTIONS.API_BASE_URL_NAME}", tags=["TELEGRAM TLT ARCHIVE"])


@rtr_archive_telegram_peers.post(
    "/archive_telegram_peers", response_model=OutArchiveTelegramPeersResponse)
async def archive_telegram_peers_router(
        auth_data: AuthData,
        web_account_data: InWebAccountData,
        tlt_config_ref: TGAccountTLTConfigRef,
        peers_data: InFolderPeersData,
) -> OutArchiveTelegramPeersResponse:
    await verify_auth_username_password(auth_data.username, auth_data.password)
    try:
        client, _, account = await get_telegram_folder_context(
            web_account_data.web_account_id,
            web_account_data.web_account_username,
            tlt_config_ref.config_name)
        peers = await edit_archive_peers(client, peers_data.peers, archived=True)
        return OutArchiveTelegramPeersResponse(
            message="Telegram peers archived [OK]",
            account=account,
            folder_id=ARCHIVE_FOLDER_ID,
            archived_count=len(peers),
            peers=peers)
    except Exception as error:
        raise_telegram_folders_http_error(error)
