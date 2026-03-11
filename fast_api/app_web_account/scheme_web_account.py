from fastapi import HTTPException
from pydantic import BaseModel, model_validator
from starlette import status


class InWebAccountData(BaseModel):
    web_account_id: str
    web_account_username: str
    # telegram_phone: str = None
    # telegram_bot_token: str = None
