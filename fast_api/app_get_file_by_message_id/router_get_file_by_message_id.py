from fastapi import APIRouter, HTTPException
from starlette import status
from starlette.responses import JSONResponse, FileResponse

from configs.options import API_OPTIONS
from fast_api.app_auth.funcs_auth import (
    verify_auth_username_password)
from fast_api.app_auth.scheme_auth import (
    AuthData)
from fast_api.app_get_file_by_message_id.scheme_get_file_by_message_id import (
    InGetFileByMessageData)
from fast_api.app_web_account.scheme_web_account import (
    InWebAccountData)
from telethon_manager.telethon_clients_manager import (
    TelethonManagerSingleton)

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
    extra_file_name = message_file_data.extra_file_name
    print("####### message_id", message_id)
    print("####### channel_id", channel_id)
    print("####### chat_id", chat_id)
    print("####### user_id", user_id)
    print("####### extra_file_name", extra_file_name)

    try:
        tlt_manager = TelethonManagerSingleton()  # Singleton
        print("####### tlt_manager.clients", tlt_manager.clients)

        json_response = JSONResponse(content={}, status_code=200)
        return json_response

        # acc_only_tlt_clients = await get_acc_only_started_tlt_clients(
        #     telethon_manager=tlt_manager,
        #     web_account_id=web_account_id,
        #     web_account_username=web_account_username,
        #     skip_disconnected=True)
        # account_only_configs = list(acc_only_tlt_clients.keys())

        #     qrcode_img_exists = await aiofiles_os.path.isfile(path=qrcode_img_fpath)
        #     if not qrcode_img_exists:
        #         get_qrcode_msg = (f"QRcode image file not found [ERROR]: "
        #                           f"{qrcode_img_fname}")
        #         json_response = JSONResponse(
        #             content={"get_qrcode_msg": get_qrcode_msg,
        #                      "username": auth_data.username,
        #                      "web_account_id": web_account_id,
        #                      "web_account_username": web_account_username,
        #                      "qrcode_img_fpath": qrcode_img_fpath,
        #                      "qrcode_img_fname": qrcode_img_fname,
        #                      "qrcode_img_exists": qrcode_img_exists},
        #             status_code=status.HTTP_200_OK)
        #         print(f"{get_qrcode_msg}\n"
        #               f"qrcode_img_fpath: {qrcode_img_fpath}\n"
        #               f"qrcode_img_fname: {qrcode_img_fname}"
        #               f"qrcode_img_exists: {qrcode_img_exists}\n")
        #         return json_response
        #
        #     # QRCode image exists
        #     file_response = FileResponse(
        #         path=qrcode_img_fpath,
        #         status_code=200,
        #         media_type="image/png",
        #         filename=qrcode_img_fname)
        #     return file_response
    except Exception as error:
        log_text = (
            f"Router QRCode image file [ERROR]:\n"
            f"error: {error}\n"
            f"web_account_id: {web_account_id}\n"
            f"web_account_username: {web_account_username}\n"
            # f"qrcode_img_fpath: {qrcode_img_fpath}\n"
            # f"qrcode_img_fname: {qrcode_img_fname}\n"
        )
        print(log_text)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=log_text)
