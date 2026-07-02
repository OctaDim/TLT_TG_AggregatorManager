from typing import List

from fastapi import HTTPException
from pydantic import BaseModel, Field, model_validator
from starlette import status

from fast_api.app_telegram_folders_common.scheme_telegram_folders_common import (
    TGFolderBaseResponse,
    TGFolderData,
)


class InReorderTelegramFoldersData(BaseModel):
    folder_ids: List[int] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_folder_ids(self):
        if len(self.folder_ids) != len(set(self.folder_ids)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="folder_ids must be unique [ERROR]")
        if any(folder_id < 2 or folder_id > 255
               for folder_id in self.folder_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="folder_ids must be between 2 and 255 [ERROR]")
        return self


class OutReorderTelegramFoldersResponse(TGFolderBaseResponse):
    folder_ids: List[int]
    folders: List[TGFolderData]
