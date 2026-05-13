from contextlib import asynccontextmanager
from typing import AsyncGenerator

from aiobotocore import session
from aiobotocore.client import AioBaseClient

from configs.environments import (
    S3_ACCESS_KEY, S3_SECRET_KEY, S3_REGION_NAME, S3_API_ENDPOINT,
    S3_SERVICE_NAME)


@asynccontextmanager
async def get_s3_client(
        aws_access_key_id: str,
        aws_secret_access_key: str,
        endpoint_url: str | None = None,
        service_name="s3",
        region_name: str = "us-east-1",
) -> AsyncGenerator[AioBaseClient, None]:
    """Simple S3 async context manager"""
    if aws_access_key_id is None:
        aws_access_key_id = S3_ACCESS_KEY

    if aws_secret_access_key is None:
        aws_secret_access_key = S3_SECRET_KEY

    if endpoint_url is None:
        endpoint_url = S3_API_ENDPOINT

    if service_name is None:
        service_name = S3_SERVICE_NAME

    if region_name is None:
        region_name = S3_REGION_NAME

    s3_session = await session.get_session()
    client_params = {"aws_access_key_id": aws_access_key_id,
                     "aws_secret_access_key": aws_secret_access_key,
                     "endpoint_url": endpoint_url,
                     "service_name": service_name,
                     "region_name": region_name}

    async with s3_session.create_client(**client_params) as s3_client:
        yield s3_client
