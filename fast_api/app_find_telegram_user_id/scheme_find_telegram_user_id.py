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
        first_name_flag = bool(self.tg_first_name)
        last_name_flag = bool(self.tg_last_name)

        valid_combin_flag = any([username_flag,
                                 phone_flag,
                                 first_name_flag and last_name_flag])

        partial_name_flag = all([first_name_flag or last_name_flag,
                                 not (first_name_flag and last_name_flag)])

        if partial_name_flag:
            error_log = (f"\nProvide both name params or leave empty [ERROR]:\n"
                         f"Possible name combination: "
                         f"[tg_first_name AND!!! tg_last_name]\n"
                         f"tg_first_name: {self.tg_first_name}\n"
                         f"tg_last_name: {self.tg_last_name}\n")
            print(error_log)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                                detail=error_log)

        if not valid_combin_flag:
            error_log = (f"\nEmpty parameters passed [ERROR]:\n"
                         f"Possible combinations: [tg_username] OR/AND "
                         f"[tg_phone] OR/AND [tg_first_name AND!!! tg_last_name]\n"
                         f"tg_username: {self.tg_username}\n"
                         f"tg_first_name: {self.tg_first_name}\n"
                         f"tg_last_name: {self.tg_last_name}\n"
                         f"tg_phone: {self.tg_phone}\n")
            print(error_log)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                                detail=error_log)
        return self
