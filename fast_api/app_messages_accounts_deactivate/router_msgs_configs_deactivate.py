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
from fast_api.app_messages_accounts_deactivate.scheme_msgs_configs_deactivate import (
    InDeactivateMsgsConfigs)
from fast_api.app_web_account.scheme_web_account import InWebAccountData

base_url_name = API_OPTIONS.API_BASE_URL_NAME
rtr_deactivate_messages_configs = APIRouter(prefix=f"/{base_url_name}",
                                            tags=["TELEGRAM TLT ENDPOINTS"])


@rtr_deactivate_messages_configs.post("/deactivate_messages_configs")
async def deactivate_messages_configs_router(
        auth_data: AuthData,
        web_account_data: InWebAccountData,
        deactivate_msgs_configs: InDeactivateMsgsConfigs
) -> JSONResponse:
    await verify_auth_username_password(
        username=auth_data.username,
        password=auth_data.password)

    web_account_id = web_account_data.web_account_id
    web_account_username = web_account_data.web_account_username

    tlt_configs_names = deactivate_msgs_configs.telethon_configs_names

    deactivated_configs = []
    skipped_configs = []
    deactivate_configs_logs: Dict[str, Dict[str, str]] = {}

    for cur_config_name in tlt_configs_names:
        try:
            deactivate_result = await update_telethon_messages_used_qry(
                telethon_config_name=cur_config_name,
                update_data={"used_for_messages": False})
            if deactivate_result:
                deactivated_configs.append(cur_config_name)
                deactivate_log = (f"Message used config deactivated [OK]:\n"
                                  f"cur_config_name: {cur_config_name}\n")
            else:
                skipped_configs.append(cur_config_name)
                deactivate_log = (f"Message used config not deactivated [ERROR]:\n"
                                  f"cur_config_name: {cur_config_name}\n")
        except Exception as error:
            skipped_configs.append(cur_config_name)
            deactivate_log = (f"Message used config deactivation [ERROR]:\n"
                              f"error: {error}\n"
                              f"cur_config_name: {cur_config_name}\n")
        deactivate_configs_logs[cur_config_name] = {
            "deactivate_log": deactivate_log}

    blue_clr = CONSOLE_COLORS.BRIGHT_BLUE
    yellow_clr = CONSOLE_COLORS.BRIGHT_YELLOW
    green_clr = CONSOLE_COLORS.BRIGHT_GREEN
    reset_clr = CONSOLE_COLORS.RESET
    magenta_clr = CONSOLE_COLORS.BRIGHT_MAGENTA

    all_configs_total = len(tlt_configs_names)
    print(f"\n{yellow_clr}All deactivated configs "
          f"[{len(deactivated_configs)}/{all_configs_total}]:{reset_clr}")
    for cur_activated_config in deactivated_configs:
        print(f"{yellow_clr}{cur_activated_config}{reset_clr}")

    print(f"\n{magenta_clr}All skipped configs "
          f"[{len(skipped_configs)}/{all_configs_total}]:{reset_clr}")
    for cur_skipped_config in skipped_configs:
        print(f"{magenta_clr}{cur_skipped_config}{reset_clr}")

    if not tlt_configs_names:
        deactivate_msg = "Empty TLT configs list to deactivate for messages [OK]:"
    elif deactivated_configs and not skipped_configs:
        deactivate_msg = "All TLT configs deactivated successfully [OK]:"
    elif deactivated_configs and skipped_configs:
        deactivate_msg = "TLT TLT configs deactivated partly [OK]:"
    else:
        deactivate_msg = "All TLT configs not deactivated [ERROR]:"

    json_response = JSONResponse(
        content={"deactivate_msg": deactivate_msg,
                 "username": auth_data.username,
                 "web_account_id": web_account_id,
                 "web_account_username": web_account_username,
                 "tlt_configs_names": tlt_configs_names,
                 "deactivated_configs": deactivated_configs,
                 "skipped_configs": skipped_configs,
                 "deactivate_configs_logs": deactivate_configs_logs},
        status_code=status.HTTP_200_OK)
    print(f"{deactivate_msg}\n"
          f"tlt_configs_names: {tlt_configs_names}\n"
          f"deactivated_configs: {deactivated_configs}\n"
          f"skipped_configs: {skipped_configs}\n"
          f"deactivate_configs_logs: {deactivate_configs_logs}\n")
    return json_response
