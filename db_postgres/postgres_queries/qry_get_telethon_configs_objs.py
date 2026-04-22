from typing import List, Dict

from sqlalchemy import Row
from sqlalchemy.ext.asyncio import AsyncSession

from db_postgres.postgres_models.telethon_configs_model import (
    TelethonConfigModel)
from db_postgres.postgres_queries_utils.get_model_records_flex_query import (
    get_model_rows_flex_query)


async def get_tlt_configs_objs_list_qry(
        ongoing_session: AsyncSession,
) -> List[Row]:
    """Returns list of dicts with Telethon clients configurations"""
    filter_fields = {"active": True}
    # filter_fields = {"active": True,
    #                  "telethon_is_active": True}
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


async def get_tlt_configs_objs_dict_qry(
        ongoing_session: AsyncSession,
) -> Dict[str, Row]:
    """Returns list of dicts with Telethon clients configurations"""
    filter_fields = {"active": True}
    # filter_fields = {"active": True,
    #                  "telethon_is_active": True}
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

    tlt_configs_objs_dict = {}

    for cur_config_obj in telethon_configs_objs:
        cur_config_name = cur_config_obj.telethon_config_name
        tlt_configs_objs_dict[cur_config_name] = cur_config_obj

    # print(f"####### tlt_configs_objs_dict: {tlt_configs_objs_dict}")  # Too long
    print(f"####### type(tlt_configs_objs_dict): {type(tlt_configs_objs_dict)}")
    print(f"####### len(tlt_configs_objs_dict): {len(tlt_configs_objs_dict)}")
    return tlt_configs_objs_dict
