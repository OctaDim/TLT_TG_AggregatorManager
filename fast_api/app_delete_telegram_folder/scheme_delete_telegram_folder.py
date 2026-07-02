from fast_api.app_telegram_folders_common.scheme_telegram_folders_common import (
    TGFolderBaseResponse,
)


class OutDeleteTelegramFolderResponse(TGFolderBaseResponse):
    folder_id: int
    deleted: bool
