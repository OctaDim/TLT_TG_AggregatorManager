from fastapi import APIRouter, HTTPException
from starlette import status
from starlette.responses import JSONResponse

from configs.options import API_OPTIONS
from fast_api.app_auth.funcs_auth import (
    verify_auth_username_password)
from fast_api.app_auth.scheme_auth import (
    AuthData)
from fast_api.app_complete_auth_phone.scheme_complete_auth_phone import (
    InCompleteAuthPhoneData)
from fast_api.app_web_account.scheme_web_account import InWebAccountData
from telethon_manager.telethon_clients_manager import (
    TelethonManagerSingleton)

base_url_name = API_OPTIONS.API_BASE_URL_NAME
rtr_complete_client_qrcode_auth = APIRouter(prefix=f"/{base_url_name}",
                                           tags=["TELEGRAM TLT ENDPOINTS"])


@rtr_complete_client_qrcode_auth.post("/complete_tg_client_qrcode_auth")
async def complete_tlt_client_phone_auth_router(
        auth_data: AuthData,
        web_account_data: InWebAccountData,
        complete_auth_data: InCompleteAuthPhoneData
) -> JSONResponse:
    await verify_auth_username_password(
        username=auth_data.username,
        password=auth_data.password)

    web_account_id = web_account_data.web_account_id
    web_account_username = web_account_data.web_account_username

    tlt_config_name = complete_auth_data.telethon_config_name
    telegram_phone = complete_auth_data.telegram_phone
    telegram_phone_code = complete_auth_data.telegram_phone_code
    phone_code_hash = complete_auth_data.phone_code_hash

    tlt_client = None
    before_sign_in_is_authorised = False
    after_sign_in_is_authorised = False

    try:
        tlt_manager = TelethonManagerSingleton()  # Singleton
        tlt_manager_client = tlt_manager.clients.get(tlt_config_name)
        tlt_not_started_config = tlt_manager.not_started_configs.get(tlt_config_name)

        if not tlt_manager_client and not tlt_not_started_config:
            json_response = JSONResponse(
                content={"message": "TLT client and TLT config not found [ERROR]:",
                         "username": auth_data.username,
                         "web_account_id": web_account_id,
                         "web_account_username": web_account_username,
                         "tlt_config_name": tlt_config_name,
                         "telegram_phone": telegram_phone,
                         "telegram_phone_code": telegram_phone_code,
                         "before_sign_in_is_authorised": before_sign_in_is_authorised,
                         "after_sign_in_is_authorised": after_sign_in_is_authorised},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
            print(f"TLT client not found [ERROR]:\n"
                  f"tlt_config_name: {tlt_config_name}\n"
                  f"telegram_phone: {telegram_phone}"
                  f"telegram_phone_code: {telegram_phone_code}\n")
            return json_response

        if tlt_manager_client:
            tlt_client = tlt_manager_client
        else:
            tlt_client, auth_resp = await tlt_manager.start_user_client(
                telethon_config=tlt_not_started_config,
                skip_authorisation=True)

        if not tlt_client:
            json_response = JSONResponse(
                content={"message": "TLT client not found or not created [ERROR]:",
                         "username": auth_data.username,
                         "web_account_id": web_account_id,
                         "web_account_username": web_account_username,
                         "tlt_config_name": tlt_config_name,
                         "telegram_phone": telegram_phone,
                         "telegram_phone_code": telegram_phone_code,
                         "before_sign_in_is_authorised": before_sign_in_is_authorised,
                         "after_sign_in_is_authorised": after_sign_in_is_authorised},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
            print(f"TLT client not found or not created [ERROR]:\n"
                  f"tlt_config_name: {tlt_config_name}\n"
                  f"telegram_phone: {telegram_phone}"
                  f"telegram_phone_code: {telegram_phone_code}\n"
                  f"tlt_client: {tlt_client}\n")
            return json_response

        before_sign_in_is_authorised = await tlt_client.is_user_authorized()
        if before_sign_in_is_authorised:
            tlt_manager.clients[tlt_config_name] = tlt_client
            tlt_manager.not_started_configs.pop(tlt_config_name, None)
            json_response = JSONResponse(
                content={"message": "TLT client authorised initially [OK]:",
                         "username": auth_data.username,
                         "web_account_id": web_account_id,
                         "web_account_username": web_account_username,
                         "tlt_config_name": tlt_config_name,
                         "telegram_phone": telegram_phone,
                         "telegram_phone_code": telegram_phone_code,
                         "before_sign_in_is_authorised": before_sign_in_is_authorised,
                         "after_sign_in_is_authorised": after_sign_in_is_authorised},
                status_code=status.HTTP_200_OK)
            print(f"TLT client authorised  initially [OK]:\n"
                  f"tlt_config_name: {tlt_config_name}\n"
                  f"telegram_phone: {telegram_phone}"
                  f"telegram_phone_code: {telegram_phone_code}\n"
                  f"tlt_client: {tlt_client}\n"
                  f"before_sign_in_is_authorised: {before_sign_in_is_authorised}\n")
            return json_response

        phone_signed_in_user = await tlt_client.sign_in(
            phone=telegram_phone,
            code=telegram_phone_code,
            password=None,
            bot_token=None,
            phone_code_hash=phone_code_hash)

        after_sign_in_is_authorised = await tlt_client.is_user_authorized()
        if after_sign_in_is_authorised:
            tlt_manager.clients[tlt_config_name] = tlt_client
            tlt_manager.not_started_configs.pop(tlt_config_name, None)
            auth_message = "TLT client signed in and authed by phone [OK]:"
        else:
            tlt_manager.not_started_configs.pop(tlt_config_name, None)
            auth_message = "TLT client signed in and NOT authed by phone [OK]:"

        json_response = JSONResponse(
            content={"message": auth_message,
                     "username": auth_data.username,
                     "web_account_id": web_account_id,
                     "web_account_username": web_account_username,
                     "tlt_config_name": tlt_config_name,
                     "telegram_phone": telegram_phone,
                     "telegram_phone_code": telegram_phone_code,
                     "before_sign_in_is_authorised": before_sign_in_is_authorised,
                     "after_sign_in_is_authorised": after_sign_in_is_authorised},
            status_code=status.HTTP_200_OK)
        print(f"{auth_message}"
              f"tlt_config_name: {tlt_config_name}\n"
              f"telegram_phone: {telegram_phone}"
              f"telegram_phone_code: {telegram_phone_code}\n"
              f"tlt_client: {tlt_client}\n"
              f"phone_signed_in_user: {phone_signed_in_user}\n"
              f"before_sign_in_is_authorised: {before_sign_in_is_authorised}\n"
              f"after_sign_in_is_authorised: {after_sign_in_is_authorised}\n")
        return json_response
    except Exception as error:
        log_text = (
            f"Router Complete authorisation by phone [ERROR]:\n"
            f"error: {error}\n"
            f"web_account_id: {web_account_id}\n"
            f"web_account_username: {web_account_username}\n"
            f"tlt_config_name: {tlt_config_name}\n"
            f"telegram_phone: {telegram_phone}\n"
            f"telegram_phone_code: {telegram_phone_code}\n"
            f"tlt_client: {tlt_client}\n"
            f"before_sign_in_is_authorised: {before_sign_in_is_authorised}\n"
            f"after_sign_in_is_authorised: {after_sign_in_is_authorised}\n")
        print(log_text)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=log_text)
