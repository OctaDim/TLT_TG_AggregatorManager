from typing import Dict, Union

import httpx
from fastapi import HTTPException
from httpx import Response
from starlette import status

from configs.aggregator_api_urls import (
    AGGREGATOR_API_WEBHOOKS_URL)
from configs.settings import (
    AGGREGATOR_USERNAME, AGGREGATOR_PASSWORD, AGGREGATOR_API_OPTIONS)


async def send_event_data_webhook_req(
        new_event_data: Dict[str, Union[str, int, list, tuple, bytes]],
        source: str,
        operation: str = "event data webhook",
        aggregator_url: str = AGGREGATOR_API_WEBHOOKS_URL
) -> Response:
    headers = {"Content-Type": "application/json"}

    auth_data = {"username": AGGREGATOR_USERNAME,
                 "password": AGGREGATOR_PASSWORD}

    json_data = {"auth_data": auth_data,
                 "event_data": new_event_data,
                 "source": source,
                 "operation": operation}

    async with httpx.AsyncClient() as client:
        try:
            req_timeout = AGGREGATOR_API_OPTIONS.OUTGOING_EXT_API_REQ_TIMEOUT
            response = await client.post(url=aggregator_url,
                                         headers=headers,
                                         json=json_data,
                                         timeout=req_timeout)
            response.raise_for_status()
            # response_json = response.json()
            # if PACT_API_OPTIONS.LOG_ALL_COMPANIES_REQ_RESPONSE:
            #     print(f"response_json: {response_json}")
            #
            # all_companies = response_json["data"]["companies"]
            # next_page_token = response_json["data"].get("next_page", "N/A")
            #
            # if PACT_API_OPTIONS.LOG_ALL_COMPANIES_REQ_RESPONSE:
            #     print(f"next_page_token: {next_page_token}")
            #     for cur_company in all_companies:
            #         print(f"cur_company: {cur_company}")
            return response
        except httpx.HTTPStatusError as ext_api_error:
            raise HTTPException(
                status_code=ext_api_error.response.status_code,
                detail=f"External Aggregator API [ERROR]: "
                       f"error: {ext_api_error}")
        except Exception as error:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Send Event data request [ERROR]:\n"
                       f"error: {error}\n"
                       f"json_data: {json_data}\n")
