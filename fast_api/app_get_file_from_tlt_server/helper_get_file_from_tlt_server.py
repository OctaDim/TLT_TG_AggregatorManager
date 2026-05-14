import mimetypes
from typing import Dict

from aiofiles import os as aiofiles_os

from configs.environments import BASE_DIR
from configs.options import TELETHON_OPTIONS
from utils_common.normalized_path import (
    get_full_dir_normal_path, get_full_file_normal_path)


async def get_tlt_server_saved_file(
        extra_file_name: str,
        custom_file_name: str,
        telethon_config_name: str
) -> Dict[str, str] | None:
    file_result = {"file_path": "",
                   "file_name": "",
                   "file_mime_type": "",
                   "get_file_error": ""}

    tlt_arch_file_extra_path = ""
    try:
        base_tlt_arch_files_dir = TELETHON_OPTIONS.ARCHIVE_TLT_TG_FILES_DIR
        tlt_arch_dir_path = get_full_dir_normal_path(
            all_dir_str_parts=[BASE_DIR, base_tlt_arch_files_dir])
        await aiofiles_os.makedirs(tlt_arch_dir_path, exist_ok=True)

        tlt_arch_file_extra_path = get_full_file_normal_path(
            all_dir_str_parts=[tlt_arch_dir_path],
            file_name_with_ext=extra_file_name)
        tlt_file_exists = await aiofiles_os.path.isfile(tlt_arch_file_extra_path)

        if not tlt_file_exists:
            get_file_error = (
                f"TLT server saved file not found [ERROR]: \n"
                f"extra_file_name: {extra_file_name} \n"
                f"custom_file_name: {custom_file_name} \n"
                f"tlt_arch_file_extra_path: {tlt_arch_file_extra_path} \n"
                f"tlt_file_exists: {tlt_file_exists} \n"
                f"telethon_config_name: {telethon_config_name}\n")
            print(get_file_error)
            file_result.update({"get_file_error": get_file_error})
            return file_result

        file_name = custom_file_name if custom_file_name else extra_file_name
        file_mime_type, encoding = mimetypes.guess_type(
            url=tlt_arch_file_extra_path,
            strict=True)
        if not file_mime_type:
            file_mime_type = "application/octet-stream"

        file_result.update({"file_path": tlt_arch_file_extra_path,
                            "file_name": file_name,
                            "file_mime_type": file_mime_type})
        return file_result
    except Exception as error:
        error_msg = (f"Getting TLT server saved file [ERROR]: \n"
                     f"error: {error} \n"
                     f"extra_file_name: {extra_file_name} \n"
                     f"custom_file_name: {custom_file_name} \n"
                     f"tlt_arch_file_extra_path: {tlt_arch_file_extra_path} \n"
                     f"telethon_config_name: {telethon_config_name}\n")
        print(error_msg)
        file_result.update({"get_file_error": error_msg})
        return file_result
