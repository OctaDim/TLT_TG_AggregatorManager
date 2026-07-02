from typing import Optional

from pydantic import BaseModel, Field

from fast_api.app_telegram_folders_common.scheme_telegram_folders_common import (
    TGFolderBaseResponse,
    TGFolderData,
    TGFolderDefinition,
)


class InCreateTelegramFolderData(BaseModel):
    folder_id: Optional[int] = Field(default=None, ge=2, le=255)
    folder_definition: TGFolderDefinition


class OutCreateTelegramFolderResponse(TGFolderBaseResponse):
    folder: TGFolderData
