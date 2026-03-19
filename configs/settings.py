import os
import sys
from configparser import ConfigParser
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

from utils_common.get_cur_ip_address import (
    get_cur_external_ip_via_google_dns, get_cur_internal_ip)
from utils_common.normalized_path import get_full_file_normal_path

BASE_DIR = Path(__file__).resolve().parent.parent

# GETTING TEST ENV CONFIGS #############################################
test_env_normal_path = get_full_file_normal_path(
    all_dir_str_parts=[BASE_DIR],
    file_name_with_ext=".env")
env = load_dotenv(test_env_normal_path)  # for future
API_TEST_USERNAME = os.getenv("API_TEST_USERNAME")
API_TEST_PASSWORD = os.getenv("API_TEST_PASSWORD")

# GETTING CURRENT INTERNAL AND EXTERNAL IPs #############################
get_cur_internal_ip(log_ip=True)
cur_external_ip = get_cur_external_ip_via_google_dns(log_ip=True)


# GETTING API INI CONFIGS ##############################################
@dataclass(frozen=True)
class API_CONFIG_NAMES:
    API_PRODUCT_SERVER_IP = "API_production"
    API_HAKASIA_PROD_SERVER_IP = "API_Hakasia_product_server"
    API_TEST_176_124_136_22_IP = "API_test_server_176_124_136_22_8000"
    API_TEST_192_168_21_22_IP = "API_test_server_192_168_21_22_8000"
    API_TEST_PORT_ANY_IP = "API_port_all_ips_0_0_0_0_8000"
    API_TEST_WIN_LOCALHOST = "API_win_localhost_127_0_0_1_8000"
    API_TEST_UNIX_LOCALHOST = "API_unix_localhost_127_0_1_1_8000"
    API_TEST_DEXP_1_IP = "API_dexp_ip_192_168_0_117_8000"
    API_TEST_DEXP_2_IP = "API_dexp_ip_192_168_0_106_8000"


api_ini_normal_path = get_full_file_normal_path(
    all_dir_str_parts=[BASE_DIR],
    file_name_with_ext=".configs_api.ini")
api_conf_parser = ConfigParser()
api_conf_parser.read(filenames=api_ini_normal_path)

if cur_external_ip == "___.___.___.___":  # Just example
    api_conf_name = API_CONFIG_NAMES.API_TEST_PORT_ANY_IP
elif cur_external_ip == "172.19.201.24":
    api_conf_name = API_CONFIG_NAMES.API_PRODUCT_SERVER_IP
elif cur_external_ip == "172.19.201.24":
    api_conf_name = API_CONFIG_NAMES.API_HAKASIA_PROD_SERVER_IP
elif cur_external_ip == "176.124.136.22":
    api_conf_name = API_CONFIG_NAMES.API_TEST_176_124_136_22_IP
elif cur_external_ip == "192.168.21.22":
    api_conf_name = API_CONFIG_NAMES.API_TEST_192_168_21_22_IP
elif cur_external_ip == "192.168.0.117":
    api_conf_name = API_CONFIG_NAMES.API_TEST_DEXP_1_IP
elif cur_external_ip == "192.168.0.106":
    api_conf_name = API_CONFIG_NAMES.API_TEST_DEXP_2_IP
elif sys.platform == "linux":
    api_conf_name = API_CONFIG_NAMES.API_TEST_UNIX_LOCALHOST
elif sys.platform == "win32":
    api_conf_name = API_CONFIG_NAMES.API_TEST_WIN_LOCALHOST
else:
    api_conf_name = API_CONFIG_NAMES.API_TEST_PORT_ANY_IP

API_HOST: str = api_conf_parser.get(section=api_conf_name, option="API_HOST")
API_PORT: int = int(api_conf_parser.get(section=api_conf_name, option="API_PORT"))
API_USERNAME: str = api_conf_parser.get(section=api_conf_name, option="API_USERNAME")
API_PASSWORD: str = api_conf_parser.get(section=api_conf_name, option="API_PASSWORD")
FASTAPI_SESSION_KEY: str = api_conf_parser.get(section=api_conf_name, option="FASTAPI_SESSION_KEY")


# GETTING TELEGRAM API INI CONFIGS #####################################
@dataclass(frozen=True)
class TELEGRAM_API_CONFIG_NAMES:
    TG_OFFICIAL_API_any_ip_prod = "TELEGRAM_OFFICIAL_API_any_ip_prod"
    TG_OFFICIAL_API_TEST_375296085622 = "TELEGRAM_OFFICIAL_API_TEST_375296085622"


telegram_api_ini_normal_path = get_full_file_normal_path(
    all_dir_str_parts=[BASE_DIR],
    file_name_with_ext=".configs_telegram.ini")
telegram_api_conf_parser = ConfigParser()
telegram_api_conf_parser.read(filenames=telegram_api_ini_normal_path)

if cur_external_ip == "___.___.___.___":  # Just example
    telegram_api_conf_name = TELEGRAM_API_CONFIG_NAMES.TG_OFFICIAL_API_any_ip_prod  # Certain configs can be defined
if cur_external_ip == "176.124.136.22":  # Just example
    telegram_api_conf_name = TELEGRAM_API_CONFIG_NAMES.TG_OFFICIAL_API_TEST_375296085622
else:
    telegram_api_conf_name = TELEGRAM_API_CONFIG_NAMES.TG_OFFICIAL_API_TEST_375296085622

TELEGRAM_OFFICIAL_APP_API_ID = int(telegram_api_conf_parser.get(
    section=telegram_api_conf_name, option="TG_OFFICIAL_APP_API_ID"))
TELEGRAM_OFFICIAL_APP_API_HASH = telegram_api_conf_parser.get(
    section=telegram_api_conf_name, option="TG_OFFICIAL_APP_API_HASH")


# GETTING SQLADMIN INI CONFIGS #########################################
@dataclass(frozen=True)
class SQLADMIN_CONFIG_NAMES:
    SQLADMIN_PRODUCT_ANY_IP = "SQLADMIN_any_ip_prod"


sqladmin_ini_normal_path = get_full_file_normal_path(
    all_dir_str_parts=[BASE_DIR],
    file_name_with_ext=".configs_sqladmin.ini")
sqladmin_conf_parser = ConfigParser()
sqladmin_conf_parser.read(filenames=sqladmin_ini_normal_path)

if cur_external_ip == "___.___.___.___":
    sqladmin_conf_name = SQLADMIN_CONFIG_NAMES.SQLADMIN_PRODUCT_ANY_IP  # Certain configs can be defined
else:
    sqladmin_conf_name = SQLADMIN_CONFIG_NAMES.SQLADMIN_PRODUCT_ANY_IP

SQLADMIN_SUPERADMIN_USERNAME = sqladmin_conf_parser.get(
    section=sqladmin_conf_name, option="SQLADMIN_SUPERADMIN_USERNAME")
SQLADMIN_ADMIN_PASSWORD = sqladmin_conf_parser.get(
    section=sqladmin_conf_name, option="SQLADMIN_ADMIN_PASSWORD")
SQLADMIN_ADMIN_USERNAME = sqladmin_conf_parser.get(
    section=sqladmin_conf_name, option="SQLADMIN_ADMIN_USERNAME")
SQLADMIN_SUPERADMIN_PASSWORD = sqladmin_conf_parser.get(
    section=sqladmin_conf_name, option="SQLADMIN_SUPERADMIN_PASSWORD")


# GETTING POSTGRES INI CONFIGS #########################################
@dataclass(frozen=True)
class POSTGRES_CONFIG_NAMES:
    POSTGRES_PRODUCT_SERVER_IP = "Postgres_production"
    POSTGRES_HAKASIA_PROD_SERVER_IP = "Postgres_Hakasia_product_server"
    POSTGRES_TEST_176_124_136_22_IP = "Postgres_prod_server_176_124_136_22"
    POSTGRES_TEST_PORT_ANY_IP = "Postgres_port_all_ips_0_0_0_0_8000"
    POSTGRES_TEST_WIN_LOCALHOST = "Postgres_win_localhost_127_0_0_1_8000"
    POSTGRES_TEST_UNIX_LOCALHOST = "Postgres_unix_localhost_127_0_1_1_8000"
    POSTGRES_TEST_DEXP_IP = "Postgres_dexp_ip_192_168_0_117_8000"


postgres_ini_normal_path = get_full_file_normal_path(
    all_dir_str_parts=[BASE_DIR],
    file_name_with_ext=".configs_postgres.ini")
postgres_conf_parser = ConfigParser()
postgres_conf_parser.read(filenames=postgres_ini_normal_path)

if cur_external_ip == "___.___.___.___":  # Just example
    postgres_conf_name = POSTGRES_CONFIG_NAMES.POSTGRES_TEST_PORT_ANY_IP
elif cur_external_ip == "172.19.201.24":
    postgres_conf_name = POSTGRES_CONFIG_NAMES.POSTGRES_PRODUCT_SERVER_IP
elif cur_external_ip == "172.19.201.24":
    postgres_conf_name = POSTGRES_CONFIG_NAMES.POSTGRES_HAKASIA_PROD_SERVER_IP
elif cur_external_ip == "176.124.136.22":
    postgres_conf_name = POSTGRES_CONFIG_NAMES.POSTGRES_TEST_176_124_136_22_IP
elif cur_external_ip == "192.168.0.117":
    postgres_conf_name = POSTGRES_CONFIG_NAMES.POSTGRES_TEST_DEXP_IP
elif sys.platform == "linux":
    postgres_conf_name = POSTGRES_CONFIG_NAMES.POSTGRES_TEST_UNIX_LOCALHOST
elif sys.platform == "win32":
    postgres_conf_name = POSTGRES_CONFIG_NAMES.POSTGRES_TEST_WIN_LOCALHOST
else:
    postgres_conf_name = POSTGRES_CONFIG_NAMES.POSTGRES_TEST_PORT_ANY_IP

POSTGRES_USER = postgres_conf_parser.get(section=postgres_conf_name, option="POSTGRES_USER")
POSTGRES_PASSWORD = postgres_conf_parser.get(section=postgres_conf_name, option="POSTGRES_PASSWORD")
POSTGRES_HOST = postgres_conf_parser.get(section=postgres_conf_name, option="POSTGRES_HOST")
POSTGRES_PORT = postgres_conf_parser.get(section=postgres_conf_name, option="POSTGRES_PORT") or None
POSTGRES_DB_NAME = postgres_conf_parser.get(section=postgres_conf_name, option="POSTGRES_DB_NAME")


# GETTING AGGREGATOR INI CONFIGS #########################################
@dataclass(frozen=True)
class AGGREGATOR_CONFIG_NAMES:
    AGGREGATOR_PRODUCT_SERVER_IP = "AGGREGATOR_production"
    AGGREGATOR_HAKASIA_SERVER_IP = "AGGREGATOR_Hakasia_product_server"
    AGGREGATOR_TEST_176_124_136_22_IP = "AGGREGATOR_test_176_124_136_22"
    AGGREGATOR_TEST_PORT_ANY_IP = "AGGREGATOR_all_ips_0_0_0_0"
    AGGREGATOR_TEST_WIN_LOCALHOST = "AGGREGATOR_win_localhost_127_0_0_1"
    AGGREGATOR_TEST_UNIX_LOCALHOST = "AGGREGATOR_unix_localhost_127_0_1_1"
    AGGREGATOR_TEST_DEXP_IP = "AGGREGATOR_dexp_ip_192_168_0_106"


aggregator_ini_normal_path = get_full_file_normal_path(
    all_dir_str_parts=[BASE_DIR],
    file_name_with_ext=".configs_aggregator.ini")
aggregator_conf_parser = ConfigParser()
aggregator_conf_parser.read(filenames=aggregator_ini_normal_path)

if cur_external_ip == "___.___.___.___":  # Just example
    aggregator_conf_name = AGGREGATOR_CONFIG_NAMES.AGGREGATOR_TEST_176_124_136_22_IP
elif cur_external_ip == "172.19.201.24":
    aggregator_conf_name = AGGREGATOR_CONFIG_NAMES.AGGREGATOR_PRODUCT_SERVER_IP
elif cur_external_ip == "172.19.201.24":
    aggregator_conf_name = AGGREGATOR_CONFIG_NAMES.AGGREGATOR_HAKASIA_SERVER_IP
elif cur_external_ip == "176.124.136.22":
    aggregator_conf_name = AGGREGATOR_CONFIG_NAMES.AGGREGATOR_TEST_176_124_136_22_IP
elif cur_external_ip == "192.168.0.117":
    aggregator_conf_name = AGGREGATOR_CONFIG_NAMES.AGGREGATOR_TEST_DEXP_IP
elif sys.platform == "linux":
    aggregator_conf_name = AGGREGATOR_CONFIG_NAMES.AGGREGATOR_TEST_UNIX_LOCALHOST
elif sys.platform == "win32":
    aggregator_conf_name = AGGREGATOR_CONFIG_NAMES.AGGREGATOR_TEST_WIN_LOCALHOST
else:
    aggregator_conf_name = AGGREGATOR_CONFIG_NAMES.AGGREGATOR_TEST_PORT_ANY_IP

AGGREGATOR_USERNAME = aggregator_conf_parser.get(section=aggregator_conf_name, option="AGGREGATOR_USERNAME")
AGGREGATOR_PASSWORD = aggregator_conf_parser.get(section=aggregator_conf_name, option="AGGREGATOR_PASSWORD")
AGGREGATOR_HOST = aggregator_conf_parser.get(section=aggregator_conf_name, option="AGGREGATOR_HOST")
AGGREGATOR_PORT = aggregator_conf_parser.get(section=aggregator_conf_name, option="AGGREGATOR_PORT") or None

# Server-port for BERT classifier API to request
AGGREGATOR_API_SEVER_PORT = "{api_host}:{api_port}".format(
    api_host=AGGREGATOR_HOST, api_port=AGGREGATOR_PORT)


@dataclass(frozen=True)
class FASTAPI_OPTIONS:
    LOG_LEVEL = "debug"  # used in main.py when starting uvicorn
    USE_COLORS = True  # used in main.py when starting uvicorn


@dataclass(frozen=True)
class ALCHEMY_OPTIONS:
    DISABLE_SWAGGER_DOCUMENTATION: bool = True
    USE_POSTGRES_DATABASE: bool = True
    ALCHEMY_ORM_RAW_SQL_LOGS: bool = False
    ALCHEMY_QUERY_EXEC_TIME_LOGS: bool = False
    ALCHEMY_SESSION_OK_ACTIONS_LOGS: bool = False
    ALCHEMY_USE_FUTURE_ALCHEMY: bool = True
    ALCHEMY_POOL_PRE_PING: bool = True
    ALCHEMY_CONST_CONN_POOL_SIZE: int = 20
    ALCHEMY_TEMP_CONN_MAX_OVERFLOW: int = 30
    ALCHEMY_POOL_RECYCLE: int = 600  # seconds
    ALCHEMY_POOL_TIMEOUT: int = 30  # seconds


@dataclass(frozen=True)
class API_OPTIONS:
    LOG_PYDANTIC_OK_VALIDATION: bool = False
    API_BASE_URL_NAME: str = "tg_tlt_aggregator_api"
    # LOG_CONVERSATION_DATA_REQ_RESPONSE: bool = False
    # LOG_MESSAGE_DATA_REQ_RESPONSE: bool = False
    # LOG_ALL_CONVERSATIONS_REQ_RESPONSE: bool = False
    # LOG_ALL_MSGS_BY_CONVERS_REQ_RESPONSE: bool = False
    # LOG_ALL_COMPANIES_REQ_RESPONSE: bool = False


# @dataclass(frozen=True)
# class WEBHOOKS_OPTIONS:
#     WEBHOOKS_API_URL_BASE_NAME: str = "aggregator_api"
#     DEBUG_SKIP_COMPANY_IDS_LIST: tuple[str] = (123456789,)  # (100179,)
#     OUTGOING_EXT_API_REQ_TIMEOUT: float = 120
#     LOG_WEBHOOK_INCOMING_REQ_DATA: bool = False
#     LOG_WEBHOOK_INCOMING_OBJ_DATA: bool = False
#     LOG_WEBHOOK_INCOMING_EXTRA_DATA: bool = False
#     LOG_WEBHOOK_NEW_AUTH_DATA: bool = False
#     LOG_NEW_CONVERSATION_DATA: bool = False
#     LOG_NEW_MESSAGE_DATA: bool = False
#     LOG_NEW_ATTACHMENT_DATA: bool = False
#     MAKE_EMERGENCY_CALL: bool = False


@dataclass(frozen=True)
class SQLADMIN_OPTIONS:
    SQLADMIN_PANEL_BASE_URL: str = "/admin_panel"
    SQLADMIN_CUSTOM_TEMPLATES_DIR: str = "admin_panel/custom_templates"
    CREATE_DEFAULT_ADMIN_SUPERADMIN: bool = True
    CREATE_DEBUG_ADMIN_SUPERADMIN: bool = True
    # MESSAGE_SYMBOLS_TRUNCATE_LIMIT: int = 50
    # PLUS_MINUS_WORDS_TRUNCATE_LIMIT: int = 100
    # CHATS_SUBJECT_TRUNCATE_LIMIT: int = 100
    # # SUBJECT_CHATS_TRUNCATE_LIMIT: int = 100
    # SENDER_NAME_FILTER_TRUNC_LIMIT: int = 25
    # EMOJI_MAX_WIDTH: int = 500
    # EMOJI_MAX_HEIGHT: int = 500
    # DISPLAY_SUBJECT_AS_ARROW: bool = False


# @dataclass(frozen=True)
# class EMERGENCY_CALL_OPTIONS:
#     EMERGENCY_CALL_URL = "https://samara.softats.ru/account/pact/emergency_call"
#     EMERGENCY_CALL_REQUEST_TIMEOUT: float = 120
#     LOG_EMERGENCY_CALL_REQ_RESPONSE: bool = True


@dataclass(frozen=True)
class TELETHON_OPTIONS:
    TERMINATE_PROCESS_TIMEOUT: int = 15
    KILL_PROCESS_TIMEOUT: int = 10
    EACH_ACC_CLIENT_START_DELAY_SEC: int = 0
    EACH_BOT_CLIENT_START_DELAY_SEC: int = 30
    TELEGRAM_CLIENT_CONNECT_RETRIES: int = 5
    TELEGRAM_CLIENT_REQUEST_RETRIES: int = 5
    FLOOD_SLEEP_THRESHOLD: int = 120
    ACCOUNT_SESSION_FILE_PREFIX: str = "sess_acc_"
    BOT_SESSION_FILE_PREFIX: str = "sess_bot_"
    LOG_NEW_TELETHON_CONFIG_DATA: bool = True
    BASE_TELETHON_SESSIONS_DIR: str = "TELETHON_SESSIONS"
    PERIODIC_ASYNC_TASK_INTERVAL_SEC: int = 43200
    LOG_EXEC_TIME_GET_EACH_ATTR: bool = False
    LOG_NON_EXISTING_ATTR_ERROR: bool = False
    LOG_ALL_EVENT_STRINGIFY_PARAMS: bool = True
    EVENT_ATTRS_SECTION_SEPARATOR_PREFIX: str = "separator"
    LOG_ALL_BEFORE_JSON_EVENT_PARAMS: bool = True
    LOG_ALL_AFTER_JSON_EVENT_PARAMS: bool = False
    LOG_NON_JSON_SERIALIZABLE_OBJ: bool = False

    HANDLE_NEW_MESSAGE_EVENT: bool = False
    HANDLE_MESSAGE_EDITED_EVENT: bool = False
    HANDLE_MESSAGE_DELETED_EVENT: bool = False
    HANDLE_MESSAGE_READ_EVENT: bool = False
    HANDLE_CHAT_ACTION_EVENT: bool = False
    HANDLE_USER_UPDATE_EVENT: bool = False
    HANDLE_RAW_EVENT: bool = False
    HANDLE_INLINE_QUERY_EVENT: bool = False
    HANDLE_CALLBACK_QUERY_EVENT: bool = False

    TEMP_TG_DOWNLOADED_FILES_DIR: str = "TEMP_TELETHON_FILES"
    DOWNLOAD_PHOTO_FILE_NAME: bool = True
    DOWNLOAD_VIDEO_FILE_NAME: bool = True

    USE_FIRST_FOUND_USER_FOR_ALL_TLT_CLIENTS: bool = True
    USE_FIRST_FOUND_USERS_BY_NAME_ALL_TLT_CLIENTS: bool = True

    ALL_TLT_CLIENTS_SEND_MSG_ONCE: bool = True

    FIND_USERS_BY_NAME_DATA: bool = True
    FIND_USERS_BY_FIRST_LAST_NAME_BOTH: bool = True
    FIND_USERS_BY_NAME_LIMIT: int = 300

    LOG_TG_FOUND_USER_BY_PHONE: bool = True
    LOG_TG_FOUND_USER_BY_NAME: bool = True
    LOG_TG_FOUND_USER_BY_USERNAME: bool = True

    LOG_TG_SEND_MSG_BY_USERNAME: bool = True
    LOG_TG_SEND_MSG_BY_USER_ID: bool = True


@dataclass(frozen=True)
class AGGREGATOR_API_OPTIONS:
    AGGREGATOR_WEBHOOKS_API_URL_BASE_NAME: str = "global_api_aggregator"
    OUTGOING_EXT_API_REQ_TIMEOUT: int = 60
    SOURCE_STRING_FOR_EXT_AGGREGATOR: str = "telegram_tlt"
    LOG_EXT_AGGREGATOR_API_RESPONSE: bool = True
