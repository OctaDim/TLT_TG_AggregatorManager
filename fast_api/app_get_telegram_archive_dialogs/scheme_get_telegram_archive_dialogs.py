from typing import List, Optional

from pydantic import BaseModel, Field

from fast_api.app_telegram_folders_common.scheme_telegram_folders_common import TGFolderBaseResponse


class InGetTelegramArchiveDialogsData(BaseModel):
    dialogs_limit: int = Field(default=100, ge=1, le=1000)


class TGArchiveDialogData(BaseModel):
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
    last_message_id: Optional[int] = None
    last_message_date: Optional[str] = None
    last_message_text: str
    last_message_out: bool
    has_draft: bool


class OutGetTelegramArchiveDialogsResponse(TGFolderBaseResponse):
    folder_id: int
    dialogs_limit: int
    returned_count: int
    dialogs: List[TGArchiveDialogData]
