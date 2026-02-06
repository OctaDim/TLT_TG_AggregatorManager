from enum import Enum


class USER_ROLE(Enum):
    """NOTE: If changed enums names here, containing tables and data
    types also should be deleted and reinitialized in Postgres DB"""
    SUPERADMIN: str = "superadmin"
    ADMIN: str = "admin"
    USER: str = "user"


class TELEGRAM_ACCOUNT_TYPE(Enum):
    ACCOUNT: str = "account"
    BOT: str = "bot"


class QR_CODE_ERROR_CORRECTION(Enum):
    # QR error correct levels
    LEVEL_L = 1
    LEVEL_M = 0
    LEVEL_Q = 3
    LEVEL_H = 2
