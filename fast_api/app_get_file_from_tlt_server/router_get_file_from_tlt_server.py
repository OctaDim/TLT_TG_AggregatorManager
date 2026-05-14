import copy

from fastapi import APIRouter, HTTPException
from starlette import status
from starlette.responses import JSONResponse, FileResponse

from configs.options import API_OPTIONS
from fast_api.app_auth.funcs_auth import (
    verify_auth_username_password)
from fast_api.app_auth.scheme_auth import (
    AuthData)
from fast_api.app_get_file_from_tlt_server.helper_get_file_from_tlt_server import (
    get_tlt_server_saved_file)
from fast_api.app_get_file_from_tlt_server.scheme_get_file_from_tlt_server import (
    InTltServerFileData)
from fast_api.app_web_account.scheme_web_account import (
    InWebAccountData)
from utils_common.correct_header_value import correct_header_str_value

base_url_name = API_OPTIONS.API_BASE_URL_NAME
rtr_get_file_from_tlt_server = APIRouter(prefix=f"/{base_url_name}",
                                         tags=["TELEGRAM TLT ENDPOINTS"])


@rtr_get_file_from_tlt_server.post("/get_tlt_server_file",
                                   response_model=None)
async def get_file_from_tlt_server_router(
        auth_data: AuthData,
        web_account_data: InWebAccountData,
        tlt_server_file_data: InTltServerFileData
) -> FileResponse | JSONResponse:
    await verify_auth_username_password(
        username=auth_data.username,
        password=auth_data.password)

    web_account_id = web_account_data.web_account_id
    web_account_username = web_account_data.web_account_username

    extra_file_name = tlt_server_file_data.extra_file_name
    custom_file_name = tlt_server_file_data.custom_file_name
    tlt_config_name = tlt_server_file_data.tlt_config_name

    tlt_file_path = ""
    tlt_file_name = ""
    tlt_file_mime_type = ""
    context = {"username": auth_data.username,
               "web_account_id": web_account_id,
               "web_account_username": web_account_username,
               "message_id": None,
               "channel_id": None,
               "chat_id": None,
               "user_id": None,
               "tlt_config_name": tlt_config_name,
               "extra_file_name": extra_file_name,
               "get_file_msg": "",
               "tlt_file_path": "",
               "tlt_file_name": "",
               "tlt_file_mime_type": "",
               "get_file_error": ""}

    try:
        file_result = await get_tlt_server_saved_file(
            extra_file_name=extra_file_name,
            custom_file_name=custom_file_name,
            telethon_config_name=tlt_config_name)

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
                  f"tlt_config_name: {tlt_config_name}\n"
                  f"extra_file_name: {extra_file_name}\n"
                  f"tlt_file_path: {tlt_file_path}\n"
                  f"tlt_file_name: {tlt_file_name}\n"
                  f"tlt_file_mime_type: {tlt_file_mime_type}\n"
                  f"get_file_error: {get_file_error}\n")
            return json_response

        get_file_msg = "TLT server saved file exists [OK]:"
        print(f"{get_file_msg}\n"
              f"tlt_file_path: {tlt_file_path}\n"
              f"tlt_file_name: {tlt_file_name}\n"
              f"tlt_file_mime_type: {tlt_file_mime_type}\n"
              f"get_file_error: {get_file_error}\n")

        file_resp_data = copy.copy(context)  # Attention: Web/proxy servers allowed not more 4-8 kb
        file_resp_data.update({
            "get_file_msg": get_file_msg,
            "tlt_file_path": tlt_file_path,
            "tlt_file_name": tlt_file_name,
            "tlt_file_mime_type": tlt_file_mime_type,
            "get_file_error": get_file_error})
        custom_resp_headers = {}
        for cur_key, cur_value in file_resp_data.items():
            right_value = correct_header_str_value(cur_value)
            new_x_header_key = f"X-TLT-{cur_key}"  # Valid custom headers key
            custom_resp_headers[new_x_header_key] = right_value

        file_response = FileResponse(
            path=tlt_file_path,
            status_code=200,
            headers=custom_resp_headers,
            media_type=tlt_file_mime_type,
            background=None,
            filename=tlt_file_name,
            stat_result=None,
            method=None,
            content_disposition_type="attachment")
        return file_response
    except Exception as error:
        log_text = (
            f"Router Get TLT server saved file [ERROR]:\n"
            f"error: {error}\n"
            f"web_account_id: {web_account_id}\n"
            f"web_account_username: {web_account_username}\n"
            f"extra_file_name: {extra_file_name}\n"
            f"tlt_config_name: {tlt_config_name}\n"
            f"tlt_file_path: {tlt_file_path}\n"
            f"tlt_file_name: {tlt_file_name}\n"
            f"tlt_file_mime_type: {tlt_file_mime_type}\n")
        print(log_text)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=log_text)
