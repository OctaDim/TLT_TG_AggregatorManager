from typing import Dict, Union

import httpx
from httpx import Response

from configs.aggregator_api_urls import (
    AGGREGATOR_API_WEBHOOKS_URL)
from configs.settings import (
    AGGREGATOR_USERNAME, AGGREGATOR_PASSWORD, AGGREGATOR_API_OPTIONS)


async def send_event_data_webhook_req(
        new_event_data: Dict[str, Union[str, int, list, tuple, bytes]],
        source: str = "telegram_tlt",
        operation: str = "TelegramEvent",
        aggregator_url: str = AGGREGATOR_API_WEBHOOKS_URL
) -> Response | None:
    headers = {"Content-Type": "application/json"}

    auth_data = {"username": AGGREGATOR_USERNAME,
                 "password": AGGREGATOR_PASSWORD}

    json_data = {"auth_data": auth_data,
                 "event_data": new_event_data,
                 "source": source,
                 "operation": operation}

    try:
        async with httpx.AsyncClient() as client:
            req_timeout = AGGREGATOR_API_OPTIONS.OUTGOING_EXT_API_REQ_TIMEOUT
            response = await client.post(url=aggregator_url,
                                         headers=headers,
                                         json=json_data,
                                         timeout=req_timeout)
            response.raise_for_status()
            response_json = response.json()
            if AGGREGATOR_API_OPTIONS.LOG_EXT_AGGREGATOR_API_RESPONSE:
                print(f"Event Data Webhook request sent to external API [OK]:\n"
                      f"event_type: {new_event_data['event_type']}\n"
                      f"request code: {response}\n"
                      f"response_json: {response_json}\n")
            return response
    except httpx.TimeoutException as timeout_error:
        error_log = (f"Request timeout to External Aggregator API [ERROR]:\n"
                     f"error: {timeout_error}\n")
        print(error_log)
        # raise HTTPException(
        #     status_code=status.HTTP_408_REQUEST_TIMEOUT,
        #     detail=error_log)
        return None
    except httpx.HTTPStatusError as ext_api_error:
        error_log = (f"External Aggregator API [ERROR]:\n"
                     f"error: {ext_api_error}\n")
        print(error_log)
        # raise HTTPException(
        #     status_code=ext_api_error.response.status_code,
        #     detail=error_log)
        return None
    except Exception as error:
        json_data["auth_data"]["password"] = "***"
        tlt_bot_token = new_event_data["tlt_bot_token"]
        if tlt_bot_token:
            bot_token_info = tlt_bot_token[:10]
            json_data["event_data"]["tlt_bot_token"] = bot_token_info
        error_log = (f"Send Event data request [ERROR]:\n"
                     f"error: {error}\n"
                     f"json_data: {json_data}\n")
        print(error_log)
        # raise HTTPException(
        #     status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        #     detail=error_log)
        return None
