from typing import List

from fast_api.app_telegram_folders_common.scheme_telegram_folders_common import (
    TGFolderBaseResponse,
    TGPeerData,
)


class OutArchiveTelegramPeersResponse(TGFolderBaseResponse):
    folder_id: int
    archived_count: int
    peers: List[TGPeerData]
