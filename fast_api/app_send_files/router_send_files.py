import json
from typing import List

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from starlette import status
from starlette.responses import JSONResponse

from configs.console_colors import CONSOLE_COLORS
from configs.options import (
    API_OPTIONS, TELETHON_OPTIONS, ALCHEMY_OPTIONS)
from db_postgres.postgres_conn.pgs_connection import PgsAsyncConnection
from db_postgres.postgres_conn.postgres_session import PgsAsyncSession
from db_postgres.postgres_queries.qry_get_telethon_configs_objs import (
    get_tlt_configs_objs_dict_qry)
from fast_api.app_auth.funcs_auth import (
    verify_auth_username_password)
from fast_api.app_auth.scheme_auth import (
    AuthData)
from fast_api.app_send_files.helper_send_file_by_user_id import (
    send_tg_file_by_user_id)
from fast_api.app_send_files.helper_send_file_by_username import (
    send_tg_file_by_username)
from fast_api.app_send_files.scheme_send_files import InSendFilesData
from fast_api.app_web_account.scheme_web_account import (
    InWebAccountData)
from telethon_manager.telethon_clients_manager import (
    TelethonManagerSingleton)
from telethon_manager.telethon_handlers.special_helper_client_sent_msg import (
    tlt_client_sent_msg_special_helper)
from utils_specific.get_account_tlt_clients import (
    get_acc_only_started_tlt_clients)

base_url_name = API_OPTIONS.API_BASE_URL_NAME
rtr_send_telegram_files = APIRouter(prefix=f"/{base_url_name}",
                                    tags=["TELEGRAM TLT ENDPOINTS"])

AUTH_DATA_DESCR = """
JSON string of AuthData: 
should be passed in request as
     auth_data = {"username": "some username",
                 "password": "some password"}
     auth_form = json.dumps(auth_data)
     request_form_data = {"auth_form": auth_form,
                          .....
                          "some_else_form_field": some_else_form_data}
Validation model:
class AuthData(BaseModel):
    username: str,
    password: str
"""

WEB_ACC_DESCR = """
JSON str of InWebAccountData:
should be passed in request as
     web_account_data = {"web_account_id": "some web account",
                         "web_account_username": "some acc username"}
     web_account_form = json.dumps(web_account_data)
     request_form_data = {"web_account_form": web_account_form
                          .....
                          "some_else_form_field": some_else_form_data}
Validation model:
class InWebAccountData(BaseModel):
    web_account_id: str
    web_account_username: str
"""

SEND_FILE_DESCR = """
JSON str of InSendFilesData:
should be passed in request as
     send_file_data = {"tg_username": "some tg username",
                       "tg_user_id": "some tg id",
                       "file_name": "some file name",
                       "file_type": "some file mime type"}
     send_file_form = json.dumps(send_file_data)
     request_form_data = {"send_file_form": send_file_form
                          .....
                          "some_else_form_field": some_else_form_data}
Validation model:
class InSendFilesData(BaseModel):
    tg_username: Optional[str] = ""
    tg_user_id: Optional[str] = ""
    file_name: str
    file_type: str | None = None
"""


@rtr_send_telegram_files.post("/send_telegram_files")
async def send_telegram_files_router(
        auth_form: str = Form(..., description=AUTH_DATA_DESCR),
        web_account_form: str = Form(..., description=WEB_ACC_DESCR),
        send_file_form: str = Form(..., description=SEND_FILE_DESCR),
        files: List[UploadFile] = File(...),
) -> JSONResponse:
    auth_dict = json.loads(auth_form)
    auth_data = AuthData(**auth_dict)

    await verify_auth_username_password(
        username=auth_data.username,
        password=auth_data.password)

    web_account_dict = json.loads(web_account_form)
    send_file_dict = json.loads(send_file_form)
    web_account_data = InWebAccountData(**web_account_dict)
    send_file_data = InSendFilesData(**send_file_dict)

    web_account_id = web_account_data.web_account_id
    web_account_username = web_account_data.web_account_username

    tg_username = send_file_data.tg_username
    tg_user_id = send_file_data.tg_user_id
    tg_user_id = int(tg_user_id) if tg_user_id else None

    try:
        tlt_manager = TelethonManagerSingleton()  # Singleton
        acc_only_tlt_clients = await get_acc_only_started_tlt_clients(
            telethon_manager=tlt_manager,
            web_account_id=web_account_id,
            web_account_username=web_account_username,
            skip_disconnected=True)
        account_only_configs = list(acc_only_tlt_clients.keys())

        all_sent_msg_usernames = []
        all_sent_msg_users_ids = []
        all_msg_sent_users = []
        all_sending_results = []
        all_sent_filenames = []

        sent_by_username_flag = False
        sent_by_user_id_flag = False
        msg_sent_flag = False

        sent_by_username_err = ""
        sent_by_user_id_err = ""

        if not account_only_configs:
            error_log = "Connected configs not found [ERROR]"
            all_sending_results.append({
                "tg_username": tg_username,
                "sent_by_username": sent_by_username_flag,
                "sent_by_username_error": error_log,
                "tg_user_id": tg_user_id,
                "sent_by_user_id": sent_by_user_id_flag,
                "sent_by_user_id_error": error_log,
                "cur_config_name": "Not found",
                "client_is_connected": False,
                "client_is_authorized": False,
                "messages_used": False,
                "message_sent_flag": msg_sent_flag})

        log_pgs_good_ops = ALCHEMY_OPTIONS.ALCHEMY_SESSION_OK_ACTIONS_LOGS
        pgs_conn = PgsAsyncConnection()
        async with PgsAsyncSession(engine=pgs_conn.engine,
                                   log_good_ops=log_pgs_good_ops
                                   ) as pgs_session:
            pgs_configs_data = await get_tlt_configs_objs_dict_qry(
                ongoing_session=pgs_session)

        send_msg_once_option = TELETHON_OPTIONS.ALL_TLT_CLIENTS_SEND_MSG_ONCE

        for cur_config_name, cur_tlt_client in acc_only_tlt_clients.items():
            cur_pgs_config_data = pgs_configs_data.get(cur_config_name)
            if cur_pgs_config_data:
                messages_used = cur_pgs_config_data.used_for_messages or False
            else:
                messages_used = False

            if not messages_used and TELETHON_OPTIONS.SKIP_NOT_MESSAGE_USED_CONFIGS:
                client_is_connected = cur_tlt_client.is_connected()
                client_is_authorised = await cur_tlt_client.is_user_authorized()
                error_log = "Not activated for messages configuration [ERROR]"
                all_sending_results.append({
                    "tg_username": tg_username,
                    "sent_by_username": sent_by_username_flag,
                    "sent_by_username_error": error_log,
                    "tg_user_id": tg_user_id,
                    "sent_by_user_id": sent_by_user_id_flag,
                    "sent_by_user_id_error": error_log,
                    "cur_config_name": cur_config_name,
                    "client_is_connected": client_is_connected,
                    "client_is_authorized": client_is_authorised,
                    "messages_used": messages_used,
                    "message_sent_flag": msg_sent_flag})
                continue

            for cur_file_obj in files:
                file_name = cur_file_obj.filename or None
                file_mime_type = cur_file_obj.content_type or None
                file_content = await cur_file_obj.read()

                if (tg_username and
                        (not send_msg_once_option or not msg_sent_flag)):
                    sent_msg_res = await send_tg_file_by_username(
                        telethon_client=cur_tlt_client,
                        telethon_config_name=cur_config_name,
                        username=tg_username,
                        file_name=file_name,
                        file_content=file_content,
                        file_mime_type=file_mime_type,
                        force_document=False)
                    message_obj = sent_msg_res["message_object"]
                    if message_obj:
                        all_msg_sent_users.append({"tg_username": tg_username,
                                                   "tg_user_id": tg_user_id})
                        all_sent_msg_usernames.append(tg_username)
                        all_sent_filenames.append(file_name)
                        sent_by_username_flag = True
                        msg_sent_flag = True  # As file has already been sent in any client by username

                        cur_tlt_config = tlt_manager.clients_configs[cur_config_name]
                        await tlt_client_sent_msg_special_helper(
                            message_object=message_obj,
                            telethon_config=cur_tlt_config)
                    else:
                        sent_by_username_err = sent_msg_res["message_error"]

                if (tg_user_id and
                        (not send_msg_once_option or not msg_sent_flag)):
                    sent_msg_res = await send_tg_file_by_user_id(
                        telethon_client=cur_tlt_client,
                        telethon_config_name=cur_config_name,
                        user_id=tg_user_id,
                        file_name=file_name,
                        file_content=file_content,
                        file_mime_type=file_mime_type,
                        force_document=False)
                    message_obj = sent_msg_res["message_object"]
                    if message_obj:
                        all_msg_sent_users.append({"tg_username": tg_username,
                                                   "tg_user_id": tg_user_id})
                        all_sent_msg_users_ids.append(tg_user_id)
                        all_sent_filenames.append(file_name)
                        sent_by_user_id_flag = True
                        msg_sent_flag = True  # As file has already been sent in any client by user_id

                        cur_tlt_config = tlt_manager.clients_configs[cur_config_name]
                        await tlt_client_sent_msg_special_helper(
                            message_object=message_obj,
                            telethon_config=cur_tlt_config)
                    else:
                        sent_by_user_id_err = sent_msg_res["message_error"]

            client_is_connected = cur_tlt_client.is_connected()
            client_is_authorised = await cur_tlt_client.is_user_authorized()
            all_sending_results.append({
                "tg_username": tg_username,
                "sent_by_username": sent_by_username_flag,
                "sent_by_username_error": sent_by_username_err,
                "tg_user_id": tg_user_id,
                "sent_by_user_id": sent_by_user_id_flag,
                "sent_by_user_id_error": sent_by_user_id_err,
                "cur_config_name": cur_config_name,
                "client_is_connected": client_is_authorised,
                "client_is_authorized": client_is_connected,
                "messages_used": messages_used,
                "message_sent_flag": msg_sent_flag})

            # For only unique values
            # if all_sent_msg_usernames:
            #     all_sent_msg_usernames = list(set(all_sent_msg_usernames))
            # if all_sent_msg_users_ids:
            #     all_sent_msg_users_ids = list(set(all_sent_msg_users_ids))
            # if all_sending_results:
            #     all_sending_results = list(set(all_sending_results))

            if (msg_sent_flag and
                    TELETHON_OPTIONS.ALL_TLT_CLIENTS_SEND_MSG_ONCE):
                break

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
                     "all_sent_filenames": all_sent_filenames},
            status_code=status.HTTP_200_OK)

        blue_clr = CONSOLE_COLORS.BRIGHT_BLUE
        yellow_clr = CONSOLE_COLORS.BRIGHT_YELLOW
        green_clr = CONSOLE_COLORS.BRIGHT_GREEN
        reset_clr = CONSOLE_COLORS.RESET
        magenta_clr = CONSOLE_COLORS.BRIGHT_MAGENTA
        cyan_clr = CONSOLE_COLORS.BRIGHT_CYAN
        print(f"Response.body: {json_response.body}\n"
              f"Response.status_code: {json_response.status_code}\n"
              f"username: {auth_data.username}\n"
              f"web_account_id: {web_account_id}\n"
              f"web_account_username: {web_account_username}\n"
              f"acc_only_tlt_clients: {acc_only_tlt_clients}\n"
              f"account_only_configs: {magenta_clr}{account_only_configs}{reset_clr}\n"
              f"all_sent_msg_usernames: {all_sent_msg_usernames}\n"
              f"all_sent_msg_users_ids: {all_sent_msg_users_ids}\n"
              f"all_msg_sent_users: {blue_clr}{all_msg_sent_users}{reset_clr}\n"
              f"all_sending_results: {yellow_clr}{all_sending_results}{reset_clr}\n"
              f"all_sent_filenames: {cyan_clr}{all_sent_filenames}{reset_clr}\n")
        print(f"{yellow_clr}All_sending_results:{reset_clr}")
        for cur_result in all_sending_results:
            print(f"{yellow_clr}{cur_result}{reset_clr}")
        return json_response
    except Exception as error:
        log_text = (f"Router send telegram files [ERROR]: "
                    f"error: {error}")
        print(log_text)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=log_text)
