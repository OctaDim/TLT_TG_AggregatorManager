import os

from aiofiles import os as aiofiles_os
from fastapi import APIRouter, HTTPException
from starlette import status
from starlette.responses import JSONResponse, FileResponse

from configs.options import API_OPTIONS
from fast_api.app_auth.funcs_auth import (
    verify_auth_username_password)
from fast_api.app_auth.scheme_auth import (
    AuthData)
from fast_api.app_get_qrcode_image_file.scheme_get_qrcode_img_file import (
    InQRCodeImgData)
from fast_api.app_web_account.scheme_web_account import InWebAccountData

base_url_name = API_OPTIONS.API_BASE_URL_NAME
rtr_get_qrcode_image_file = APIRouter(prefix=f"/{base_url_name}",
                                      tags=["TELEGRAM TLT ENDPOINTS"])


@rtr_get_qrcode_image_file.post("/get_qrcode_image_file",
                                response_model=None)
async def get_qrcode_image_file_router(
        auth_data: AuthData,
        web_account_data: InWebAccountData,
        qrcode_img_data: InQRCodeImgData
) -> FileResponse | JSONResponse:
    await verify_auth_username_password(
        username=auth_data.username,
        password=auth_data.password)

    web_account_id = web_account_data.web_account_id
    web_account_username = web_account_data.web_account_username

    # TODO: Make creation qr code img from url, saving in memory and getting from memory directly, not from file
    qrcode_url = qrcode_img_data.qr_code_url

    qrcode_img_fpath = qrcode_img_data.qr_code_fpath
    qrcode_img_fname = os.path.basename(qrcode_img_fpath)

    try:
        qrcode_img_exists = await aiofiles_os.path.isfile(path=qrcode_img_fpath)
        if not qrcode_img_exists:
            get_qrcode_msg = (f"QRcode image file not found [ERROR]: "
                              f"{qrcode_img_fname}")
            json_response = JSONResponse(
                content={"get_qrcode_msg": get_qrcode_msg,
                         "username": auth_data.username,
                         "web_account_id": web_account_id,
                         "web_account_username": web_account_username,
                         "qrcode_img_fpath": qrcode_img_fpath,
                         "qrcode_img_fname": qrcode_img_fname,
                         "qrcode_img_exists": qrcode_img_exists},
                status_code=status.HTTP_200_OK)
            print(f"{get_qrcode_msg}\n"
                  f"qrcode_img_fpath: {qrcode_img_fpath}\n"
                  f"qrcode_img_fname: {qrcode_img_fname}"
                  f"qrcode_img_exists: {qrcode_img_exists}\n")
            return json_response

        # QRCode image exists
        file_response = FileResponse(
            path=qrcode_img_fpath,
            status_code=200,
            media_type="image/png",
            filename=qrcode_img_fname)
        return file_response
    except Exception as error:
        log_text = (
            f"Router QRCode image file [ERROR]:\n"
            f"error: {error}\n"
            f"web_account_id: {web_account_id}\n"
            f"web_account_username: {web_account_username}\n"
            f"qrcode_img_fpath: {qrcode_img_fpath}\n"
            f"qrcode_img_fname: {qrcode_img_fname}\n")
        print(log_text)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=log_text)
