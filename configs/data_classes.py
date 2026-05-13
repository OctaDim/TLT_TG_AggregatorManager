from dataclasses import dataclass


@dataclass(slots=True)
class S3BucketData:
    bucket_exists: bool = False
    access_allowed: bool = False
    valid_bucket: bool = False
    create_success: bool = False
    log_message: str = ""
