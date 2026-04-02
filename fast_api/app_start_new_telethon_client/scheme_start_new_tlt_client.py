from typing import Literal

from fastapi import HTTPException
from pydantic import BaseModel, model_validator
from starlette import status


class InStartNewTelethonClient(BaseModel):
    telegram_phone: str = None
    telegram_bot_token: str = None
    authorisation_type: Literal["console", "web"] = "console"

    @model_validator(mode="after")
    def validate_fields(self):
        if not self.telegram_phone and not self.telegram_bot_token:
            error_log = (f"Not passed telegram_user_phone or telegram_bot_token [ERROR]: "
                         f"telegram_phone: {self.telegram_phone}, "
                         f"telegram_bot_token: {self.telegram_bot_token}")
        elif self.telegram_phone and self.telegram_bot_token:
            error_log = (f"Only telegram_user_phone or telegram_bot_token accepted [ERROR]: "
                         f"telegram_phone: {self.telegram_phone}, "
                         f"telegram_bot_token: {self.telegram_bot_token}")
        else:
            error_log = None

        if error_log:
            print(error_log)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=error_log)
        return self
