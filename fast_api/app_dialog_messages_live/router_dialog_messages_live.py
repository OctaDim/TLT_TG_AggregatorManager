from fastapi import APIRouter
from starlette import status
from starlette.responses import JSONResponse

from configs.options import API_OPTIONS
from fast_api.app_auth.funcs_auth import verify_auth_username_password
from fast_api.app_auth.scheme_auth import AuthData
from fast_api.app_dialog_messages_live.scheme_dialog_messages_live import (
    InDialogMessagesLiveData)
from fast_api.app_dialogs_common.helper_dialogs_common import (
    get_single_account_client,
    resolve_dialog_entity,
    serialize_live_message,
    validate_messenger_type,
    validate_peer_storage_type,
    validate_peer_type)
from fast_api.app_web_account.scheme_web_account import InWebAccountData
from telethon_manager.telethon_clients_manager import (
    TelethonManagerSingleton)

base_url_name = API_OPTIONS.API_BASE_URL_NAME
rtr_get_dialog_messages_live = APIRouter(
    prefix=f"/{base_url_name}",
    tags=["TELEGRAM TLT DIALOGS"])


@rtr_get_dialog_messages_live.post("/get_dialog_messages_live")
async def get_dialog_messages_live_router(
        auth_data: AuthData,
        web_account_data: InWebAccountData,
        dialog_request_data: InDialogMessagesLiveData,
) -> JSONResponse:
    await verify_auth_username_password(
        username=auth_data.username,
        password=auth_data.password)

    messenger_type = validate_messenger_type(
        dialog_request_data.messenger_type)
    config_name = dialog_request_data.config_name
    peer_id = dialog_request_data.peer_id
    peer_type = validate_peer_type(dialog_request_data.peer_type)
    peer_storage_type = validate_peer_storage_type(
        dialog_request_data.peer_storage_type)
    after_message_id = dialog_request_data.after_message_id
    messages_limit = dialog_request_data.messages_limit

    telethon_manager = TelethonManagerSingleton()
    telethon_client, _ = await get_single_account_client(
        telethon_manager=telethon_manager,
        web_account_id=web_account_data.web_account_id,
        web_account_username=web_account_data.web_account_username,
        config_name=config_name)
    entity_obj = await resolve_dialog_entity(
        telethon_client=telethon_client,
        peer_id=peer_id,
        peer_storage_type=peer_storage_type)

    if after_message_id:
        message_objs = await telethon_client.get_messages(
            entity=entity_obj,
            limit=messages_limit,
            min_id=after_message_id)
    else:
        message_objs = await telethon_client.get_messages(
            entity=entity_obj,
            limit=messages_limit)

    live_messages = []
    latest_message_id = after_message_id or 0
    for message_obj in reversed(list(message_objs)):
        serialized_message = serialize_live_message(
            config_name=config_name,
            peer_id=peer_id,
            peer_type=peer_type,
            peer_storage_type=peer_storage_type,
            message_obj=message_obj)
        live_messages.append(serialized_message)
        if serialized_message["message_id"]:
            latest_message_id = max(
                latest_message_id,
                serialized_message["message_id"])

    response_content = {
        "message": "Live dialog messages received [OK]",
        "messenger_type": messenger_type,
        "config_name": config_name,
        "peer_id": peer_id,
        "peer_type": peer_type,
        "peer_storage_type": peer_storage_type,
        "after_message_id": after_message_id,
        "messages_limit": messages_limit,
        "returned_count": len(live_messages),
        "latest_message_id": latest_message_id,
        "live_messages": live_messages,
    }
    return JSONResponse(
        content=response_content,
        status_code=status.HTTP_200_OK)

