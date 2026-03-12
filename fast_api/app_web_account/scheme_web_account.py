from fastapi import HTTPException
from pydantic import BaseModel, model_validator
from starlette import status


class InWebAccountData(BaseModel):
    web_account_id: str
    web_account_username: str
    # telegram_phone: str = None
    # telegram_bot_token: str = None

    @model_validator(mode="after")
    def validate_fields(self):
        acc_id_flag = bool(self.web_account_id)
        acc_username_flag = bool(self.web_account_username)

        if not (acc_id_flag and acc_username_flag):
            error_log = (f"\nEmpty parameters passed [ERROR]:\n"
                         f"Possible combinations: "
                         f"[web_account_id AND web_account_username]\n"
                         f"web_account_id: {self.web_account_id}\n"
                         f"web_account_username: {self.web_account_username}\n")
            print(error_log)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=error_log)
        return self
