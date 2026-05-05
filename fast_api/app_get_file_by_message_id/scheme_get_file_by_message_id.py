from typing import Optional

from pydantic import BaseModel, model_validator
from starlette import status
from starlette.exceptions import HTTPException


class InGetFileByMessageData(BaseModel):
    message_id: int
    channel_id: Optional[int] = None
    chat_id: Optional[int] = None
    user_id: Optional[int] = None
    # telethon_config_name: Optional[str] = None
    tlt_config_name: Optional[str] = None
    extra_file_name: Optional[str] = None

    @model_validator(mode="before")
    def validate_fields(cls, data):
        message_id = data.get("message_id")
        channel_id = data.get("channel_id")
        chat_id = data.get("chat_id")
        user_id = data.get("user_id")
        extra_file_name = data.get("extra_file_name")
        tlt_config_name = data.get("tlt_config_name")

        valid_chanel_flag = channel_id not in ["", None]
        valid_chat_flag = chat_id not in ["", None]
        valid_user_flag = user_id not in ["", None]

        passed_ids_sum = sum([bool(channel_id), bool(chat_id), bool(user_id)])
        if passed_ids_sum == 1:
            valid_combin_flag = any([
                all([message_id, channel_id, tlt_config_name, valid_chanel_flag]),
                all([message_id, chat_id, tlt_config_name, valid_chat_flag]),
                all([message_id, user_id, tlt_config_name, valid_user_flag])])
        elif extra_file_name and passed_ids_sum == 0:
            valid_combin_flag = True
        else:
            valid_combin_flag = False

        if not valid_combin_flag:
            error_log = (f"\nWrong parameters combination [ERROR]:\n"
                         f"Possible combinations: [extra_file_name] OR "
                         f"[message_id] AND ([channel_id OR chat_id OR user_id])\n"
                         f"message_id: {message_id}\n"
                         f"channel_id: {channel_id}\n"
                         f"chat_id: {chat_id}\n"
                         f"user_id: {user_id}\n"
                         f"tlt_config_name: {tlt_config_name}\n"
                         f"extra_file_name: {extra_file_name}\n"
                         f"valid_chanel_flag: {valid_chanel_flag}\n"
                         f"valid_chat_flag: {valid_chat_flag}\n"
                         f"valid_user_flag: {valid_user_flag}\n"
                         f"passed_ids_sum: {passed_ids_sum}\n"
                         f"valid_combin_flag: {valid_combin_flag}\n")
            print(error_log)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=error_log)
        return data
