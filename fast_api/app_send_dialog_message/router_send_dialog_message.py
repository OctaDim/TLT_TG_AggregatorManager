from fastapi import APIRouter, HTTPException
from starlette import status
from starlette.responses import JSONResponse

from configs.options import API_OPTIONS
from fast_api.app_auth.funcs_auth import verify_auth_username_password
from fast_api.app_auth.scheme_auth import AuthData
from fast_api.app_dialogs_common.helper_dialogs_common import (
    can_send_to_entity,
    get_single_account_client,
    resolve_dialog_entity,
    send_text_to_dialog_entity,
    serialize_live_message,
    validate_messenger_type,
    validate_peer_storage_type,
    validate_peer_type)
from fast_api.app_send_dialog_message.scheme_send_dialog_message import (
    InSendDialogMessageData)
from fast_api.app_web_account.scheme_web_account import InWebAccountData
from telethon_manager.telethon_clients_manager import (
    TelethonManagerSingleton)
from telethon_manager.telethon_handlers.special_helper_client_sent_msg import (
    tlt_client_sent_msg_special_helper)

base_url_name = API_OPTIONS.API_BASE_URL_NAME
rtr_send_dialog_message = APIRouter(
    prefix=f"/{base_url_name}",
    tags=["TELEGRAM TLT DIALOGS"])


@rtr_send_dialog_message.post("/send_dialog_message")
async def send_dialog_message_router(
        auth_data: AuthData,
        web_account_data: InWebAccountData,
        send_dialog_message_data: InSendDialogMessageData,
) -> JSONResponse:
    await verify_auth_username_password(
        username=auth_data.username,
        password=auth_data.password)

    messenger_type = validate_messenger_type(
        send_dialog_message_data.messenger_type)
    config_name = send_dialog_message_data.config_name
    peer_id = send_dialog_message_data.peer_id
    peer_type = validate_peer_type(send_dialog_message_data.peer_type)
    peer_storage_type = validate_peer_storage_type(
        send_dialog_message_data.peer_storage_type)
    message_text = send_dialog_message_data.message_text

    telethon_manager = TelethonManagerSingleton()
    telethon_client, telethon_config = await get_single_account_client(
        telethon_manager=telethon_manager,
        web_account_id=web_account_data.web_account_id,
        web_account_username=web_account_data.web_account_username,
        config_name=config_name)
    entity_obj = await resolve_dialog_entity(
        telethon_client=telethon_client,
        peer_id=peer_id,
        peer_storage_type=peer_storage_type)

    if not can_send_to_entity(entity_obj):
        error_log = (
            "Sending message to selected dialog is not allowed [ERROR]:\n"
            "config_name: {config_name}\n"
            "peer_id: {peer_id}\n"
            "peer_type: {peer_type}\n"
        ).format(
            config_name=config_name,
            peer_id=peer_id,
            peer_type=peer_type,
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=error_log)

    message_obj = await send_text_to_dialog_entity(
        telethon_client=telethon_client,
        entity_obj=entity_obj,
        message_text=message_text)
    await tlt_client_sent_msg_special_helper(
        message_object=message_obj,
        telethon_config=telethon_config)

    response_content = {
        "message": "Dialog message sent [OK]",
        "messenger_type": messenger_type,
        "config_name": config_name,
        "peer_id": peer_id,
        "peer_type": peer_type,
        "peer_storage_type": peer_storage_type,
        "sent_message": serialize_live_message(
            config_name=config_name,
            peer_id=peer_id,
            peer_type=peer_type,
            peer_storage_type=peer_storage_type,
            message_obj=message_obj),
    }
    return JSONResponse(
        content=response_content,
        status_code=status.HTTP_200_OK)

