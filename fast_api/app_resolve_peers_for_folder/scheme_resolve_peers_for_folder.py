from typing import List

from pydantic import BaseModel, Field

from fast_api.app_telegram_folders_common.scheme_telegram_folders_common import (
    TGFolderBaseResponse,
    TGPeerRef,
    TGPeerResolutionData,
)


class InResolvePeersForFolderData(BaseModel):
    peers: List[TGPeerRef] = Field(min_length=1)


class OutResolvePeersForFolderResponse(TGFolderBaseResponse):
    resolved_count: int
    unresolved_count: int
    results: List[TGPeerResolutionData]
