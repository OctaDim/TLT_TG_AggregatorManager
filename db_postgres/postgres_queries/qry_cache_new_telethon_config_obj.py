from typing import Any, Dict, Union

from fastapi import HTTPException
from sqlalchemy import Row
from starlette import status

from configs.settings import ALCHEMY_OPTIONS, TELETHON_OPTIONS
from db_postgres.postgres_conn.pgs_connection import PgsAsyncConnection
from db_postgres.postgres_conn.postgres_session import PgsAsyncSession
from db_postgres.postgres_models.telethon_configs_model import (
    TelethonConfigModel)
from db_postgres.postgres_queries_utils.create_cache_new_model_object import (
    create_cache_new_model_obj_qry)


async def cache_new_telethon_config_qry(
        new_telethon_config_data: Dict[str, Union[int, str]]
) -> TelethonConfigModel | Row[tuple[Any, ...]] | None:
    pgs_conn = PgsAsyncConnection()
    async with PgsAsyncSession(engine=pgs_conn.engine,
                               log_good_ops=ALCHEMY_OPTIONS.ALCHEMY_ORM_RAW_SQL_LOGS
                               ) as pgs_sync_session:
        try:
            new_tlt_config_obj = await create_cache_new_model_obj_qry(
                ModelClassORM=TelethonConfigModel,
                ongoing_session=pgs_sync_session,
                new_data=new_telethon_config_data,
                log_new_data=TELETHON_OPTIONS.LOG_NEW_TELETHON_CONFIG_DATA)
            return new_tlt_config_obj
        except Exception as error:
            log_text = (f"Creating-caching new Telethon config data [ERROR]: "
                        f"error: {error}, "
                        f"orm_model_class: {TelethonConfigModel}, "
                        f"new_tlt_config_data: {new_telethon_config_data}")
            print(log_text)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=log_text)
