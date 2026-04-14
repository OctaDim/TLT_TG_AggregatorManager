from fastapi import APIRouter
from starlette import status
from starlette.responses import JSONResponse

from configs.options import API_OPTIONS, TELETHON_OPTIONS
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
rtr_complete_client_phone_auth = APIRouter(prefix=f"/{base_url_name}",
                                           tags=["TELEGRAM TLT ENDPOINTS"])


@rtr_complete_client_phone_auth.post("/complete_tg_client_phone_auth")
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

    phone_signed_in_user = None
    before_sign_in_is_authorised = False
    after_sign_in_is_authorised = False
    auth_message = ""
    auth_error = ""

    try:
        tlt_manager = TelethonManagerSingleton()  # Singleton
        tlt_manager_client = tlt_manager.clients.get(tlt_config_name)
        tlt_not_started_config = tlt_manager.not_started_configs.get(tlt_config_name)

        if not tlt_manager_client and not tlt_not_started_config:
            complete_auth_msg = "Phone Auth: Client and config not found [ERROR]:"
            json_response = JSONResponse(
                content={"complete_auth_msg": complete_auth_msg,
                         "username": auth_data.username,
                         "web_account_id": web_account_id,
                         "web_account_username": web_account_username,
                         "tlt_config_name": tlt_config_name,
                         "telegram_phone": telegram_phone,
                         "telegram_phone_code": telegram_phone_code,
                         "before_sign_in_is_authorised": before_sign_in_is_authorised,
                         "after_sign_in_is_authorised": after_sign_in_is_authorised,
                         "auth_message": auth_message,
                         "auth_error": auth_error},
                status_code=status.HTTP_200_OK)
            print(f"{complete_auth_msg}\n"
                  f"tlt_config_name: {tlt_config_name}\n"
                  f"telegram_phone: {telegram_phone}"
                  f"telegram_phone_code: {telegram_phone_code}\n"
                  f"tlt_manager_client: {tlt_manager_client}\n"
                  f"tlt_not_started_config: {tlt_not_started_config}\n")
            return json_response

        if tlt_manager_client:
            tlt_client = tlt_manager_client
        else:
            tlt_client, auth_resp = await tlt_manager.start_user_client(
                telethon_config=tlt_not_started_config,
                skip_authorisation=True,
                connect_retries=TELETHON_OPTIONS.CLIENT_CONNECT_RETRIES,
                connect_delay_sec=TELETHON_OPTIONS.CLIENT_CONNECT_DELAY_SEC)
            auth_message = auth_resp.auth_message
            auth_error = auth_resp.auth_error

        if not tlt_client:
            complete_auth_msg = "Phone Auth: Client not found or not created [ERROR]:"
            json_response = JSONResponse(
                content={"complete_auth_msg": complete_auth_msg,
                         "username": auth_data.username,
                         "web_account_id": web_account_id,
                         "web_account_username": web_account_username,
                         "tlt_config_name": tlt_config_name,
                         "telegram_phone": telegram_phone,
                         "telegram_phone_code": telegram_phone_code,
                         "before_sign_in_is_authorised": before_sign_in_is_authorised,
                         "after_sign_in_is_authorised": after_sign_in_is_authorised,
                         "auth_message": auth_message,
                         "auth_error": auth_error},
                status_code=status.HTTP_200_OK)
            print(f"{complete_auth_msg}\n"
                  f"tlt_config_name: {tlt_config_name}\n"
                  f"telegram_phone: {telegram_phone}"
                  f"telegram_phone_code: {telegram_phone_code}\n"
                  f"tlt_manager_client: {tlt_manager_client}\n"
                  f"tlt_client: {tlt_client}\n"
                  f"auth_message: {auth_message}\n"
                  f"auth_error: {auth_error}\n")
            return json_response

        before_sign_in_is_authorised = await tlt_client.is_user_authorized()
        if before_sign_in_is_authorised:
            tlt_manager.clients[tlt_config_name] = tlt_client
            tlt_manager.not_started_configs.pop(tlt_config_name, None)
            complete_auth_msg = "Phone Auth: Client authorised initially [OK]:"
            json_response = JSONResponse(
                content={"complete_auth_msg": complete_auth_msg,
                         "username": auth_data.username,
                         "web_account_id": web_account_id,
                         "web_account_username": web_account_username,
                         "tlt_config_name": tlt_config_name,
                         "telegram_phone": telegram_phone,
                         "telegram_phone_code": telegram_phone_code,
                         "before_sign_in_is_authorised": before_sign_in_is_authorised,
                         "after_sign_in_is_authorised": after_sign_in_is_authorised,
                         "auth_message": auth_message,
                         "auth_error": auth_error},
                status_code=status.HTTP_200_OK)
            print(f"{complete_auth_msg}\n"
                  f"tlt_config_name: {tlt_config_name}\n"
                  f"telegram_phone: {telegram_phone}"
                  f"telegram_phone_code: {telegram_phone_code}\n"
                  f"tlt_manager_client: {tlt_manager_client}\n"
                  f"tlt_client: {tlt_client}\n"
                  f"before_sign_in_is_authorised: {before_sign_in_is_authorised}\n"
                  f"auth_message: {auth_message}\n"
                  f"auth_error: {auth_error}\n")
            return json_response

        try:
            phone_signed_in_user = await tlt_client.sign_in(
                phone=telegram_phone,
                code=telegram_phone_code,
                password=None,
                bot_token=None,
                phone_code_hash=phone_code_hash)
        except Exception as sign_in_error:
            complete_auth_msg = (f"Phone Auth: Client sign in by phone [ERROR]: "
                                 f"sign_in_error: {sign_in_error} \n")
            json_response = JSONResponse(
                content={"complete_auth_msg": complete_auth_msg,
                         "username": auth_data.username,
                         "web_account_id": web_account_id,
                         "web_account_username": web_account_username,
                         "tlt_config_name": tlt_config_name,
                         "telegram_phone": telegram_phone,
                         "telegram_phone_code": telegram_phone_code,
                         "before_sign_in_is_authorised": before_sign_in_is_authorised,
                         "after_sign_in_is_authorised": after_sign_in_is_authorised,
                         "auth_message": auth_message,
                         "auth_error": auth_error},
                status_code=status.HTTP_200_OK)
            print(f"{complete_auth_msg}\n"
                  f"tlt_config_name: {tlt_config_name}\n"
                  f"telegram_phone: {telegram_phone}"
                  f"telegram_phone_code: {telegram_phone_code}\n"
                  f"tlt_manager_client: {tlt_manager_client}\n"
                  f"tlt_client: {tlt_client}\n"
                  f"before_sign_in_is_authorised: {before_sign_in_is_authorised}\n"
                  f"auth_message: {auth_message}\n"
                  f"auth_error: {auth_error}\n")
            return json_response

        after_sign_in_is_authorised = await tlt_client.is_user_authorized()
        if after_sign_in_is_authorised:
            tlt_manager.clients[tlt_config_name] = tlt_client
            tlt_manager.not_started_configs.pop(tlt_config_name, None)
            complete_auth_msg = "Phone Auth: Client signed in and authed by phone [OK]:"
        else:
            tlt_manager.not_started_configs.pop(tlt_config_name, None)
            complete_auth_msg = "Phone Auth: Client signed in and NOT AUTHED by phone [OK]:"

        json_response = JSONResponse(
            content={"complete_auth_msg": complete_auth_msg,
                     "username": auth_data.username,
                     "web_account_id": web_account_id,
                     "web_account_username": web_account_username,
                     "tlt_config_name": tlt_config_name,
                     "telegram_phone": telegram_phone,
                     "telegram_phone_code": telegram_phone_code,
                     "before_sign_in_is_authorised": before_sign_in_is_authorised,
                     "after_sign_in_is_authorised": after_sign_in_is_authorised,
                     "auth_message": auth_message,
                     "auth_error": auth_error},
            status_code=status.HTTP_200_OK)
        print(f"{complete_auth_msg}"
              f"tlt_config_name: {tlt_config_name}\n"
              f"telegram_phone: {telegram_phone}"
              f"telegram_phone_code: {telegram_phone_code}\n"
              f"tlt_manager_client: {tlt_manager_client}\n"
              f"tlt_client: {tlt_client}\n"
              f"phone_signed_in_user: {phone_signed_in_user}\n"
              f"before_sign_in_is_authorised: {before_sign_in_is_authorised}\n"
              f"after_sign_in_is_authorised: {after_sign_in_is_authorised}\n"
              f"auth_message: {auth_message}\n"
              f"auth_error: {auth_error}\n")
        return json_response
    except Exception as error:
        complete_auth_msg = (
            f"Router Phone Auth: Complete client auth by Phone [ERROR]: \n"
            f"error: {error}")
        json_response = JSONResponse(
            content={"complete_auth_msg": complete_auth_msg,
                     "username": auth_data.username,
                     "web_account_id": web_account_id,
                     "web_account_username": web_account_username,
                     "tlt_config_name": tlt_config_name,
                     "telegram_phone": telegram_phone,
                     "telegram_phone_code": telegram_phone_code,
                     "phone_signed_in_user": phone_signed_in_user,
                     "before_sign_in_is_authorised": before_sign_in_is_authorised,
                     "after_sign_in_is_authorised": after_sign_in_is_authorised,
                     "auth_message": auth_message,
                     "auth_error": auth_error},
            status_code=status.HTTP_200_OK)
        return json_response
