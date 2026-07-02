from typing import List

from fast_api.app_telegram_folders_common.scheme_telegram_folders_common import (
    TGFolderBaseResponse,
    TGFolderData,
)


class OutGetTelegramFoldersResponse(TGFolderBaseResponse):
    tags_enabled: bool
    folders: List[TGFolderData]
