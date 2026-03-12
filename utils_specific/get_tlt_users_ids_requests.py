from typing import List

from telethon import TelegramClient, types, functions

from configs.settings import TELETHON_OPTIONS


async def get_tg_users_ids_by_username(
        telethon_client: TelegramClient,
        username: str,
        telethon_config_name: str = None,
) -> List[int]:
    matched_users_ids = []
    username = (username or "").lstrip("@").lower()

    try:
        user_obj = await telethon_client.get_entity(username)
        if user_obj:
            matched_users_ids.append(user_obj.id)
            if TELETHON_OPTIONS.LOG_TG_FOUND_USER_BY_USERNAME:
                print(f"\nFound EXACT telegram user BY USERNAME:\n"
                      f"telethon_config_name: {telethon_config_name}\n"
                      f"user_obj.id: {user_obj.id}\n"
                      f"user_obj.first_name: {user_obj.first_name}\n"
                      f"user_obj.last_name: {user_obj.last_name}\n"
                      f"user_obj.phone: {user_obj.phone}\n")
    except Exception as error:
        print(f"Getting tg user id by username via get_entity [ERROR]:\n"
              f"error: {error}\n"
              f"telethon_client: {telethon_client}\n"
              f"tlt_config_name: {telethon_config_name}\n"
              f"username: {username}\n")
    return matched_users_ids


async def request_tg_users_ids_by_phone(
        telethon_client: TelegramClient,
        req_phone: str,
        telethon_config_name: str = None,
) -> List[int]:
    matched_users_ids = []
    req_phone = req_phone or ""

    try:
        contact_obj = types.InputPhoneContact(
            client_id=0,  # 0 or any number
            first_name="",  # empty to get default orig contact first_name from telegram, not overridden
            last_name="",  # empty to get default orig contact last_name from telegram, not overridden
            phone=req_phone)
        request_func = functions.contacts.ImportContactsRequest([contact_obj])  # Imports users by !!!phone!!! only
        request_res = await telethon_client(request_func)
        if request_res.users:
            for cur_user_obj in request_res.users:
                matched_users_ids.append(cur_user_obj.id)
                request_func = functions.contacts.DeleteContactsRequest([cur_user_obj])
                await telethon_client(request_func)
                if TELETHON_OPTIONS.LOG_TG_FOUND_USER_BY_PHONE:
                    print(f"\nFound EXACT telegram user BY PHONE:\n"
                          f"telethon_config_name: {telethon_config_name}\n"
                          f"cur_user_obj.id: {cur_user_obj.id}\n"
                          f"cur_user_obj.first_name: {cur_user_obj.first_name}\n"
                          f"cur_user_obj.last_name: {cur_user_obj.last_name}\n"
                          f"cur_user_obj.phone: {cur_user_obj.phone}\n")
    except Exception as error:
        print(f"Getting tg users ids by phone via user import-delete request [ERROR]:\n"
              f"error: {error}\n"
              f"telethon_client: {telethon_client}\n"
              f"tlt_config_name: {telethon_config_name}\n"
              f"req_phone: {req_phone}\n")
    return matched_users_ids


async def request_tg_users_ids_by_name(
        telethon_client: TelegramClient,
        req_first_name: str,
        req_last_name: str,
        # req_phone: str,
        telethon_config_name: str = None,
) -> List[int]:
    matched_users_ids = []

    req_first_name = req_first_name or ""
    req_last_name = req_last_name or ""
    # req_phone = req_phone or ""

    if req_first_name and req_last_name:
        name_query_str = f"{req_first_name} {req_last_name}"
    else:
        name_query_str = req_first_name or req_last_name

    if name_query_str:
        try:
            request_func = functions.contacts.SearchRequest(q=name_query_str, limit=300)  # Finds by !!!name!!! only
            request_res = await telethon_client(request_func)

            for cur_user_obj in request_res.users:
                real_user_obj_flag = all([isinstance(cur_user_obj, types.User),
                                          not cur_user_obj.bot,
                                          not cur_user_obj.deleted])
                if real_user_obj_flag:
                    cur_first_name = (cur_user_obj.first_name or "").lower()
                    cur_last_name = (cur_user_obj.last_name or "").lower()
                    # cur_phone = cur_user_obj.phone or ""

                    low_tg_first_name = req_first_name.lower()
                    low_tg_last_name = req_last_name.lower()
                    # no_plus_tg_phone = req_phone.replace("+", "")

                    first_name_flag = bool(req_first_name) and bool(cur_first_name)
                    last_name_flag = bool(req_last_name) and bool(cur_last_name)
                    # phone_flag = bool(req_phone) and bool(cur_phone)

                    name_match_flag = all([
                        # first_name_flag and (low_tg_first_name in cur_first_name),  # including first name
                        first_name_flag and (low_tg_first_name == cur_first_name),  # exact first name
                        # last_name_flag and (low_tg_last_name == cur_last_name),  # including last name
                        last_name_flag and (low_tg_last_name in cur_last_name)])  # exact last name

                    if name_match_flag:
                        matched_users_ids.append(cur_user_obj.id)
                        if TELETHON_OPTIONS.LOG_TG_FOUND_USER_BY_NAME:
                            print(f"\nFound PROBABLE telegram user BY NAME:\n"
                                  f"telethon_config_name: {telethon_config_name}\n"
                                  f"cur_user_obj.id: {cur_user_obj.id}\n"
                                  f"cur_user_obj.first_name: {cur_user_obj.first_name}\n"
                                  f"cur_user_obj.last_name: {cur_user_obj.last_name}\n"
                                  f"cur_user_obj.phone: {cur_user_obj.phone}\n")
        except Exception as error:
            print(f"Getting tg users ids by name via search request [ERROR]:\n"
                  f"error: {error}\n"
                  f"telethon_client: {telethon_client}\n"
                  f"tlt_config_name: {telethon_config_name}\n"
                  # f"req_phone: {req_phone}\n"
                  f"req_first_name: {req_first_name}\n"
                  f"req_last_name: {req_last_name}\n")
    return matched_users_ids
