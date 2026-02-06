if __name__ == "__main__":
    import asyncio
    from db_postgres.postgres_conn.pgs_connection import PgsAsyncConnection
    from db_postgres.postgres_conn.postgres_session import PgsAsyncSession
    from db_postgres.postgres_models.telethon_configs_model import (
        TelethonConfigModel)
    from db_postgres.postgres_queries_utils.get_model_records_flex_query import (
        get_model_rows_flex_query)

    ModelClassORM = TelethonConfigModel
    filter_fields = {
        # "id": 31,
        "web_account_id": "30",
        "web_account_username": "globalhome",
        # "tg_personal_phone": "+375296720893",
        # "tg_personal_phone": [None],
        # "tg_personal_phone": ["+375296720893", ""],
        "tg_personal_phone": ["+375296720893", "", None],
        # "tg_bot_token": None,
        # "tg_bot_token": ["", None],
    }


    async def test_get_model_rows_flex_qry():
        pgs_async_conn = PgsAsyncConnection()
        async with PgsAsyncSession(engine=pgs_async_conn.engine,
                                   log_good_ops=True
                                   ) as pgs_async_session:
            result = await get_model_rows_flex_query(
                orm_model_class=ModelClassORM,
                ongoing_session=pgs_async_session,
                selected_fields=None,
                fields_values_filter=filter_fields,
                order_by_fields=None,
                return_scalars=True)
            return result


    query_result = asyncio.run(test_get_model_rows_flex_qry(), debug=True)
    print("len(query_result): ", len(query_result))
    print("query_result: ", query_result)
