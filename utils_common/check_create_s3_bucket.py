from aiobotocore.client import AioBaseClient
from botocore.exceptions import ClientError

from configs.data_classes import S3BucketData
from configs.options import TELETHON_OPTIONS


async def check_create_s3_bucket(
        s3_client: AioBaseClient,
        s3_bucket_name: str,
        s3_region_name: str = "us-east-1"
) -> S3BucketData:
    try:
        await s3_client.head_bucket(Bucket=s3_bucket_name)
        log_msg = (f"S3 Bucket already exists and access allowed [OK]:\n"
                   f"s3_bucket_name: {s3_bucket_name}\n")
        bucket_data = S3BucketData(bucket_exists=True,
                                   access_allowed=True,
                                   valid_bucket=True,
                                   log_message=log_msg)
    except ClientError as client_error:
        s3_error_code = client_error.response["Error"]["Code"]
        if s3_error_code == "404":
            error_log = (f"S3 Bucket not found [ERROR]:\n"
                         f"client_error: {client_error}\n"
                         f"s3_error_code: {s3_error_code}\n"
                         f"s3_bucket_name: {s3_bucket_name}\n")
            bucket_data = S3BucketData(bucket_exists=False,
                                       access_allowed=False,
                                       log_message=error_log)
        elif s3_error_code == "403":
            error_log = (f"S3 Bucket access denied [ERROR]:\n"
                         f"client_error: {client_error}\n"
                         f"s3_error_code: {s3_error_code}\n"
                         f"s3_bucket_name: {s3_bucket_name}\n")
            bucket_data = S3BucketData(bucket_exists=True,
                                       access_allowed=False,
                                       log_message=error_log)
        else:
            error_log = (f"S3 Client [ERROR]:\n"
                         f"client_error: {client_error}\n"
                         f"s3_error_code: {s3_error_code}\n"
                         f"s3_bucket_name: {s3_bucket_name}\n")
            bucket_data = S3BucketData(bucket_exists=False,
                                       access_allowed=False,
                                       log_message=error_log)
    except Exception as head_bucket_error:
        error_log = (f"S3 Bucket head check [ERROR]:\n"
                     f"head_bucket_error: {head_bucket_error}\n"
                     f"s3_bucket_name: {s3_bucket_name}\n")
        bucket_data = S3BucketData(bucket_exists=False,
                                   access_allowed=False,
                                   log_message=error_log)
    if TELETHON_OPTIONS.S3_LOG_BUCKET_HEAD_CHECK:
        print(bucket_data.log_message)

    if not bucket_data.bucket_exists:
        if s3_region_name == "us-east-1":
            # Region us-east-1 doesn't require LocationConstraint
            location_constraint = {}
        else:
            # Others require LocationConstraint
            location_constraint = {"LocationConstraint": s3_region_name}

        try:
            await s3_client.create_bucket(
                Bucket=s3_bucket_name,
                CreateBucketConfiguration=location_constraint)
            log_msg = (f"S3 Bucket created successfully [OK]:\n"
                       f"s3_bucket_name: {s3_bucket_name}\n"
                       f"s3_region_name: {s3_region_name}\n"
                       f"location_constraint: {location_constraint}\n")
            bucket_data = S3BucketData(bucket_exists=True,
                                       access_allowed=True,
                                       create_success=True,
                                       valid_bucket=True,
                                       log_message=log_msg)
        except (ClientError, Exception) as create_bucket_error:
            log_msg = (f"S3 Bucket creation failed [ERROR]:\n"
                       f"create_bucket_error: {create_bucket_error}\n"
                       f"s3_bucket_name: {s3_bucket_name}\n"
                       f"s3_region_name: {s3_region_name}\n"
                       f"location_constraint: {location_constraint}\n")
            bucket_data = S3BucketData(bucket_exists=False,
                                       access_allowed=False,
                                       create_success=False,
                                       log_message=log_msg)

        if TELETHON_OPTIONS.S3_LOG_BUCKET_CREATE_SUCCESS:
            print(bucket_data.log_message)

    return bucket_data
