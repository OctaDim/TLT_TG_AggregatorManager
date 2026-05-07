import copy

from aiofiles import os as aiofiles_os
from fastapi import APIRouter, HTTPException
from starlette import status
from starlette.responses import JSONResponse, FileResponse

from configs.options import API_OPTIONS
from fast_api.app_auth.funcs_auth import (
    verify_auth_username_password)
from fast_api.app_auth.scheme_auth import (
    AuthData)
from fast_api.app_get_file_by_message_id.helper_get_file_by_message_id import (
    get_tg_file_by_message_id)
from fast_api.app_get_file_by_message_id.scheme_get_file_by_message_id import (
    InGetFileByMessageData)
from fast_api.app_web_account.scheme_web_account import (
    InWebAccountData)
from telethon_manager.telethon_clients_manager import (
    TelethonManagerSingleton)
from utils_common.correct_header_value import correct_header_str_value

base_url_name = API_OPTIONS.API_BASE_URL_NAME
rtr_get_file_by_message_id = APIRouter(prefix=f"/{base_url_name}",
                                       tags=["TELEGRAM TLT ENDPOINTS"])


@rtr_get_file_by_message_id.post("/get_file_by_message",
                                 response_model=None)
async def get_file_by_message_id_router(
        auth_data: AuthData,
        web_account_data: InWebAccountData,
        message_file_data: InGetFileByMessageData
) -> FileResponse | JSONResponse:
    await verify_auth_username_password(
        username=auth_data.username,
        password=auth_data.password)

    web_account_id = web_account_data.web_account_id
    web_account_username = web_account_data.web_account_username

    message_id = message_file_data.message_id
    channel_id = message_file_data.channel_id
    chat_id = message_file_data.chat_id
    user_id = message_file_data.user_id
    # telethon_config_name = message_file_data.telethon_config_name
    tlt_config_name = message_file_data.tlt_config_name
    extra_file_name = message_file_data.extra_file_name
    custom_file_name = message_file_data.custom_file_name

    tlt_file_path = ""
    tlt_file_name = ""
    tlt_file_mime_type = ""
    context = {"username": auth_data.username,
               "web_account_id": web_account_id,
               "web_account_username": web_account_username,
               "message_id": message_id,
               "channel_id": channel_id,
               "chat_id": chat_id,
               "user_id": user_id,
               "tlt_config_name": tlt_config_name,
               "extra_file_name": extra_file_name,
               "tlt_file_path": "",
               "tlt_file_name": "",
               "tlt_file_mime_type": ""}

    try:
        tlt_manager = TelethonManagerSingleton()  # Singleton
        tlt_client = tlt_manager.clients.get(tlt_config_name)

        if not tlt_client:
            get_file_error = (f"TLT telegram client not found [ERROR]: \n"
                              f"tlt_config_name: {tlt_config_name} \n")
            context.update({"get_file_msg": get_file_error,
                            "get_file_error": get_file_error})
            json_response = JSONResponse(
                content=context,
                status_code=status.HTTP_200_OK)
            print(get_file_error)
            return json_response

        file_owner_peer_id = channel_id or chat_id or user_id
        file_result = await get_tg_file_by_message_id(
            file_message_id=message_id,
            file_owner_peer_id=file_owner_peer_id,
            telethon_client=tlt_client,
            telethon_config_name=tlt_config_name,
            custom_file_name=custom_file_name)

        if not file_result:
            get_file_error = f"Telegram file not received [ERROR]:"
            context.update({"get_file_msg": get_file_error,
                            "get_file_error": get_file_error})
            json_response = JSONResponse(
                content=context,
                status_code=status.HTTP_200_OK)
            print(f"{get_file_error}\n"
                  f"message_id: {message_id}\n"
                  f"channel_id: {channel_id}\n"
                  f"chat_id: {chat_id}\n"
                  f"user_id: {user_id}\n"
                  f"tlt_config_name: {tlt_config_name}\n"
                  f"extra_file_name: {extra_file_name}\n"
                  f"get_file_error: {get_file_error}\n")
            return json_response

        tlt_file_path = file_result["file_path"]
        tlt_file_name = file_result["file_name"]
        tlt_file_mime_type = file_result["file_mime_type"]
        get_file_error = file_result["get_file_error"]

        if get_file_error or not tlt_file_path:
            context.update({"get_file_msg": get_file_error,
                            "get_file_error": get_file_error})
            json_response = JSONResponse(
                content=context,
                status_code=status.HTTP_200_OK)
            print(f"{get_file_error}\n"
                  f"message_id: {message_id}\n"
                  f"channel_id: {channel_id}\n"
                  f"chat_id: {chat_id}\n"
                  f"user_id: {user_id}\n"
                  f"tlt_config_name: {tlt_config_name}\n"
                  f"extra_file_name: {extra_file_name}\n"
                  f"tlt_file_path: {tlt_file_path}\n"
                  f"tlt_file_name: {tlt_file_name}\n"
                  f"tlt_file_mime_type: {tlt_file_mime_type}\n"
                  f"get_file_error: {get_file_error}\n")
            return json_response

        file_exists = await aiofiles_os.path.isfile(path=tlt_file_path)
        if not file_exists:
            get_file_error = f"Not existing file [ERROR]:"
            context.update({"get_file_msg": get_file_error,
                            "tlt_file_path": tlt_file_path,
                            "get_file_error": get_file_error})
            json_response = JSONResponse(
                content=context,
                status_code=status.HTTP_200_OK)
            print(f"{get_file_error}\n"
                  f"file_exists: {file_exists}\n"
                  f"tlt_file_path: {tlt_file_path}\n"
                  f"get_file_error: {get_file_error}")
            return json_response

        # File downloaded from message successfully and exists
        get_file_msg = "File downloaded successfully [OK]:"
        print(f"{get_file_msg}\n"
              f"tlt_file_path: {tlt_file_path}\n"
              f"tlt_file_name: {tlt_file_name}\n"
              f"tlt_file_mime_type: {tlt_file_mime_type}\n"
              f"get_file_error: {get_file_error}\n")

        file_resp_headers = copy.copy(context)
        file_resp_headers.update({
            "get_file_msg": get_file_msg,
            "tlt_file_path": tlt_file_path,
            "tlt_file_name": tlt_file_name,
            "tlt_file_mime_type": tlt_file_mime_type,
            "get_file_error": get_file_error})
        for cur_key, cur_value in file_resp_headers.items():
            right_value = correct_header_str_value(cur_value)
            file_resp_headers[cur_key] = right_value

        file_response = FileResponse(
            path=tlt_file_path,
            status_code=200,
            headers=file_resp_headers,
            media_type=tlt_file_mime_type,
            background=None,
            filename=tlt_file_name,
            stat_result=None,
            method=None,
            content_disposition_type="attachment")
        return file_response
    except Exception as error:
        log_text = (
            f"Router Get telegram file by Message ID and Peer ID [ERROR]:\n"
            f"error: {error}\n"
            f"web_account_id: {web_account_id}\n"
            f"web_account_username: {web_account_username}\n"
            f"message_id: {message_id}\n"
            f"channel_id: {channel_id}\n"
            f"chat_id: {chat_id}\n"
            f"user_id: {user_id}\n"
            f"extra_file_name: {extra_file_name}\n"
            f"tlt_config_name: {tlt_config_name}\n"
            f"tlt_file_path: {tlt_file_path}\n"
            f"tlt_file_name: {tlt_file_name}\n"
            f"tlt_file_mime_type: {tlt_file_mime_type}\n")
        print(log_text)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=log_text)
