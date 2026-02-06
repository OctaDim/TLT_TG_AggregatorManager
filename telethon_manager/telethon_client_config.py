from typing import Optional

from pydantic import BaseModel

from configs.enums import TELEGRAM_ACCOUNT_TYPE


class TelethonConfig(BaseModel):
    web_account_id: str
    web_account_username: str
    telethon_config_id: int
    name: Optional[str] = None
    account_type: TELEGRAM_ACCOUNT_TYPE
    api_id: int
    api_hash: str
    session_string: Optional[str] = None
    bot_token: Optional[str] = None
    phone: Optional[str] = None
    proxy: Optional[dict] = None
    is_active: bool = True
