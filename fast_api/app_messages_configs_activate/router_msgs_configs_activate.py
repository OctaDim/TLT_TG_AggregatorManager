from typing import Dict

from fastapi import APIRouter
from starlette import status
from starlette.responses import JSONResponse

from configs.console_colors import CONSOLE_COLORS
from configs.options import API_OPTIONS
from db_postgres.postgres_queries.qry_update_telethon_messages_used import (
    update_telethon_messages_used_qry)
from fast_api.app_auth.funcs_auth import (
    verify_auth_username_password)
from fast_api.app_auth.scheme_auth import (
    AuthData)
from fast_api.app_messages_configs_activate.scheme_msgs_configs_activate import (
    InActivateMsgsConfigs)
from fast_api.app_web_account.scheme_web_account import InWebAccountData

base_url_name = API_OPTIONS.API_BASE_URL_NAME
rtr_activate_messages_configs = APIRouter(prefix=f"/{base_url_name}",
                                          tags=["TELEGRAM TLT ENDPOINTS"])


@rtr_activate_messages_configs.post("/activate_messages_configs")
async def activate_messages_configs_router(
        auth_data: AuthData,
        web_account_data: InWebAccountData,
        active_msgs_configs: InActivateMsgsConfigs
) -> JSONResponse:
    await verify_auth_username_password(
        username=auth_data.username,
        password=auth_data.password)

    web_account_id = web_account_data.web_account_id
    web_account_username = web_account_data.web_account_username

    tlt_configs_names = active_msgs_configs.telethon_configs_names

    activated_configs = []
    skipped_configs = []
    activate_configs_logs: Dict[str, Dict[str, str]] = {}

    for cur_config_name in tlt_configs_names:
        try:
            activate_result = await update_telethon_messages_used_qry(
                telethon_config_name=cur_config_name,
                update_data={"used_for_messages": True})

            if activate_result:
                activated_configs.append(cur_config_name)
                activate_log = (f"Message used config activated [OK]:\n"
                                f"cur_config_name: {cur_config_name}\n")
            else:

                skipped_configs.append(cur_config_name)
                activate_log = (f"Message used config not activated [ERROR]:\n"
                                f"cur_config_name: {cur_config_name}\n")
        except Exception as error:
            skipped_configs.append(cur_config_name)
            activate_log = (f"Message used config activation [ERROR]:\n"
                            f"error: {error}\n"
                            f"cur_1config_name: {cur_config_name}\n")
        activate_configs_logs[cur_config_name] = {
            "activate_log": activate_log}

    blue_clr = CONSOLE_COLORS.BRIGHT_BLUE
    yellow_clr = CONSOLE_COLORS.BRIGHT_YELLOW
    green_clr = CONSOLE_COLORS.BRIGHT_GREEN
    reset_clr = CONSOLE_COLORS.RESET
    magenta_clr = CONSOLE_COLORS.BRIGHT_MAGENTA

    all_configs_total = len(tlt_configs_names)
    print(f"\n{yellow_clr}All activated configs "
          f"[{len(activated_configs)}/{all_configs_total}]:{reset_clr}")
    for cur_activated_config in activated_configs:
        print(f"{yellow_clr}{cur_activated_config}{reset_clr}")

    print(f"\n{magenta_clr}All skipped configs "
          f"[{len(skipped_configs)}/{all_configs_total}]:{reset_clr}")
    for cur_skipped_config in skipped_configs:
        print(f"{magenta_clr}{cur_skipped_config}{reset_clr}")

    if not tlt_configs_names:
        activate_msg = "Empty TLT configs list to activate for messages [OK]:"
    elif activated_configs and not skipped_configs:
        activate_msg = "All TLT configs activated successfully [OK]:"
    elif activated_configs and skipped_configs:
        activate_msg = "TLT TLT configs activated partly [OK]:"
    else:
        activate_msg = "All TLT configs not connected [ERROR]:"

    json_response = JSONResponse(
        content={"activate_msg": activate_msg,
                 "username": auth_data.username,
                 "web_account_id": web_account_id,
                 "web_account_username": web_account_username,
                 "tlt_configs_names": tlt_configs_names,
                 "activated_configs": activated_configs,
                 "skipped_configs": skipped_configs,
                 "activate_configs_logs": activate_configs_logs},
        status_code=status.HTTP_200_OK)
    print(f"{activate_msg}\n"
          f"tlt_configs_names: {tlt_configs_names}\n"
          f"activated_configs: {activated_configs}\n"
          f"skipped_configs: {skipped_configs}\n"
          f"activate_configs_logs: {activate_configs_logs}\n")
    return json_response
