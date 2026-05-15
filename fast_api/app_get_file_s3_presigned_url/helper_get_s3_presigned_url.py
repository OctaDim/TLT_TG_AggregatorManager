from typing import Dict

from s3_async_managers.get_s3_client_context_func import get_s3_client


async def get_s3_storage_object(
        s3_bucket_name: str,
        s3_object_key: str | None = None,
        custom_file_name: str | None = None,
        s3_url_expiration: int | float = None,
        telethon_config_name: str = None
) -> Dict[str, str]:
    file_result = {"s3_presigned_url": "",
                   "file_name": "",
                   "file_mime_type": "",
                   "get_file_error": ""}
    try:
        async with get_s3_client() as s3_client:
            s3_presigned_url = await s3_client.generate_presigned_url(
                ClientMethod="get_object",
                Params={
                    "Bucket": s3_bucket_name,
                    "Key": s3_object_key,
                    "ResponseContentDisposition": f"attachment; "  # Optional to save forcibly
                                                  f"filename={s3_object_key}"},
                ExpiresIn=s3_url_expiration)

            s3_head_response = await s3_client.head_object(
                Bucket=s3_bucket_name,
                Key=s3_object_key)
            s3_mime_type = s3_head_response.get("ContentType",
                                                "application/octet-stream")

            file_name = custom_file_name or s3_object_key
            file_result.update({"s3_presigned_url": s3_presigned_url,
                                "file_name": file_name,
                                "file_mime_type": s3_mime_type,
                                "get_file_error": ""})
            return file_result
    except Exception as error:
        error_msg = (f"Getting AWS/S3 object presigned url [ERROR]: \n"
                     f"error: {error} \n"
                     f"s3_bucket_name: {s3_bucket_name} \n"
                     f"s3_object_key: {s3_object_key} \n"
                     f"custom_file_name: {custom_file_name} \n"
                     f"s3_url_expire_timeout: {s3_url_expiration} \n"
                     f"telethon_config_name: {telethon_config_name}\n")
        print(error_msg)
        file_result.update({"get_file_error": error_msg})
        return file_result
