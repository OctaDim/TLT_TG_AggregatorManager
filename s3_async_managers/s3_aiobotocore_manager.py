import asyncio
from typing import Optional

from aiobotocore import session
from aiobotocore.client import AioBaseClient


class AioBotoCoreManager:
    def __init__(self, aws_access_key_id: Optional[str] = None,
                 aws_secret_access_key: Optional[str] = None,
                 endpoint_url: Optional[str] = None,
                 service_name: str = "s3",
                 region_name: Optional[str] = None,
                 # api_version=None,
                 # use_ssl: bool = True,
                 # verify=None,
                 # config=None,
                 # aws_account_id=None,
                 aws_session_token: Optional[str] = None):
        """aws_session_token: AWS session token (for temporary credentials)
           endpoint_url: Custom endpoint URL (for S3 compatible services)
           service_name: AWS service name (s3, dynamodb, sqs, etc.)"""
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.service_name = service_name
        self.region_name = region_name
        self.aws_session_token = aws_session_token
        self.endpoint_url = endpoint_url

        self._session: Optional[session.AioSession] = None
        self._client: Optional[AioBaseClient] = None
        self._lock = asyncio.Lock()

    async def __aenter__(self) -> "AioBotoCoreManager":
        await self.get_client()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

    def _get_session(self) -> session.AioSession:
        if self._session is None:
            self._session = session.get_session()
        return self._session

    async def _create_client(self) -> None:
        aws_session = self._get_session()

        client_params = {"aws_access_key_id": self.aws_access_key_id,
                         "aws_secret_access_key": self.aws_secret_access_key,
                         "endpoint_url": self.endpoint_url,
                         "service_name": self.service_name,
                         "region_name": self.region_name,
                         "aws_session_token": self.aws_session_token}
        self._client = await aws_session.create_client(**client_params).__aenter__()

    async def get_client(self) -> AioBaseClient:
        async with self._lock:
            if self._client is None:
                await self._create_client()
            return self._client

    async def close(self) -> None:
        async with self._lock:
            if self._client is not None:
                await self._client.__aexit__(None, None, None)
                self._client = None
