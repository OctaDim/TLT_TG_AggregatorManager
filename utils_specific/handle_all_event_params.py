from typing import Dict, Any

from telethon import events, TelegramClient

from configs.aggregator_api_urls import AGGREGATOR_API_WEBHOOKS_URL
from configs.settings import TELETHON_OPTIONS, AGGREGATOR_API_OPTIONS
from telethon_manager.telethon_client_config import TelethonConfig
from utils_common.serialize_custom_json import get_only_jsonable_values
from utils_specific.event_params_detailed_log import (
    log_all_event_params)
from utils_specific.send_event_data_webhook import (
    send_event_data_webhook_req)


async def send_all_event_params(
        event: events.NewMessage.Event,
        telethon_client: TelegramClient,
        telethon_config: TelethonConfig,
        event_type: str,
        handler_additional_params: Dict[str, Any],
) -> None:
    separator = TELETHON_OPTIONS.EVENT_ATTRS_SECTION_SEPARATOR_PREFIX
    if None in (telethon_client, telethon_config):
        print(f"Deleted Telethon object(s), not handled event [ERROR]:\n"
              f"telethon_client: {telethon_client}\n"
              f"telethon_config: {telethon_config}\n")
        return

    if TELETHON_OPTIONS.LOG_ALL_EVENT_STRINGIFY_PARAMS:
        print(event.stringify())

    if telethon_config.bot_token:
        tlt_bot_token_info = telethon_config.bot_token[:10]
    else:
        tlt_bot_token_info = None

    all_event_params = {
        "event_type": event_type,
        "web_account_id": telethon_config.web_account_id,
        "web_account_username": telethon_config.web_account_username,
        "tlt_account_type": telethon_config.account_type.value,
        "tlt_phone": telethon_config.phone,
        "tlt_bot_token": tlt_bot_token_info,
        separator: ""}

    all_event_params.update(handler_additional_params)

    if TELETHON_OPTIONS.LOG_ALL_BEFORE_JSON_EVENT_PARAMS:
        await log_all_event_params(
            log_title=f"EVENT: {event_type} [PRELIMINARY]",
            event_params_dict=all_event_params)

    jsonable_event_params = await get_only_jsonable_values(
        all_values=all_event_params,
        separator=TELETHON_OPTIONS.EVENT_ATTRS_SECTION_SEPARATOR_PREFIX,
        log_invalid_json=TELETHON_OPTIONS.LOG_NON_JSON_SERIALIZABLE_OBJ)

    if TELETHON_OPTIONS.LOG_ALL_AFTER_JSON_EVENT_PARAMS:
        await log_all_event_params(
            log_title=f"EVENT: {event_type} [JSONABLE]",
            event_params_dict=jsonable_event_params)

    await send_event_data_webhook_req(
        new_event_data=jsonable_event_params,
        source=AGGREGATOR_API_OPTIONS.SOURCE_STRING_FOR_EXT_AGGREGATOR,
        operation=event_type,
        aggregator_url=AGGREGATOR_API_WEBHOOKS_URL)
