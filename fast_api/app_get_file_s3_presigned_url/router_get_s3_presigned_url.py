from fastapi import APIRouter, HTTPException
from starlette import status
from starlette.responses import JSONResponse, FileResponse

from configs.options import API_OPTIONS, TELETHON_OPTIONS
from fast_api.app_auth.funcs_auth import (
    verify_auth_username_password)
from fast_api.app_auth.scheme_auth import (
    AuthData)
from fast_api.app_get_file_s3_presigned_url.helper_get_s3_presigned_url import (
    get_s3_storage_object)
from fast_api.app_get_file_s3_presigned_url.scheme_get_s3_presigned_url import (
    S3PresignedUrlData)
from fast_api.app_web_account.scheme_web_account import (
    InWebAccountData)

base_url_name = API_OPTIONS.API_BASE_URL_NAME
rtr_get_file_from_s3_storage = APIRouter(prefix=f"/{base_url_name}",
                                         tags=["TELEGRAM TLT ENDPOINTS"])


@rtr_get_file_from_s3_storage.post("/get_s3_storage_object",
                                   response_model=None)
async def get_file_from_s3_storage_router(
        auth_data: AuthData,
        web_account_data: InWebAccountData,
        s3_presigned_url_data: S3PresignedUrlData
) -> FileResponse | JSONResponse:
    await verify_auth_username_password(
        username=auth_data.username,
        password=auth_data.password)

    web_account_id = web_account_data.web_account_id
    web_account_username = web_account_data.web_account_username

    s3_bucket_name = s3_presigned_url_data.s3_bucket_name
    s3_object_key = s3_presigned_url_data.s3_object_key
    s3_url_expiration = s3_presigned_url_data.s3_url_expiration
    extra_file_name = s3_presigned_url_data.extra_file_name
    custom_file_name = s3_presigned_url_data.custom_file_name
    tlt_config_name = s3_presigned_url_data.tlt_config_name

    s3_presigned_url = ""
    s3_file_name = ""
    s3_file_mime_type = ""
    context = {"username": auth_data.username,
               "web_account_id": web_account_id,
               "web_account_username": web_account_username,
               "tlt_config_name": tlt_config_name,
               "extra_file_name": extra_file_name,
               "get_file_msg": "",
               "s3_presigned_url": "",
               "s3_file_name": "",
               "s3_file_mime_type": "",
               "get_file_error": ""}

    s3_obj_key = s3_object_key or extra_file_name
    if s3_url_expiration:
        s3_url_expiration = s3_url_expiration
    else:
        s3_url_expiration = TELETHON_OPTIONS.S3_PRESIGNED_URL_EXPIRATION_SEC

    try:
        s3_file_result = await get_s3_storage_object(
            s3_bucket_name=s3_bucket_name,
            s3_object_key=s3_obj_key,
            s3_url_expiration=s3_url_expiration,
            custom_file_name=custom_file_name,
            telethon_config_name=tlt_config_name)

        s3_presigned_url = s3_file_result["s3_presigned_url"]
        s3_file_name = s3_file_result["file_name"]
        s3_file_mime_type = s3_file_result["file_mime_type"]
        get_file_error = s3_file_result["get_file_error"]

        if get_file_error or not s3_presigned_url:
            context.update({"get_file_msg": get_file_error,
                            "get_file_error": get_file_error})
            json_response = JSONResponse(
                content=context,
                status_code=status.HTTP_200_OK)
            print(f"{get_file_error}\n"
                  f"tlt_config_name: {tlt_config_name}\n"
                  f"s3_bucket_name: {s3_bucket_name}\n"
                  f"s3_object_key: {s3_object_key}\n"
                  f"extra_file_name: {extra_file_name}\n"
                  f"custom_file_name: {custom_file_name}\n"
                  f"s3_presigned_url: {s3_presigned_url}\n"
                  f"s3_file_name: {s3_file_name}\n"
                  f"s3_file_mime_type: {s3_file_mime_type}\n"
                  f"get_file_error: {get_file_error}\n")
            return json_response

        get_file_msg = "AWS/S3 storage object exists [OK]:"
        print(f"{get_file_msg}\n"
              f"tlt_config_name: {tlt_config_name}\n"
              f"s3_presigned_url: {s3_presigned_url}\n"
              f"s3_file_name: {s3_file_name}\n"
              f"s3_file_mime_type: {s3_file_mime_type}\n"
              f"get_file_error: {get_file_error}\n")

        context.update({"get_file_msg": get_file_msg,
                        "s3_presigned_url": s3_presigned_url,
                        "s3_file_name": s3_file_name,
                        "s3_file_mime_type": s3_file_mime_type,
                        "get_file_error": get_file_error})
        json_response = JSONResponse(
            content=context,
            status_code=status.HTTP_200_OK)
        print(f"{get_file_error}\n"
              f"tlt_config_name: {tlt_config_name}\n"
              f"s3_presigned_url: {s3_presigned_url}\n"
              f"s3_file_name: {s3_file_name}\n"
              f"s3_file_mime_type: {s3_file_mime_type}\n"
              f"get_file_error: {get_file_error}\n")
        return json_response
    except Exception as error:
        log_text = (
            f"Router Get TLT server saved file [ERROR]:\n"
            f"error: {error}\n"
            f"web_account_id: {web_account_id}\n"
            f"web_account_username: {web_account_username}\n"
            f"tlt_config_name: {tlt_config_name}\n"
            f"s3_bucket_name: {s3_bucket_name}\n"
            f"s3_object_key: {s3_object_key}\n"
            f"extra_file_name: {extra_file_name}\n"
            f"custom_file_name: {custom_file_name}\n"
            f"s3_presigned_url: {s3_presigned_url}\n"
            f"s3_file_name: {s3_file_name}\n"
            f"s3_file_mime_type: {s3_file_mime_type}\n")
        print(log_text)
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=log_text)
