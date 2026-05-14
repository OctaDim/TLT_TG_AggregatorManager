from typing import Optional

from pydantic import BaseModel, model_validator
from starlette import status
from starlette.exceptions import HTTPException


class InTltServerFileData(BaseModel):
    extra_file_name: str
    custom_file_name: Optional[str] = None
    tlt_config_name: Optional[str] = None

    @model_validator(mode="before")
    def validate_fields(cls, data):
        extra_file_name = data.get("extra_file_name")
        custom_file_name = data.get("custom_file_name")

        if not extra_file_name:
            error_log = (f"\nWrong parameters combination [ERROR]:\n"
                         f"Possible combinations: [extra_file_name] and "
                         f"[custom_file_name or not custom_file_name] and"
                         f"[tlt_config_name or not tlt_config_name]\n"
                         f"extra_file_name: {extra_file_name}\n"
                         f"custom_file_name: {custom_file_name}\n")
            print(error_log)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=error_log)
        return data
