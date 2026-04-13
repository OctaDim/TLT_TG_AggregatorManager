from fastapi import APIRouter, HTTPException
from starlette import status
from starlette.responses import JSONResponse

from configs.options import API_OPTIONS
from fast_api.app_auth.funcs_auth import (
    verify_auth_username_password)
from fast_api.app_auth.scheme_auth import (
    AuthData)
from fast_api.app_complete_auth_qrcode.scheme_complete_auth_qrcode import (
    InCompleteAuthQRCodeData)
from fast_api.app_web_account.scheme_web_account import InWebAccountData
from telethon_manager.telethon_clients_manager import (
    TelethonManagerSingleton)

base_url_name = API_OPTIONS.API_BASE_URL_NAME
rtr_complete_client_qrcode_auth = APIRouter(prefix=f"/{base_url_name}",
                                            tags=["TELEGRAM TLT ENDPOINTS"])


@rtr_complete_client_qrcode_auth.post("/complete_tg_client_qrcode_auth")
async def complete_tlt_client_qrcode_auth_router(
        auth_data: AuthData,
        web_account_data: InWebAccountData,
        complete_auth_data: InCompleteAuthQRCodeData
) -> JSONResponse:
    await verify_auth_username_password(
        username=auth_data.username,
        password=auth_data.password)

    web_account_id = web_account_data.web_account_id
    web_account_username = web_account_data.web_account_username

    tlt_config_name = complete_auth_data.telethon_config_name
    qr_code_url = complete_auth_data.qr_code_url
    qr_code_file_path = complete_auth_data.qr_code_file_path

    tlt_manager_client = None
    tlt_client = None
    before_sign_in_is_authorised = False
    after_sign_in_is_authorised = False
    auth_message = ""
    auth_error = ""

    try:
        tlt_manager = TelethonManagerSingleton()  # Singleton
        tlt_manager_client = tlt_manager.clients.get(tlt_config_name)
        tlt_not_started_config = tlt_manager.not_started_configs.get(tlt_config_name)

        if not tlt_manager_client and not tlt_not_started_config:
            complete_auth_msg = "QRCode Auth: Client and config not found [ERROR]:"
            json_response = JSONResponse(
                content={"complete_auth_msg": complete_auth_msg,
                         "username": auth_data.username,
                         "web_account_id": web_account_id,
                         "web_account_username": web_account_username,
                         "tlt_config_name": tlt_config_name,
                         "qr_code_url": qr_code_url,
                         "qr_code_file_path": qr_code_file_path,
                         "before_sign_in_is_authorised": before_sign_in_is_authorised,
                         "after_sign_in_is_authorised": after_sign_in_is_authorised,
                         "auth_message": auth_message,
                         "auth_error": auth_error},
                status_code=status.HTTP_200_OK)
            print(f"{complete_auth_msg}\n"
                  f"tlt_config_name: {tlt_config_name}\n"
                  f"qr_code_url: {qr_code_url}"
                  f"qr_code_file_path: {qr_code_file_path}\n"
                  f"tlt_manager_client: {tlt_manager_client}\n"
                  f"tlt_not_started_config: {tlt_not_started_config}\n")
            return json_response

        if tlt_manager_client:
            tlt_client = tlt_manager_client
        else:
            tlt_client, auth_resp = await tlt_manager.start_user_client(
                telethon_config=tlt_not_started_config,
                skip_authorisation=True)
            auth_message = auth_resp.auth_message
            auth_error = auth_resp.auth_error

        if not tlt_client:
            complete_auth_msg = "QRCode Auth: Client not found or not created [ERROR]:"
            json_response = JSONResponse(
                content={"complete_auth_msg": complete_auth_msg,
                         "username": auth_data.username,
                         "web_account_id": web_account_id,
                         "web_account_username": web_account_username,
                         "tlt_config_name": tlt_config_name,
                         "qr_code_url": qr_code_url,
                         "qr_code_file_path": qr_code_file_path,
                         "before_sign_in_is_authorised": before_sign_in_is_authorised,
                         "after_sign_in_is_authorised": after_sign_in_is_authorised,
                         "auth_message": auth_message,
                         "auth_error": auth_error},
                status_code=status.HTTP_200_OK)
            print(f"{complete_auth_msg}\n"
                  f"tlt_config_name: {tlt_config_name}\n"
                  f"qr_code_url: {qr_code_url}"
                  f"qr_code_file_path: {qr_code_file_path}\n"
                  f"tlt_manager_client: {tlt_manager_client}\n"
                  f"tlt_client: {tlt_client}\n"
                  f"auth_message: {auth_message}\n"
                  f"auth_error: {auth_error}\n")
            return json_response

        before_sign_in_is_authorised = await tlt_client.is_user_authorized()
        if before_sign_in_is_authorised:
            tlt_manager.clients[tlt_config_name] = tlt_client
            tlt_manager.not_started_configs.pop(tlt_config_name, None)
            complete_auth_msg = "QRCode Auth: Client authorised initially [OK]:"
            json_response = JSONResponse(
                content={"complete_auth_msg": complete_auth_msg,
                         "username": auth_data.username,
                         "web_account_id": web_account_id,
                         "web_account_username": web_account_username,
                         "tlt_config_name": tlt_config_name,
                         "qr_code_url": qr_code_url,
                         "qr_code_file_path": qr_code_file_path,
                         "before_sign_in_is_authorised": before_sign_in_is_authorised,
                         "after_sign_in_is_authorised": after_sign_in_is_authorised,
                         "auth_message": auth_message,
                         "auth_error": auth_error},
                status_code=status.HTTP_200_OK)
            print(f"{complete_auth_msg}\n"
                  f"tlt_config_name: {tlt_config_name}\n"
                  f"qr_code_url: {qr_code_url}"
                  f"qr_code_file_path: {qr_code_file_path}\n"
                  f"tlt_manager_client: {tlt_manager_client}\n"
                  f"tlt_client: {tlt_client}\n"
                  f"before_sign_in_is_authorised: {before_sign_in_is_authorised}\n"
                  f"auth_message: {auth_message}\n"
                  f"auth_error: {auth_error}\n")
            return json_response

        # TODO: Make client understands, that qrcode was scanned
        # qrcode_signed_in_user = await qr_code_login.wait()

        after_sign_in_is_authorised = await tlt_client.is_user_authorized()
        if after_sign_in_is_authorised:
            tlt_manager.clients[tlt_config_name] = tlt_client
            tlt_manager.not_started_configs.pop(tlt_config_name, None)
            complete_auth_msg = "QRCode Auth: Client signed in and authed by phone [OK]:"
        else:
            tlt_manager.not_started_configs.pop(tlt_config_name, None)
            complete_auth_msg = "QRCode Auth: Client signed in and NOT AUTHED by phone [OK]:"

        json_response = JSONResponse(
            content={"complete_auth_msg": complete_auth_msg,
                     "username": auth_data.username,
                     "web_account_id": web_account_id,
                     "web_account_username": web_account_username,
                     "tlt_config_name": tlt_config_name,
                     "qr_code_url": qr_code_url,
                     "qr_code_file_path": qr_code_file_path,
                     "before_sign_in_is_authorised": before_sign_in_is_authorised,
                     "after_sign_in_is_authorised": after_sign_in_is_authorised,
                     "auth_message": auth_message,
                     "auth_error": auth_error},
            status_code=status.HTTP_200_OK)
        print(f"{complete_auth_msg}"
              f"tlt_config_name: {tlt_config_name}\n"
              f"qr_code_url: {qr_code_url}"
              f"qr_code_file_path: {qr_code_file_path}\n"
              f"tlt_manager_client: {tlt_manager_client}\n"
              f"tlt_client: {tlt_client}\n"
              # TODO: How to complete authorisation by qrcode???
              # "phone_signed_in_user: {phone_signed_in_user}\n"
              f"before_sign_in_is_authorised: {before_sign_in_is_authorised}\n"
              f"after_sign_in_is_authorised: {after_sign_in_is_authorised}\n"
              f"auth_message: {auth_message}\n"
              f"auth_error: {auth_error}\n")
        return json_response
    except Exception as error:
        log_text = (
            f"Router QRCode Auth: Complete client authorisation by QRcode [ERROR]:\n"
            f"error: {error}\n"
            f"web_account_id: {web_account_id}\n"
            f"web_account_username: {web_account_username}\n"
            f"tlt_config_name: {tlt_config_name}\n"
            f"qr_code_url: {qr_code_url}\n"
            f"qr_code_file_path: {qr_code_file_path}\n"
            f"tlt_manager_client: {tlt_manager_client}\n"
            f"tlt_client: {tlt_client}\n"
            f"before_sign_in_is_authorised: {before_sign_in_is_authorised}\n"
            f"after_sign_in_is_authorised: {after_sign_in_is_authorised}\n"
            f"auth_message: {auth_message}\n"
            f"auth_error: {auth_error}\n")
        print(log_text)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=log_text)
