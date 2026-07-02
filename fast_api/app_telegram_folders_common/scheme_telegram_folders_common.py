from typing import List, Optional

from fastapi import HTTPException
from pydantic import BaseModel, Field, model_validator
from starlette import status


class TGAccountTLTConfigRef(BaseModel):
    config_name: str = Field(min_length=1)


class TGPeerRef(BaseModel):
    peer_id: Optional[int] = None
    username: Optional[str] = None
    peer_storage_type: Optional[str] = None

    @model_validator(mode="after")
    def validate_reference(self):
        if self.peer_id is None and not (self.username or "").strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="peer_id or username is required [ERROR]")
        return self


class TGFolderDefinition(BaseModel):
    title: str = Field(min_length=1, max_length=12)
    emoticon: Optional[str] = None
    color: Optional[int] = Field(default=None, ge=0)
    title_noanimate: bool = False
    contacts: bool = False
    non_contacts: bool = False
    groups: bool = False
    broadcasts: bool = False
    bots: bool = False
    exclude_muted: bool = False
    exclude_read: bool = False
    exclude_archived: bool = False
    pinned_peers: List[TGPeerRef] = Field(default_factory=list)
    include_peers: List[TGPeerRef] = Field(default_factory=list)
    exclude_peers: List[TGPeerRef] = Field(default_factory=list)


class TGAccountData(BaseModel):
    config_name: str
    telegram_account_id: Optional[int] = None
    username: Optional[str] = None
    first_name_cst: Optional[str] = None
    last_name_cst: Optional[str] = None
    phone_cst: Optional[str] = None
    account_type_cst: Optional[str] = None
    bot_cst: Optional[str] = None


class TGPeerData(BaseModel):
    peer_id: int
    username: Optional[str] = None
    title: Optional[str] = None
    first_name_cst: Optional[str] = None
    last_name_cst: Optional[str] = None
    phone_cst: Optional[str] = None
    bot_cst: Optional[str] = None
    peer_type_cst: str
    peer_storage_type: str
    peer_is_bot: bool = False


class TGFolderData(BaseModel):
    folder_id: int
    folder_kind: str
    title: str
    emoticon: Optional[str] = None
    color: Optional[int] = None
    title_noanimate: bool = False
    contacts: bool = False
    non_contacts: bool = False
    groups: bool = False
    broadcasts: bool = False
    bots: bool = False
    exclude_muted: bool = False
    exclude_read: bool = False
    exclude_archived: bool = False
    has_my_invites: bool = False
    pinned_peers: List[TGPeerData] = Field(default_factory=list)
    include_peers: List[TGPeerData] = Field(default_factory=list)
    exclude_peers: List[TGPeerData] = Field(default_factory=list)


class TGFolderCandidateData(BaseModel):
    peer: TGPeerData
    included: bool
    reasons: List[str] = Field(default_factory=list)


class TGPeerResolutionData(BaseModel):
    requested_peer: TGPeerRef
    resolved: bool
    peer: Optional[TGPeerData] = None
    error: Optional[str] = None


class TGFolderBaseResponse(BaseModel):
    message: str
    account: TGAccountData


class InFolderIdData(BaseModel):
    folder_id: int = Field(ge=2, le=255)


class InFolderPeersData(BaseModel):
    peers: List[TGPeerRef] = Field(min_length=1)
