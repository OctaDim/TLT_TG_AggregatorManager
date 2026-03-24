from dataclasses import dataclass


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

    FOUND_FIRST_USER_FOR_ALL_TLT_CLIENTS: bool = True
    FOUND_FIRST_USER_BY_NAME_ALL_TLT_CLIENTS: bool = True

    LOG_TG_FOUND_USER_BY_PHONE: bool = True
    LOG_TG_FOUND_USER_BY_NAME: bool = True
    LOG_TG_FOUND_USER_BY_USERNAME: bool = True

    FIND_USERS_BY_NAME_DATA: bool = True
    FIND_USERS_BY_FIRST_LAST_NAME_BOTH: bool = True
    FIND_USERS_BY_NAME_LIMIT: int = 300

    ALL_TLT_CLIENTS_SEND_MSG_ONCE: bool = True

    LOG_TG_SEND_MSG_BY_USERNAME: bool = True
    LOG_TG_SEND_MSG_BY_USER_ID: bool = True


@dataclass(frozen=True)
class AGGREGATOR_API_OPTIONS:
    AGGREGATOR_WEBHOOKS_API_URL_BASE_NAME: str = "global_api_aggregator"
    OUTGOING_EXT_API_REQ_TIMEOUT: int = 60
    SOURCE_STRING_FOR_EXT_AGGREGATOR: str = "telegram_tlt"
    LOG_EXT_AGGREGATOR_API_RESPONSE: bool = True


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


# @dataclass(frozen=True)
# class EMERGENCY_CALL_OPTIONS:
#     EMERGENCY_CALL_URL = "https://samara.softats.ru/account/pact/emergency_call"
#     EMERGENCY_CALL_REQUEST_TIMEOUT: float = 120
#     LOG_EMERGENCY_CALL_REQ_RESPONSE: bool = True
