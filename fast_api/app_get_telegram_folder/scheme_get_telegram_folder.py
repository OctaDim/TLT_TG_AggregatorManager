from fast_api.app_telegram_folders_common.scheme_telegram_folders_common import (
    TGFolderBaseResponse,
    TGFolderData,
)


class OutGetTelegramFolderResponse(TGFolderBaseResponse):
    folder: TGFolderData
