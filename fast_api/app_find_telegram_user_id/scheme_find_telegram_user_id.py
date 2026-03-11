from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel, model_validator
from starlette import status


class InFindTgUserData(BaseModel):
    tg_username: Optional[str] = ""
    tg_first_name: Optional[str] = ""
    tg_last_name: Optional[str] = ""
    tg_phone: Optional[str] = ""

    @model_validator(mode="after")
    def validate_fields(self):
        valid_combin_flag = any([
            bool(self.tg_username),
            bool(self.tg_phone),
            bool(self.tg_first_name) and bool(self.tg_last_name)])

        if not valid_combin_flag:
            error_log = (f"\nEmpty parameters or combination [ERROR]: "
                         f"[tg_username] OR/AND [tg_phone] OR/AND "
                         f"[tg_first_name AND!!! tg_last_name]\n"
                         f"tg_username: {self.tg_username}\n"
                         f"tg_first_name: {self.tg_first_name}\n"
                         f"tg_last_name: {self.tg_last_name}\n"
                         f"tg_phone: {self.tg_phone}\n")
            print(error_log)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                                detail=error_log)
        return self
