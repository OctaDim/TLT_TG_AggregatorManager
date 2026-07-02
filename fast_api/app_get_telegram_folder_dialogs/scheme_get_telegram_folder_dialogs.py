from typing import List, Optional

from pydantic import BaseModel, Field

from fast_api.app_telegram_folders_common.scheme_telegram_folders_common import (
    TGFolderBaseResponse,
    TGFolderData,
)


class InGetTelegramFolderDialogsData(BaseModel):
    folder_id: int = Field(ge=2, le=255)
    dialogs_limit: int = Field(default=100, ge=1, le=1000)


class TGFolderDialogData(BaseModel):
    config_name: str
    peer_id: int
    peer_type: str
    peer_storage_type: str
    peer_key: str
    peer_title: str
    peer_username: Optional[str] = None
    peer_first_name: Optional[str] = None
    peer_last_name: Optional[str] = None
    peer_phone: Optional[str] = None
    peer_is_bot: bool
    can_send: bool
    unread_count: int
    is_pinned: bool
    is_archived: bool
    folder_match_reason: str
    last_message_id: Optional[int] = None
    last_message_date: Optional[str] = None
    last_message_text: str
    last_message_out: bool
    has_draft: bool


class OutGetTelegramFolderDialogsResponse(TGFolderBaseResponse):
    folder: TGFolderData
    dialogs_limit: int
    scanned_dialogs_count: int
    returned_count: int
    membership_source: str
    snapshot_source: str
    snapshot_age_ms: float
    snapshot_wait_ms: float
    snapshot_scan_ms: float
    membership_filter_ms: float
    total_processing_ms: float
    dialogs: List[TGFolderDialogData]
