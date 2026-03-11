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
        username_flag = bool(self.tg_username)
        phone_flag = bool(self.tg_phone)
        valid_name_flag = bool(self.tg_first_name) and bool(self.tg_last_name)

        valid_combin_flag = any([username_flag,
                                 phone_flag,
                                 valid_name_flag])

        invalid_name_combin_flag = all([username_flag or not username_flag,
                                        phone_flag or not phone_flag,
                                        not valid_name_flag])

        if invalid_name_combin_flag:
            error_log = (f"\nProvide both params or leave them empty [ERROR]: "
                         f"[tg_first_name AND!!! tg_last_name]\n"
                         f"tg_first_name: {self.tg_first_name}\n"
                         f"tg_last_name: {self.tg_last_name}\n")
            print(error_log)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                                detail=error_log)

        if not valid_combin_flag:
            error_log = (f"\nEmpty parameters or wrong name combination [ERROR]: "
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
