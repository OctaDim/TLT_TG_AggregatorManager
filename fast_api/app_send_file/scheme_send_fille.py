from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel, model_validator
from starlette import status


class InSendFileData(BaseModel):
    tg_username: Optional[str] = ""
    tg_user_id: Optional[str] = ""
    file_name: str
    file_content: bytes


    @model_validator(mode="before")
    def validate_fields(cls, data):
        tg_username = data["tg_username"]
        tg_user_id = data["tg_user_id"]
        file_name = data["file_name"]
        file_content = data["file_content"]

        username_flag = bool(tg_username)
        user_id_flag = bool(tg_user_id)
        file_name_flag = bool(file_name)
        file_content_flag = bool(file_content)

        valid_combin_flag = any([
            (username_flag or user_id_flag) and (file_name_flag and file_content_flag),
            (username_flag and user_id_flag) and (file_name_flag and file_content_flag)])

        if not valid_combin_flag:
            error_log = (f"\nWrong parameters passed [ERROR]:\n"
                         f"Possible combinations: "
                         f"[tg_username OR/AND tg_user_id] AND [file_name] AND [file_content]\n"
                         f"tg_username: {tg_username}\n"
                         f"tg_user_id: {tg_user_id}\n"
                         f"file_name: {file_name}\n"
                         f"file_content_flag: {file_content_flag}\n")
            print(error_log)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=error_log)
        return data
