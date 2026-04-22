from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel, model_validator
from starlette import status


class InSendMessageData(BaseModel):
    tg_username: Optional[str] = ""
    tg_user_id: Optional[str] = ""
    message_text: str

    @model_validator(mode="after")
    def validate_fields(self):
        username_flag = bool(self.tg_username)
        user_id_flag = bool(self.tg_user_id)
        message_text_flag = bool(self.message_text)

        valid_combin_flag = any([
            (username_flag or user_id_flag) and message_text_flag,
            (username_flag and user_id_flag) and message_text_flag])

        if not valid_combin_flag:
            error_log = (f"\nEmpty parameters passed [ERROR]:\n"
                         f"Possible combinations: "
                         f"[tg_username OR/AND tg_user_id] AND [message_text]\n"
                         f"tg_username: {self.tg_username}\n"
                         f"tg_user_id: {self.tg_user_id}\n"
                         f"message_text: {self.message_text}\n")
            print(error_log)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=error_log)
        return self
