from typing import Optional

from pydantic import BaseModel, model_validator
from starlette import status
from starlette.exceptions import HTTPException


class InGetFileByMessageData(BaseModel):
    message_id: int
    channel_id: Optional[int] = None
    chat_id: Optional[int] = None
    user_id: Optional[int] = None
    extra_file_name: Optional[str] = None

    @model_validator(mode="before")
    def validate_fields(cls, data):
        message_id = data.get("message_id")
        channel_id = data.get("channel_id")
        chat_id = data.get("chat_id")
        user_id = data.get("user_id")
        extra_file_name = data.get("extra_file_name")

        valid_combin_flag = any([
            message_id and channel_id and (channel_id not in ["", None]),

            message_id and (channel_id or chat_id or user_id),
            extra_file_name])

        if not valid_combin_flag:
            error_log = (f"\nWrong parameters combination [ERROR]:\n"
                         f"Possible combinations: [extra_file_name] OR "
                         f"[message_id] AND [channel_id OR chat_id OR user_id]\n"
                         f"message_id: {message_id}\n"
                         f"channel_id: {channel_id}\n"
                         f"chat_id: {chat_id}\n"
                         f"user_id: {user_id}\n"
                         f"extra_file_name: {extra_file_name}\n")
            print(error_log)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=error_log)
        return data
