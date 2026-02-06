import os

from configs.settings import TELETHON_OPTIONS, BASE_DIR
from utils_common.normalized_path import get_full_dir_normal_path


async def init_telethon_sessions_dir():
    telethon_sessions_dir = TELETHON_OPTIONS.BASE_TELETHON_SESSIONS_DIR
    tlt_sessions_dir_full_f_path = get_full_dir_normal_path(
        all_dir_str_parts=[BASE_DIR, telethon_sessions_dir])
    if not os.path.isdir(tlt_sessions_dir_full_f_path):
        os.makedirs(name=tlt_sessions_dir_full_f_path, exist_ok=True)
