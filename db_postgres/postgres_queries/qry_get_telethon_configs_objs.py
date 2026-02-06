from typing import List

from sqlalchemy import Row
from sqlalchemy.ext.asyncio import AsyncSession

from db_postgres.postgres_models.telethon_configs_model import (
    TelethonConfigModel)
from db_postgres.postgres_queries_utils.get_model_records_flex_query import (
    get_model_rows_flex_query)


async def get_telethon_configs_objs_qry(
        ongoing_session: AsyncSession,
) -> List[Row]:
    """Returns list of dicts with Telethon clients configurations"""
    filter_fields = {"active": True}
    telethon_configs_objs = await get_model_rows_flex_query(
        orm_model_class=TelethonConfigModel,
        ongoing_session=ongoing_session,
        selected_fields=None,
        fields_values_filter=filter_fields,
        order_by_fields="id",
        return_scalars=True)
    # print(f"####### telethon_configs_objs: {telethon_configs_objs}")  # Too long
    print(f"####### type(telethon_configs_objs): {type(telethon_configs_objs)}")
    print(f"####### len(telethon_configs_objs): {len(telethon_configs_objs)}")
    return list(telethon_configs_objs)
