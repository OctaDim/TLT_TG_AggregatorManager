from typing import Optional

from pydantic import BaseModel, model_validator
from starlette import status
from starlette.exceptions import HTTPException


class S3PresignedUrlData(BaseModel):
    s3_bucket_name: str
    s3_object_key:  Optional[str] = None
    s3_url_expiration: Optional[int|float] = None
    extra_file_name:  Optional[str] = None
    custom_file_name: Optional[str] = None
    tlt_config_name: Optional[str] = None

    @model_validator(mode="before")
    def validate_fields(cls, data):
        aws_s3_bucket_name = data.get("s3_bucket_name")
        aws_s3_object_key = data.get("s3_object_key")
        extra_file_name = data.get("extra_file_name")
        custom_file_name = data.get("custom_file_name")

        valid_combin = any([aws_s3_bucket_name and aws_s3_object_key,
                            aws_s3_bucket_name and extra_file_name])

        if not valid_combin:
            error_log = (f"\nWrong parameters combination [ERROR]:\n"
                         f"Possible combinations: [aws_s3_bucket_name] AND "
                         f"([aws_s3_object_key] OR [extra_file_name])\n"
                         f"extra_file_name: {extra_file_name}\n"
                         f"custom_file_name: {custom_file_name}\n")
            print(error_log)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=error_log)
        return data
