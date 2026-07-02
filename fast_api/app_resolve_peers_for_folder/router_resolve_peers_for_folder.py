from fastapi import APIRouter

from configs.options import API_OPTIONS
from fast_api.app_auth.funcs_auth import verify_auth_username_password
from fast_api.app_auth.scheme_auth import AuthData
from fast_api.app_resolve_peers_for_folder.scheme_resolve_peers_for_folder import (
    InResolvePeersForFolderData,
    OutResolvePeersForFolderResponse,
)
from fast_api.app_telegram_folders_common.helper_telegram_folders_common import (
    get_telegram_folder_context,
    raise_telegram_folders_http_error,
    resolve_peer_refs,
)
from fast_api.app_telegram_folders_common.scheme_telegram_folders_common import (
    TGAccountTLTConfigRef,
)
from fast_api.app_web_account.scheme_web_account import InWebAccountData

rtr_resolve_peers_for_folder = APIRouter(
    prefix=f"/{API_OPTIONS.API_BASE_URL_NAME}",
    tags=["TELEGRAM TLT FOLDERS"])


@rtr_resolve_peers_for_folder.post(
    "/resolve_peers_for_folder",
    response_model=OutResolvePeersForFolderResponse)
async def resolve_peers_for_folder_router(
        auth_data: AuthData,
        web_account_data: InWebAccountData,
        tlt_config_ref: TGAccountTLTConfigRef,
        peers_data: InResolvePeersForFolderData,
) -> OutResolvePeersForFolderResponse:
    await verify_auth_username_password(auth_data.username, auth_data.password)
    try:
        client, _, account = await get_telegram_folder_context(
            web_account_data.web_account_id,
            web_account_data.web_account_username,
            tlt_config_ref.config_name)
        _, results = await resolve_peer_refs(
            client, peers_data.peers, strict=False)
        resolved_count = sum(item.resolved for item in results)
        return OutResolvePeersForFolderResponse(
            message="Telegram folder peers resolved [OK]",
            account=account,
            resolved_count=resolved_count,
            unresolved_count=len(results) - resolved_count,
            results=results)
    except Exception as error:
        raise_telegram_folders_http_error(error)
