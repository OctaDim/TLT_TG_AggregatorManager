from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel, model_validator
from starlette import status


class InSendMessageData(BaseModel):
    tg_username: Optional[str] = ""
    tg_user_id: Optional[str] = ""
    message_text: Optional[str] = ""
    specific_msg_config: Optional[str] = None  # To send from certain config

    @model_validator(mode="before")
    def validate_fields(cls, data):
        tg_username = data["tg_username"]
        tg_user_id = data["tg_user_id"]

        valid_combin_flag = any([tg_username or tg_user_id, ])

        if not valid_combin_flag:
            error_log = (f"\nWrong parameters combination passed [ERROR]:\n "
                         f"Possible combinations: "
                         f"[tg_username OR/AND tg_user_id]\n "
                         f"tg_username: {tg_username}\n "
                         f"tg_user_id: {tg_user_id}\n ")
            print(error_log)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=error_log)
        return data
