from typing import List

from fastapi import HTTPException
from pydantic import BaseModel, model_validator
from starlette import status


class InDialogsByConfigsData(BaseModel):
    messenger_type: str = "telegram"
    selected_configs: List[str]
    dialogs_limit_per_config: int = 100

    @model_validator(mode="after")
    def validate_fields(self):
        if not self.selected_configs:
            error_log = "selected_configs is empty [ERROR]"
            print(error_log)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_log)

        if self.dialogs_limit_per_config < 1:
            error_log = "dialogs_limit_per_config must be positive [ERROR]"
            print(error_log)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_log)
        return self

