from typing import Dict

from fastapi import HTTPException
from starlette import status

from configs.options import ALCHEMY_OPTIONS
from db_postgres.postgres_conn.pgs_connection import PgsAsyncConnection
from db_postgres.postgres_conn.postgres_session import PgsAsyncSession
from db_postgres.postgres_models.telethon_configs_model import (
    TelethonConfigModel)
from db_postgres.postgres_queries_utils.update_existing_model_objects import (
    update_existing_model_objs_qry)


async def update_telethon_active_status_qry(
        telethon_config_name: str,
        update_data: Dict[str, bool]
) -> bool | None:
    pgs_conn = PgsAsyncConnection()
    async with PgsAsyncSession(engine=pgs_conn.engine,
                               log_good_ops=ALCHEMY_OPTIONS.ALCHEMY_ORM_RAW_SQL_LOGS
                               ) as pgs_sync_session:
        filter_fields = {
            "telethon_config_name": telethon_config_name}

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
