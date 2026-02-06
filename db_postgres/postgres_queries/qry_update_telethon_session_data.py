from typing import Dict

from fastapi import HTTPException
from starlette import status

from configs.settings import ALCHEMY_OPTIONS
from db_postgres.postgres_conn.pgs_connection import PgsAsyncConnection
from db_postgres.postgres_conn.postgres_session import PgsAsyncSession
from db_postgres.postgres_models.telethon_configs_model import (
    TelethonConfigModel)
from db_postgres.postgres_queries_utils.update_existing_model_objects import (
    update_existing_model_objs_qry)


async def update_telethon_session_data_qry(
        telethon_config_id: int,
        web_account_id: str,
        web_account_username: str,
        telegram_phone: str,
        telegram_bot_token: str,
        update_data: Dict[str, str]
) -> bool | None:
    pgs_conn = PgsAsyncConnection()
    async with PgsAsyncSession(engine=pgs_conn.engine,
                               log_good_ops=ALCHEMY_OPTIONS.ALCHEMY_ORM_RAW_SQL_LOGS
                               ) as pgs_sync_session:
        tg_phone_filter = telegram_phone if telegram_phone else [None, ""]
        tg_bot_token_filter = telegram_bot_token if telegram_bot_token else [None, ""]
        filter_fields = {
            "id": telethon_config_id,
            "web_account_id": web_account_id,
            "web_account_username": web_account_username,
            "tg_personal_phone": tg_phone_filter,
            "tg_bot_token": tg_bot_token_filter}

        try:
            tlt_config_is_updated = await update_existing_model_objs_qry(
                ModelClassORM=TelethonConfigModel,
                ongoing_session=pgs_sync_session,
                fields_values_filter=filter_fields,
                update_data=update_data)
            if tlt_config_is_updated:
                return True
        except Exception as error:
            log_text = (f"Updating Telethon session data qry [ERROR]: "
                        f"error: {error}, "
                        f"orm_model_class: {TelethonConfigModel}, "
                        f"filter_fields: {filter_fields}")
            print(log_text)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=log_text)
