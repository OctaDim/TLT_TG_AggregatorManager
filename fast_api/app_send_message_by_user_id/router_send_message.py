from fastapi import APIRouter, HTTPException
from starlette import status
from starlette.responses import JSONResponse

from configs.console_colors import CONSOLE_COLORS
from configs.settings import API_OPTIONS, TELETHON_OPTIONS
from fast_api.app_auth.funcs_auth import (
    verify_auth_username_password)
from fast_api.app_auth.scheme_auth import (
    AuthData)
from fast_api.app_send_message_by_user_id.helper_send_message import (
    send_tg_message_by_username, send_tg_message_by_user_id)
from fast_api.app_send_message_by_user_id.scheme_send_message import (
    InSendMessageData)
from fast_api.app_web_account.scheme_web_account import (
    InWebAccountData)
from telethon_manager.telethon_clients_manager import (
    TelethonManagerSingleton)
from utils_specific.get_account_tlt_clients import (
    get_account_only_tlt_clients)

base_url_name = API_OPTIONS.API_BASE_URL_NAME
rtr_send_telegram_message = APIRouter(prefix=f"/{base_url_name}",
                                      tags=["TELEGRAM TLT ENDPOINTS"])


@rtr_send_telegram_message.post("/send_telegram_message")
async def send_telegram_message_router(
        auth_data: AuthData,
        web_account_data: InWebAccountData,
        send_message_data: InSendMessageData
) -> JSONResponse:
    await verify_auth_username_password(
        username=auth_data.username,
        password=auth_data.password)

    web_account_id = web_account_data.web_account_id
    web_account_username = web_account_data.web_account_username
    # telegram_phone = web_account_data.telegram_phone
    # bot_token = web_account_data.telegram_bot_token
    # bot_token_info = bot_token[:10] if bot_token else None

    tg_username = send_message_data.tg_username
    tg_user_id = send_message_data.tg_user_id
    tg_user_id = int(tg_user_id) if tg_user_id else None
    message_text = send_message_data.message_text

    try:
        all_sent_msg_usernames = []
        all_sent_msg_users_ids = []
        all_msg_sent_users = []
        all_sending_results = []
        sent_by_username_flag = False
        sent_by_user_id_flag = False
        sent_by_username_err = ""
        sent_by_user_id_err = ""

        telethon_manager = TelethonManagerSingleton()  # Singleton
        acc_only_tlt_clients = await get_account_only_tlt_clients(
            telethon_manager=telethon_manager,
            web_account_id=web_account_id,
            web_account_username=web_account_username)
        account_only_configs = list(acc_only_tlt_clients.keys())

        for cur_config_name, cur_tlt_client in acc_only_tlt_clients.items():
            if tg_username:
                sent_msg_res = await send_tg_message_by_username(
                    telethon_client=cur_tlt_client,
                    telethon_config_name=cur_config_name,
                    username=tg_username,
                    message_text=message_text)
                message_obj = sent_msg_res["message_object"]
                if message_obj:
                    sent_by_username_flag = True
                    all_msg_sent_users.append({"tg_username": tg_username,
                                               "tg_user_id": tg_user_id})
                    all_sent_msg_usernames.append(tg_username)
                    if TELETHON_OPTIONS.ALL_TLT_CLIENTS_SEND_MSG_ONCE:
                        break  # As message has already been sent in any client by username
                else:
                    sent_by_username_err = sent_msg_res["sent_msg_error"]

            if tg_user_id:
                sent_msg_res = await send_tg_message_by_user_id(
                    telethon_client=cur_tlt_client,
                    telethon_config_name=cur_config_name,
                    user_id=tg_user_id,
                    message_text=message_text)
                message_obj = sent_msg_res["message_object"]
                if message_obj:
                    sent_by_user_id_flag = True
                    all_msg_sent_users.append({"tg_username": tg_username,
                                               "tg_user_id": tg_user_id})
                    all_sent_msg_users_ids.append(tg_user_id)
                    if TELETHON_OPTIONS.ALL_TLT_CLIENTS_SEND_MSG_ONCE:
                        break  # As message has already been sent in any client by user_id
                else:
                    sent_by_user_id_err = sent_msg_res["sent_msg_error"]

        # if all_sent_msg_usernames:
        #     all_sent_msg_usernames = list(set(all_sent_msg_usernames))
        # if all_sent_msg_users_ids:
        #     all_sent_msg_users_ids = list(set(all_sent_msg_users_ids))

        all_sending_results.append({
            "tg_username": tg_username,
            "sent_by_username": sent_by_username_flag,
            "sent_by_username_error": sent_by_username_err,
            "tg_user_id": tg_user_id,
            "sent_by_user_id": sent_by_user_id_flag,
            "sent_by_user_id_error": sent_by_user_id_err})

        json_response = JSONResponse(
            content={"message": "Telegram users ids found [OK]",
                     "username": auth_data.username,
                     "web_account_id": web_account_id,
                     "web_account_username": web_account_username,
                     "account_only_configs": account_only_configs,
                     "all_sent_msg_usernames": all_sent_msg_usernames,
                     "all_sent_msg_users_ids": all_sent_msg_users_ids,
                     "all_msg_sent_users": all_msg_sent_users,
                     "all_sending_results": all_sending_results,
                     "message_text": message_text},
            status_code=status.HTTP_200_OK)

        blue_clr = CONSOLE_COLORS.BRIGHT_BLUE
        yellow_clr = CONSOLE_COLORS.BRIGHT_YELLOW
        green_clr = CONSOLE_COLORS.BRIGHT_GREEN
        reset_clr = CONSOLE_COLORS.RESET
        magenta_clr = CONSOLE_COLORS.BRIGHT_MAGENTA
        print(f"Response.body: {json_response.body}\n"
              f"Response.status_code: {json_response.status_code}\n"
              f"username: {auth_data.username}\n"
              f"web_account_id: {web_account_id}\n"
              f"web_account_username: {web_account_username}\n"
              f"acc_only_tlt_clients: {acc_only_tlt_clients}\n"
              f"account_only_configs: {account_only_configs}\n"
              f"all_sent_msg_usernames: {green_clr}{all_sent_msg_usernames}{reset_clr}\n"
              f"all_sent_msg_users_ids: {blue_clr}{all_sent_msg_users_ids}{reset_clr}\n"
              f"all_msg_sent_users: {magenta_clr}{all_msg_sent_users}{reset_clr}\n"
              f"all_sending_results: {yellow_clr}{all_sending_results}{reset_clr}\n"
              f"message_text: \"{message_text}\"\n")
        return json_response
    except Exception as error:
        log_text = (f"Router send telegram message [ERROR]: "
                    f"error: {error}")
        print(log_text)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=log_text)
