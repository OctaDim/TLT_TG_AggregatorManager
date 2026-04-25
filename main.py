import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI
from sqladmin import Admin
from starlette.applications import Starlette
from starlette.middleware.sessions import SessionMiddleware

from admin_panel.admin_views.admin_auth_role_backend import (
    AdminAuthRoleAuthBackend)
from configs.environments import (
    API_HOST, API_PORT,
    FASTAPI_SESSION_KEY)
from configs.labels_messages import LABELS
from configs.options import FASTAPI_OPTIONS, SQLADMIN_OPTIONS
from db_postgres.postgres_conn.pgs_connection import (
    PgsAsyncConnection, close_all_async_pgs_connections,
    close_all_sync_pgs_connections)
from db_postgres.postgres_init.db_create_sqladmin_users import (
    create_default_sqladmin_users)
from db_postgres.postgres_init.db_tables_initialization import (
    sync_initialize_db_tables)
from fast_api.app_complete_auth_phone.router_complete_auth_phone import (
    rtr_complete_client_phone_auth)
from fast_api.app_complete_auth_qrcode.router_complete_auth_qrcode import (
    rtr_complete_client_qrcode_auth)
from fast_api.app_find_telegram_users_data.router_find_telegram_data import (
    rtr_find_telegram_users_data)
from fast_api.app_get_qrcode_image_file.router_get_qrcode_img_file import (
    rtr_get_qrcode_image_file)
from fast_api.app_messages_accounts_deactivate.router_msgs_configs_deactivate import (
    rtr_deactivate_messages_configs)
from fast_api.app_messages_configs_activate.router_msgs_configs_activate import (
    rtr_activate_messages_configs)
from fast_api.app_messages_configs_by_web_acc.router_messages_configs_by_web_acc import (
    rtr_tlt_messages_configs_by_web_acc)
from fast_api.app_reconnect_authed_tlt_clients.router_reconnect_authed_tlt_clients import (
    rtr_reconnect_authed_tlt_clients)
from fast_api.app_send_file.router_send_file import (
    rtr_send_telegram_file)
from fast_api.app_send_message.router_send_message import (
    rtr_send_telegram_message)
from fast_api.app_start_new_telethon_client.router_start_new_tlt_client import (
    rtr_start_new_telethon_client)
from fast_api.app_stop_clear_tlt_clients.router_stop_clear_tlt_clients import (
    rtr_stop_clear_tlt_clients)
from fast_api.app_stop_tlt_clients.router_stop_tlt_clients import (
    rtr_stop_tlt_clients)
from fast_api.app_tlt_api_health_check.router_tlt_api_health_check import (
    rtr_tlt_api_health_check)
from fast_api.app_tlt_clients_tasks_status.router_tlt_clients_tasks_status import (
    rtr_tlt_clients_tasks_status)
from fast_api.app_tlt_configs_by_web_acc.router_tlt_configs_by_web_acc import (
    rtr_tlt_configs_by_web_account)
from telethon_manager.telethon_clients_manager import (
    TelethonManagerSingleton)
from telethon_manager.telethon_init_session_dir import (
    init_telethon_sessions_dir)

routers_list = [
    rtr_tlt_api_health_check,
    rtr_tlt_clients_tasks_status,
    rtr_start_new_telethon_client,
    rtr_find_telegram_users_data,
    rtr_send_telegram_message,
    rtr_tlt_configs_by_web_account,
    rtr_complete_client_phone_auth,
    rtr_complete_client_qrcode_auth,
    rtr_get_qrcode_image_file,
    rtr_stop_tlt_clients,
    rtr_stop_clear_tlt_clients,
    rtr_reconnect_authed_tlt_clients,
    rtr_tlt_messages_configs_by_web_acc,
    rtr_activate_messages_configs,
    rtr_deactivate_messages_configs,
    rtr_send_telegram_file,

]

admin_panel_views = []


def initialize_postgres_db_tables():
    sync_initialize_db_tables()


def run_redis():
    # TODO: Check Redis availability and start Redis if not (future)
    print("TODO: Check Redis availability and start Redis if not (future)")


def run_postgres():
    # TODO: Check Postgres availability and start Postgres if not (future)
    print("TODO: Check Postgres availability and start Postgres if not (future)")


async def lifespan_on_startup():
    print(">>>>>>> FastAPI Lifespan (STARTUP): <<<<<<<")
    run_redis()
    run_postgres()
    await create_default_sqladmin_users()  # Creating default sqladmin users


async def lifespan_on_shutdown():
    print(">>>>>>> FastAPI Lifespan (SHUTDOWN): <<<<<<<")
    telethon_manager = TelethonManagerSingleton()  # Singleton
    await telethon_manager.disconnect_all_tlt_clients()
    await telethon_manager.cancel_all_telethon_async_tasks()
    await close_all_async_pgs_connections()
    close_all_sync_pgs_connections()


@asynccontextmanager
async def fast_api_lifespan(app: FastAPI) -> AsyncGenerator:
    await lifespan_on_startup()
    yield  # FastAPI lifespan yield  (Execution fastapi application)
    await lifespan_on_shutdown()


def setup_admin_panel(
        application: FastAPI | Starlette,
        fastapi_session_key: str
) -> Admin:
    authentication_backend = AdminAuthRoleAuthBackend(
        secret_key=fastapi_session_key)
    admin = Admin(
        app=application,
        engine=PgsAsyncConnection().engine,
        authentication_backend=authentication_backend,
        session_maker=None,
        base_url=SQLADMIN_OPTIONS.SQLADMIN_PANEL_BASE_URL,
        title=LABELS.ADMIN_PANEL_TITLE,
        logo_url=None,
        favicon_url=None,
        middlewares=None,
        debug=False,
        templates_dir=SQLADMIN_OPTIONS.SQLADMIN_CUSTOM_TEMPLATES_DIR, )  # Origin SQLAdmin value = "templates"
    for cur_admin_view in admin_panel_views:
        admin.add_view(cur_admin_view)
    return admin


def create_fastapi_application() -> SessionMiddleware:
    fastapi_app = FastAPI(
        lifespan=fast_api_lifespan,
        # docs_url=None,
        # redoc_url=None,
    )

    for cur_router in routers_list:
        fastapi_app.include_router(router=cur_router, )

    setup_admin_panel(application=fastapi_app,
                      fastapi_session_key=FASTAPI_SESSION_KEY)

    fastapi_app_with_middleware = SessionMiddleware(
        app=fastapi_app,
        secret_key=FASTAPI_SESSION_KEY,
        session_cookie="admin_session",
        max_age=600,
        path="/",
        same_site="lax",  # "lax", "strict" or "none"
        https_only=False,
        domain=None)
    return fastapi_app_with_middleware


async def run_telethon():
    await init_telethon_sessions_dir()
    telethon_manager = TelethonManagerSingleton()
    telethon_configs = await telethon_manager.get_postgres_db_tlt_configs()
    await telethon_manager.run_all_telethon_clients(telethon_configs)
    tlt_async_tasks = await telethon_manager.run_all_tlt_clients_async_tasks()
    return tlt_async_tasks


async def run_uvicorn_fastapi_server():  # If used itself without any other async tasks
    uvicorn.run(app=create_fastapi_application(),
                # app="main:create_fastapi_app",  # literal func call is necessary if server reload=True when code changing
                loop="asyncio",
                host=API_HOST,
                port=API_PORT,
                # reload=True,
                # factory=True,
                log_level=FASTAPI_OPTIONS.LOG_LEVEL,
                use_colors=FASTAPI_OPTIONS.USE_COLORS, )
    print("Uvicorn and FastAPI server started [OK]")


async def create_run_uvicorn_fastapi_server():  # If used together with other async tasks
    uvicorn_config = uvicorn.Config(
        app=create_fastapi_application(),
        host=API_HOST,
        port=API_PORT,
        # reload=True,
        # factory=True,
        log_level=FASTAPI_OPTIONS.LOG_LEVEL,
        use_colors=FASTAPI_OPTIONS.USE_COLORS,
        loop="asyncio",
        lifespan="on", )  # Lifespan events can be used if necessary
    server = uvicorn.Server(config=uvicorn_config)
    await server.serve()


async def main_process():
    telethon_async_tasks = await run_telethon()  # Start Telethon clients before FastAPI startup
    uvicorn_fastapi_task = asyncio.create_task(
        coro=create_run_uvicorn_fastapi_server(),
        name="uvicorn_fastapi_server",
        context=None)  # Context vars can be passed/gotten
    all_async_tasks = [*telethon_async_tasks, uvicorn_fastapi_task]
    await asyncio.gather(*all_async_tasks, return_exceptions=True)


if __name__ == "__main__":
    initialize_postgres_db_tables()
    asyncio.run(main=main_process(), debug=True)
