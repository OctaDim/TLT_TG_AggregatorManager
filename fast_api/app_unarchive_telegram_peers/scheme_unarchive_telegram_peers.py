from typing import List

from fast_api.app_telegram_folders_common.scheme_telegram_folders_common import (
    TGFolderBaseResponse,
    TGPeerData,
)


class OutUnarchiveTelegramPeersResponse(TGFolderBaseResponse):
    folder_id: int
    unarchived_count: int
    peers: List[TGPeerData]
