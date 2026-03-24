from typing import Dict, Union

from telethon import TelegramClient, types, functions

from configs.options import TELETHON_OPTIONS


async def get_tg_users_data_by_username(
        telethon_client: TelegramClient,
        username: str,
        telethon_config_name: str = None,
) -> Dict[str, Dict[str, Union[int, str]]]:
    matched_users_data = {}
    username = (username or "").lstrip("@").lower()

    try:
        user_obj = await telethon_client.get_entity(username)
        if user_obj:
            real_user_obj_flag = all([isinstance(user_obj, types.User),
                                      not user_obj.bot,
                                      not user_obj.deleted])
            if real_user_obj_flag:
                user_id_str = str(user_obj.id)
                user_data = {"username": user_obj.username,
                             "id": user_id_str,
                             "phone": user_obj.phone,
                             "first_name": user_obj.first_name,
                             "last_name": user_obj.last_name,
                             "bot": user_obj.bot}
                matched_users_data[user_id_str] = user_data
                if TELETHON_OPTIONS.LOG_TG_FOUND_USER_BY_USERNAME:
                    print(f"\nFound EXACT telegram user BY USERNAME [OK]:\n"
                          f"telethon_config_name: {telethon_config_name}\n"
                          f"user_obj.id: {user_id_str}\n"
                          f"user_obj.username: {user_obj.username}\n"
                          f"user_obj.first_name: {user_obj.first_name}\n"
                          f"user_obj.last_name: {user_obj.last_name}\n"
                          f"user_obj.phone: {user_obj.phone}\n")
    except Exception as error:
        print(f"Getting tg user id by username via get_entity [ERROR]:\n"
              f"error: {error}\n"
              f"telethon_client: {telethon_client}\n"
              f"tlt_config_name: {telethon_config_name}\n"
              f"username: {username}\n")
    return matched_users_data


async def request_tg_users_data_by_phone(
        telethon_client: TelegramClient,
        req_phone: str,
        telethon_config_name: str = None,
) -> Dict[str, Dict[str, Union[int, str]]]:
    matched_users_data = {}
    req_phone = req_phone or ""

    try:
        contact_obj = types.InputPhoneContact(
            client_id=0,  # 0 or any number
            first_name="[X] Temporary",  # Cannot be None, so temp used. Overrides orig tg contact first_name
            last_name="[X] Temporary",  # Cannot be None, so temp used. Overrides orig tg contact last_name
            phone=req_phone)
        req_func = functions.contacts.ImportContactsRequest([contact_obj])  # Imports users by !!!phone!!! only
        req_res = await telethon_client(req_func)
        if hasattr(req_res, "users") and req_res.users:
            # req_res_user_obj = req_res.users[0]
            for cur_user_obj in req_res.users:
                real_user_obj_flag = all([
                    isinstance(cur_user_obj, types.User),
                    not cur_user_obj.bot,
                    not cur_user_obj.deleted])

                if not real_user_obj_flag:
                    continue

                user_first_name = cur_user_obj.first_name
                user_last_name = cur_user_obj.last_name
                user_id_str = str(cur_user_obj.id)

                user_data = {"username": cur_user_obj.username,
                             "id": user_id_str,
                             "phone": cur_user_obj.phone,
                             "first_name": user_first_name,
                             "last_name": user_last_name,
                             "bot": cur_user_obj.bot}
                matched_users_data[user_id_str] = user_data

                req_func = functions.contacts.DeleteContactsRequest(
                    [cur_user_obj])
                await telethon_client(req_func)

                # if not user_first_name and not user_last_name:
                #     sub_req_func = functions.users.GetFullUserRequest(
                #         id=cur_user_obj.id)
                #     sub_req_res = await telethon_client(sub_req_func)
                #     if hasattr(sub_req_res, 'users') and sub_req_res.users:
                #         sub_req_user_obj = sub_req_res.users[0]
                #         user_first_name = sub_req_user_obj.first_name
                #         user_last_name = sub_req_user_obj.last_name

                if TELETHON_OPTIONS.LOG_TG_FOUND_USER_BY_PHONE:
                    print(
                        f"\nFound EXACT telegram user BY PHONE [OK]:\n"
                        f"telethon_config_name: {telethon_config_name}\n"
                        f"cur_user_obj.id: {user_id_str}\n"
                        f"user_obj.username: {cur_user_obj.username}\n"
                        f"cur_user_obj.first_name: {user_first_name}\n"
                        f"cur_user_obj.last_name: {user_last_name}\n"
                        f"cur_user_obj.phone: {cur_user_obj.phone}\n")
    except Exception as error:
        print(f"Getting tg users ids by phone via user import-delete request [ERROR]:\n"
              f"error: {error}\n"
              f"telethon_client: {telethon_client}\n"
              f"tlt_config_name: {telethon_config_name}\n"
              f"req_phone: {req_phone}\n")
    return matched_users_data


async def request_tg_users_data_by_name(
        telethon_client: TelegramClient,
        req_first_name: str,
        req_last_name: str,
        # req_phone: str,
        telethon_config_name: str = None,
) -> Dict[str, Dict[str, Union[int, str]]]:
    matched_users_data = {}

    req_first_name = req_first_name or ""
    req_last_name = req_last_name or ""
    # req_phone = req_phone or ""

    if req_first_name and req_last_name:
        name_query_str = f"{req_first_name} {req_last_name}"
    else:
        name_query_str = req_first_name or req_last_name

    if name_query_str:
        try:
            request_func = functions.contacts.SearchRequest(  # Finds by !!!name!!! only
                q=name_query_str,
                limit=TELETHON_OPTIONS.FIND_USERS_BY_NAME_LIMIT)
            request_res = await telethon_client(request_func)
            if hasattr(request_res, "users") and request_res.users:
                for cur_user_obj in request_res.users:
                    real_user_obj_flag = all([
                        isinstance(cur_user_obj, types.User),
                        not cur_user_obj.bot,
                        not cur_user_obj.deleted])

                    if not real_user_obj_flag:
                        continue

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
                        user_id_str = str(cur_user_obj.id)
                        user_data = {"username": cur_user_obj.username,
                                     "id": user_id_str,
                                     "phone": cur_user_obj.phone,
                                     "first_name": cur_user_obj.first_name,
                                     "last_name": cur_user_obj.last_name,
                                     "bot": cur_user_obj.bot}
                        matched_users_data[user_id_str] = user_data

                        if TELETHON_OPTIONS.LOG_TG_FOUND_USER_BY_NAME:
                            print(
                                f"\nFound PROBABLE telegram user BY NAME [OK]:\n"
                                f"telethon_config_name: {telethon_config_name}\n"
                                f"cur_user_obj.id: {user_id_str}\n"
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
    return matched_users_data
