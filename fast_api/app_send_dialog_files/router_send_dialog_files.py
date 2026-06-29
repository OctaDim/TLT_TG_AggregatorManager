from typing import List

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from starlette import status
from starlette.responses import JSONResponse

from configs.options import API_OPTIONS
from fast_api.app_auth.funcs_auth import verify_auth_username_password
from fast_api.app_dialogs_common.helper_dialogs_common import (
    can_send_to_entity,
    get_single_account_client,
    resolve_dialog_entity,
    send_files_to_dialog_entity,
    serialize_live_message,
    validate_messenger_type,
    validate_peer_storage_type,
    validate_peer_type)
from fast_api.app_web_account.scheme_web_account import InWebAccountData
from telethon_manager.telethon_clients_manager import (
    TelethonManagerSingleton)
from telethon_manager.telethon_handlers.special_helper_client_sent_msg import (
    tlt_client_sent_msg_special_helper)

base_url_name = API_OPTIONS.API_BASE_URL_NAME
rtr_send_dialog_files = APIRouter(
    prefix=f"/{base_url_name}",
    tags=["TELEGRAM TLT DIALOGS"])


@rtr_send_dialog_files.post("/send_dialog_files")
async def send_dialog_files_router(
        auth_username: str = Form(...),
        auth_password: str = Form(...),
        web_account_id: str = Form(...),
        web_account_username: str = Form(...),
        messenger_type: str = Form("telegram"),
        config_name: str = Form(...),
        peer_id: int = Form(...),
        peer_type: str = Form(...),
        peer_storage_type: str = Form(...),
        caption_text: str = Form(""),
        files: List[UploadFile] = File(...),
) -> JSONResponse:
    await verify_auth_username_password(
        username=auth_username,
        password=auth_password)

    web_account_data = InWebAccountData(
        web_account_id=web_account_id,
        web_account_username=web_account_username)
    messenger_type = validate_messenger_type(messenger_type)
    peer_type = validate_peer_type(peer_type)
    peer_storage_type = validate_peer_storage_type(peer_storage_type)

    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="files is empty [ERROR]")

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
            "Sending file to selected dialog is not allowed [ERROR]:\n"
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

    files_data = []
    for cur_file_obj in files:
        files_data.append({
            "file_name": cur_file_obj.filename,
            "file_mime_type": cur_file_obj.content_type,
            "file_content": await cur_file_obj.read(),
        })

    sent_message_objs = await send_files_to_dialog_entity(
        telethon_client=telethon_client,
        entity_obj=entity_obj,
        files_data=files_data,
        caption_text=caption_text)

    serialized_messages = []
    for message_obj in sent_message_objs:
        await tlt_client_sent_msg_special_helper(
            message_object=message_obj,
            telethon_config=telethon_config)
        serialized_messages.append(serialize_live_message(
            config_name=config_name,
            peer_id=peer_id,
            peer_type=peer_type,
            peer_storage_type=peer_storage_type,
            message_obj=message_obj))

    response_content = {
        "message": "Dialog files sent [OK]",
        "messenger_type": messenger_type,
        "config_name": config_name,
        "peer_id": peer_id,
        "peer_type": peer_type,
        "peer_storage_type": peer_storage_type,
        "sent_messages": serialized_messages,
    }
    return JSONResponse(
        content=response_content,
        status_code=status.HTTP_200_OK)

