if __name__ == "__main__":
    import asyncio
    from db_postgres.postgres_conn.pgs_connection import PgsAsyncConnection
    from db_postgres.postgres_conn.postgres_session import PgsAsyncSession
    from db_postgres.postgres_models.__temp.webhook_conversation_model import (
        WebhookConversationModel)
    from db_postgres.postgres_queries_utils.update_existing_model_objects import (
        update_existing_model_objs_qry)

    ModelClassORM = WebhookConversationModel
    filter_fields = {"local_id": [361, 360]}
    update_data = {"event": "upd-222", "type": "conv-222"}


    async def test_update_existing_model_obj_qry():
        pgs_async_conn = PgsAsyncConnection()
        async with PgsAsyncSession(engine=pgs_async_conn.engine,
                                   log_good_ops=True
                                   ) as pgs_async_session:
            result = await update_existing_model_objs_qry(
                ModelClassORM=ModelClassORM,
                ongoing_session=pgs_async_session,
                fields_values_filter=filter_fields,
                update_data=update_data)
            return result


    query_result = asyncio.run(test_update_existing_model_obj_qry(), debug=True)
    print("query_result: ", query_result)
