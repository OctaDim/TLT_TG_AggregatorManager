from typing import List

from pydantic import BaseModel, Field

from fast_api.app_telegram_folders_common.scheme_telegram_folders_common import (
    TGFolderBaseResponse,
    TGFolderCandidateData,
    TGFolderDefinition,
)


class InPreviewFolderCandidatesData(BaseModel):
    folder_definition: TGFolderDefinition
    dialogs_limit: int = Field(default=200, ge=1, le=1000)


class OutPreviewFolderCandidatesResponse(TGFolderBaseResponse):
    is_estimate: bool
    dialogs_limit: int
    included_count: int
    excluded_count: int
    candidates: List[TGFolderCandidateData]
