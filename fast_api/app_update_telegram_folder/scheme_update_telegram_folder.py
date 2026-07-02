from pydantic import BaseModel, Field

from fast_api.app_telegram_folders_common.scheme_telegram_folders_common import (
    TGFolderBaseResponse,
    TGFolderData,
    TGFolderDefinition,
)


class InUpdateTelegramFolderData(BaseModel):
    folder_id: int = Field(ge=2, le=255)
    folder_definition: TGFolderDefinition


class OutUpdateTelegramFolderResponse(TGFolderBaseResponse):
    folder: TGFolderData
