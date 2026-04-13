import asyncio
from abc import ABC

import qrcode
from pydantic.dataclasses import dataclass
from telethon import TelegramClient

from configs.enums import QR_CODE_ERROR_CORRECTION
from configs.environments import BASE_DIR
from configs.options import TELETHON_OPTIONS
from telethon_manager.telethon_client_config import TelethonConfig
from utils_common.create_save_qrcode_image_file import save_qrcode_image
from utils_common.normalized_path import get_full_file_normal_path
from utils_common.validate_dir_file import check_create_dir_by_filename_async


@dataclass
class AuthResponse:
    is_authorised: bool = False
    requires_action: bool = False
    auth_by_phone: bool = False
    auth_by_qrcode: bool = False
    auth_via_console: bool = False
    phone_code_hash: str | None = None
    qrcode_url: str | None = None
    qrcode_fpath: str | None = None
    is_auth_error: bool = False
    auth_message: str = ""
    auth_error: str = ""


class AuthDriver(ABC):
    def __init__(self,
                 telethon_user_client: TelegramClient,
                 telethon_config: TelethonConfig):
        self.telethon_user_client = telethon_user_client
        self.telethon_config = telethon_config

    async def auth_user_client_via_driver(self) -> AuthResponse:
        pass


class TltAuthWebQRAndPhoneDriver(AuthDriver):
    async def auth_user_client_via_driver(self) -> AuthResponse:
        """QRCode plus Phone authorisation driver method"""
        config_name = self.telethon_config.name
        session_str = self.telethon_config.session_string
        session_str_info = f"...{session_str[-15:]}" if session_str else None
        telegram_phone = self.telethon_config.phone
        auth_type = self.telethon_config.authorisation_type
        user_client = self.telethon_user_client

        client_is_user_authorised = await user_client.is_user_authorized()  # Redundant
        if client_is_user_authorised:
            auth_msg = "WEB QR+Phone Auth Driver: Client authorised initially"
            auth_resp = AuthResponse(is_authorised=True,
                                     requires_action=False,
                                     auth_by_phone=True,
                                     auth_by_qrcode=True,
                                     auth_via_console=False,
                                     phone_code_hash=None,
                                     qrcode_url=None,
                                     qrcode_fpath=None,
                                     is_auth_error=False,
                                     auth_message=auth_msg,
                                     auth_error="")
            return auth_resp

        qr_code_login = None
        qr_code_url = None
        try:
            print("Telethon user client auth via WEB QR+Phone driver:")
            # By QRCode via WEB (QRCode+Phone)
            qr_code_login = await user_client.qr_login(
                ignored_ids=None)
            qr_code_url = qr_code_login.url
            print(f"Authorisation QRCode created successfully [OK]:\n"
                  f"qr_code_login: {qr_code_login}\n"
                  f"qr_code_url: {qr_code_url}\n")

            # Saving QRCode image file
            qrcode_thread_timeout = TELETHON_OPTIONS.WAIT_FOR_QRCODE_OPS_TIMEOUT_SEC
            temp_qrcode_imgs_dir = TELETHON_OPTIONS.TEMP_AUTH_QRCODE_IMGS_DIR
            qr_code_img_size = TELETHON_OPTIONS.QR_CODE_IMAGE_SIZE

            qrcode_img_file_path = get_full_file_normal_path(
                all_dir_str_parts=[BASE_DIR, temp_qrcode_imgs_dir],
                file_name_with_ext=f"{config_name}.png")
            await check_create_dir_by_filename_async(qrcode_img_file_path)
            qrcode_saved_fpath = await asyncio.wait_for(
                fut=asyncio.to_thread(save_qrcode_image,
                                      qr_code_url=qr_code_url,
                                      full_file_path=qrcode_img_file_path,
                                      qrcode_image_size=qr_code_img_size,
                                      qrcode_fill_color="#2B94FF",
                                      qrcode_back_color="white"),
                timeout=qrcode_thread_timeout)

            # By Phone via WEB (QRCode+Phone)
            request_sent_code = await user_client.send_code_request(
                phone=telegram_phone,
                force_sms=False,  # Deprecated
                _retry_count=0)
            phone_code_hash = request_sent_code.phone_code_hash
            print(f"Phone authorisation code sent to phone [OK]:\n"
                  f"request_sent_code: {request_sent_code}\n")

            if qrcode_saved_fpath:
                auth_msg = ("WEB QR+Phone Auth Driver: "
                            "QRCode created, Phone code sent, "
                            "waiting scanning qrcode or entering phone code")
                auth_resp = AuthResponse(is_authorised=False,
                                         requires_action=True,
                                         auth_by_phone=True,
                                         auth_by_qrcode=True,
                                         auth_via_console=False,
                                         phone_code_hash=phone_code_hash,
                                         qrcode_url=qr_code_url,
                                         qrcode_fpath=qrcode_saved_fpath,
                                         is_auth_error=False,
                                         auth_message=auth_msg,
                                         auth_error="")
            else:  # if not qrcode_saved_fpath:
                auth_msg = ("WEB QR+Phone Auth Driver: "
                            "QRCode created but not saved, Phone code sent,"
                            "only authorisation by phone code accessible")
                auth_resp = AuthResponse(is_authorised=False,
                                         requires_action=True,
                                         auth_by_phone=True,
                                         auth_by_qrcode=False,
                                         auth_via_console=False,
                                         phone_code_hash=phone_code_hash,
                                         qrcode_url=qr_code_url,
                                         qrcode_fpath=qrcode_saved_fpath,
                                         is_auth_error=False,
                                         auth_message=auth_msg,
                                         auth_error="")
            return auth_resp
        except Exception as error:
            error_log = (f"\n\n⚠️ Web QR+Phone Auth Driver [ERROR]:\n"
                         f"error: {error}\n"
                         f"config_name: {config_name}\n"
                         f"telegram_phone: {telegram_phone}\n"
                         f"user_client: {user_client}\n"
                         f"client_is_user_authorised: {client_is_user_authorised}\n"
                         f"auth_type: {auth_type}\n"
                         f"qr_code_login: {qr_code_login}\n"
                         f"qr_code_url: {qr_code_url}\n"
                         f"session_str_info: {session_str_info}\n")
            auth_resp = AuthResponse(is_authorised=False,
                                     requires_action=False,
                                     auth_by_phone=True,
                                     auth_by_qrcode=True,
                                     auth_via_console=False,
                                     phone_code_hash=None,
                                     qrcode_url=None,
                                     qrcode_fpath=None,
                                     is_auth_error=True,
                                     auth_message="",
                                     auth_error=error_log)
            print(error_log)
            return auth_resp


class TltAuthWebQRCodeDriver(AuthDriver):
    async def auth_user_client_via_driver(self) -> AuthResponse:
        """QRCode authorisation driver method"""
        config_name = self.telethon_config.name
        session_str = self.telethon_config.session_string
        session_str_info = f"...{session_str[-15:]}" if session_str else None
        telegram_phone = self.telethon_config.phone
        auth_type = self.telethon_config.authorisation_type
        user_client = self.telethon_user_client

        client_is_user_authorised = await user_client.is_user_authorized()  # Redundant
        if client_is_user_authorised:
            auth_msg = "WEB QRCode Auth Driver: Client authorised initially"
            auth_resp = AuthResponse(is_authorised=True,
                                     requires_action=False,
                                     auth_by_phone=False,
                                     auth_by_qrcode=True,
                                     auth_via_console=False,
                                     phone_code_hash=None,
                                     qrcode_url=None,
                                     qrcode_fpath=None,
                                     is_auth_error=False,
                                     auth_message=auth_msg,
                                     auth_error="")
            return auth_resp

        qr_code_login = None
        qr_code_url = None
        try:
            # By QRCode via WEB
            print("Telethon user client auth via WEB QRCode driver:")
            qr_code_login = await user_client.qr_login(
                ignored_ids=None)
            qr_code_url = qr_code_login.url
            print(f"Authorisation QRCode created successfully [OK]:\n"
                  f"qr_code_login: {qr_code_login}\n"
                  f"qr_code_url: {qr_code_url}\n")

            # Saving QRCode image file
            qrcode_thread_timeout = TELETHON_OPTIONS.WAIT_FOR_QRCODE_OPS_TIMEOUT_SEC
            temp_qrcode_imgs_dir = TELETHON_OPTIONS.TEMP_AUTH_QRCODE_IMGS_DIR
            qr_code_img_size = TELETHON_OPTIONS.QR_CODE_IMAGE_SIZE

            qrcode_img_file_path = get_full_file_normal_path(
                all_dir_str_parts=[BASE_DIR, temp_qrcode_imgs_dir],
                file_name_with_ext=f"{config_name}.png")
            await check_create_dir_by_filename_async(qrcode_img_file_path)
            qrcode_saved_res = await asyncio.wait_for(
                fut=asyncio.to_thread(save_qrcode_image,
                                      qr_code_url=qr_code_url,
                                      full_file_path=qrcode_img_file_path,
                                      qrcode_image_size=qr_code_img_size,
                                      qrcode_fill_color="#2B94FF",
                                      qrcode_back_color="white"),
                timeout=qrcode_thread_timeout)
            if qrcode_saved_res:
                auth_msg = ("WEB QRCode Auth Driver: QRCode created, "
                            "waiting scanning")
                auth_resp = AuthResponse(is_authorised=False,
                                         requires_action=True,
                                         auth_by_phone=False,
                                         auth_by_qrcode=True,
                                         auth_via_console=False,
                                         phone_code_hash=None,
                                         qrcode_url=qr_code_url,
                                         qrcode_fpath=qrcode_saved_res,
                                         is_auth_error=False,
                                         auth_message=auth_msg,
                                         auth_error="")
                return auth_resp
            else:  # if not qrcode_saved_res:
                auth_error = ("WEB QRCode Auth Driver: QRCode created "
                              "but not saved")
                auth_resp = AuthResponse(is_authorised=False,
                                         requires_action=False,
                                         auth_by_phone=False,
                                         auth_by_qrcode=True,
                                         auth_via_console=False,
                                         phone_code_hash=None,
                                         qrcode_url=qr_code_url,
                                         qrcode_fpath=qrcode_saved_res,
                                         is_auth_error=True,
                                         auth_message="",
                                         auth_error=auth_error)
                return auth_resp
        except Exception as error:
            error_log = (f"\n\n⚠️ Web QRCode Auth Driver [ERROR]:\n"
                         f"error: {error}\n"
                         f"config_name: {config_name}\n"
                         f"telegram_phone: {telegram_phone}\n"
                         f"user_client: {user_client}\n"
                         f"client_is_user_authorised: {client_is_user_authorised}\n"
                         f"auth_type: {auth_type}\n"
                         f"qr_code_login: {qr_code_login}\n"
                         f"qr_code_url: {qr_code_url}\n"
                         f"session_str_info: {session_str_info}\n")
            auth_resp = AuthResponse(is_authorised=False,
                                     requires_action=False,
                                     auth_by_phone=False,
                                     auth_by_qrcode=True,
                                     auth_via_console=False,
                                     phone_code_hash=None,
                                     qrcode_url=None,
                                     qrcode_fpath=None,
                                     is_auth_error=True,
                                     auth_message="",
                                     auth_error=error_log)
            print(error_log)
            return auth_resp


class TltAuthWebPhoneDriver(AuthDriver):
    async def auth_user_client_via_driver(self) -> AuthResponse:
        """Phone authorisation driver method"""
        config_name = self.telethon_config.name
        session_str = self.telethon_config.session_string
        session_str_info = f"...{session_str[-15:]}" if session_str else None
        telegram_phone = self.telethon_config.phone
        auth_type = self.telethon_config.authorisation_type
        user_client = self.telethon_user_client

        client_is_user_authorised = await user_client.is_user_authorized()  # Redundant
        if client_is_user_authorised:
            auth_msg = "WEB Phone Auth Driver: Client authorised initially"
            auth_resp = AuthResponse(is_authorised=True,
                                     requires_action=False,
                                     auth_by_phone=True,
                                     auth_by_qrcode=False,
                                     auth_via_console=False,
                                     phone_code_hash=None,
                                     qrcode_url=None,
                                     qrcode_fpath=None,
                                     is_auth_error=False,
                                     auth_message=auth_msg,
                                     auth_error="")
            return auth_resp

        qr_code_login = None
        qr_code_url = None
        try:
            # By Phone via WEB
            print("Telethon user client auth via WEB Phone driver:")
            request_sent_code = await user_client.send_code_request(
                phone=telegram_phone,
                force_sms=False,  # Deprecated
                _retry_count=0)
            phone_code_hash = request_sent_code.phone_code_hash
            print(f"Phone authorisation code sent to phone [OK]:\n"
                  f"request_sent_code: {request_sent_code}\n")
            auth_msg = "WEB Phone Auth:  Phone code sent to telegram"
            auth_resp = AuthResponse(is_authorised=False,
                                     requires_action=True,
                                     auth_by_phone=True,
                                     auth_by_qrcode=False,
                                     auth_via_console=False,
                                     phone_code_hash=phone_code_hash,
                                     qrcode_url=None,
                                     qrcode_fpath=None,
                                     is_auth_error=False,
                                     auth_message=auth_msg,
                                     auth_error="")
            return auth_resp
        except Exception as error:
            error_log = (f"\n\n⚠️ Web Phone Auth Driver [ERROR]:\n"
                         f"error: {error}\n"
                         f"config_name: {config_name}\n"
                         f"telegram_phone: {telegram_phone}\n"
                         f"user_client: {user_client}\n"
                         f"client_is_user_authorised: {client_is_user_authorised}\n"
                         f"auth_type: {auth_type}\n"
                         f"qr_code_login: {qr_code_login}\n"
                         f"qr_code_url: {qr_code_url}\n"
                         f"session_str_info: {session_str_info}\n")
            auth_resp = AuthResponse(is_authorised=False,
                                     requires_action=False,
                                     auth_by_phone=True,
                                     auth_by_qrcode=False,
                                     auth_via_console=False,
                                     phone_code_hash=None,
                                     qrcode_url=None,
                                     qrcode_fpath=None,
                                     is_auth_error=True,
                                     auth_message="",
                                     auth_error=error_log)
            print(error_log)
            return auth_resp


class TltAuthConsoleDriver(AuthDriver):
    async def auth_user_client_via_driver(self) -> AuthResponse:
        auth_thread_timeout = TELETHON_OPTIONS.WAIT_FOR_TG_AUTH_TREADS_TIMEOUT_SEC

        config_name = self.telethon_config.name
        session_str = self.telethon_config.session_string
        session_str_info = f"...{session_str[-15:]}" if session_str else None
        telegram_phone = self.telethon_config.phone
        auth_type = self.telethon_config.authorisation_type
        user_client = self.telethon_user_client

        client_is_user_authorised = await user_client.is_user_authorized()
        if client_is_user_authorised:
            auth_msg = "Console Auth Driver: Client authorised initially"
            auth_resp = AuthResponse(is_authorised=True,
                                     requires_action=False,
                                     auth_by_phone=False,
                                     auth_by_qrcode=False,
                                     auth_via_console=True,
                                     phone_code_hash=None,
                                     qrcode_url=None,
                                     qrcode_fpath=None,
                                     is_auth_error=False,
                                     auth_message=auth_msg,
                                     auth_error="")
            return auth_resp

        auth_type_choice = None
        request_sent_code = None
        phone_signed_in_user = None
        qr_code_login = None
        qr_code_url = None
        qr_code = None
        qrcode_signed_in_user = None
        try:
            input_text = (f"Choose authorisation type for "
                          f"phone: {telegram_phone}, config name: {config_name}:\n"
                          f"1 - by telephone \n"
                          f"2 - by QR code \n"
                          f"3 - skip client\n"
                          f"Enter your choice: ")
            auth_type_choice = await asyncio.wait_for(
                fut=asyncio.to_thread(input, input_text),
                timeout=auth_thread_timeout)

            if auth_type_choice == "1" and telegram_phone:  # By Phone via Console
                print("Telethon user client authorising via phone:")
                request_sent_code = await user_client.send_code_request(
                    phone=telegram_phone,
                    force_sms=False,  # Deprecated
                    _retry_count=0)
                phone_code_hash = request_sent_code.phone_code_hash
                print(f"Phone authorisation code sent to phone [OK]:\n"
                      f"request_sent_code: {request_sent_code}\n")

                input_text = "Enter Telegram code: "
                phone_auth_code = await asyncio.wait_for(
                    fut=asyncio.to_thread(input, input_text),
                    timeout=auth_thread_timeout)

                phone_signed_in_user = await user_client.sign_in(
                    phone=telegram_phone,
                    code=phone_auth_code,
                    password=None,
                    bot_token=None,
                    phone_code_hash=phone_code_hash)
                print(f"Phone user client authorised successfully [OK]:\n"
                      f"request_sent_code: {request_sent_code}\n"
                      f"phone_signed_in_user: {phone_signed_in_user}\n")

                auth_msg = "Console Phone Auth Driver: Authorised"
                auth_resp = AuthResponse(is_authorised=True,
                                         requires_action=False,
                                         auth_by_phone=True,
                                         auth_by_qrcode=False,
                                         auth_via_console=True,
                                         phone_code_hash=phone_code_hash,
                                         qrcode_url=None,
                                         qrcode_fpath=None,
                                         is_auth_error=False,
                                         auth_message=auth_msg,
                                         auth_error="")
                return auth_resp
            elif auth_type_choice == "2":  # By QRCode via Console
                print("Telethon user client authorisation via QR code:")
                qr_code_login = await user_client.qr_login(
                    ignored_ids=None)
                qr_code_url = qr_code_login.url
                print(f"Authorisation QRCode created successfully [OK]:\n"
                      f"qr_code_login: {qr_code_login}\n"
                      f"qr_code_url: {qr_code_url}\n")

                print("Generating QR code in console:")
                qr_code_obj = qrcode.main.QRCode(
                    version=None,
                    error_correction=QR_CODE_ERROR_CORRECTION.LEVEL_M.value,
                    box_size=10,
                    border=4,
                    image_factory=None,
                    mask_pattern=None, )
                qr_code_obj.add_data(qr_code_login.url, optimize=20)
                await asyncio.to_thread(qr_code_obj.print_ascii)
                qrcode_signed_in_user = await qr_code_login.wait()
                print(f"QR Code user client authorised successfully [OK]:\n"
                      f"qr_code_login: {qr_code_login}\n"
                      f"qr_code_url: {qr_code_url}\n"
                      f"qr_code: {qr_code}\n"
                      f"qrcode_signed_in_user: {qrcode_signed_in_user}\n")
                auth_msg = "Console QRCode Auth Driver: Authorised"
                auth_resp = AuthResponse(is_authorised=True,
                                         requires_action=False,
                                         auth_by_phone=False,
                                         auth_by_qrcode=True,
                                         auth_via_console=True,
                                         phone_code_hash=None,
                                         qrcode_url=qr_code_url,
                                         qrcode_fpath=None,
                                         is_auth_error=False,
                                         auth_message=auth_msg,
                                         auth_error="")
                return auth_resp
            else:  # auth_type_choice == "3": or any other value
                auth_error = (f"Console Auth Driver [ERROR]: "
                              f"Wrong auth type choice: {auth_type_choice}")
                auth_resp = AuthResponse(is_authorised=False,
                                         requires_action=False,
                                         auth_by_phone=False,
                                         auth_by_qrcode=False,
                                         auth_via_console=True,
                                         phone_code_hash=None,
                                         qrcode_url=None,
                                         qrcode_fpath=None,
                                         is_auth_error=True,
                                         auth_message="",
                                         auth_error=auth_error)
                return auth_resp
        except asyncio.TimeoutError as thread_timeout_error:
            error_log = (f"\n\n⚠️ Console Auth Driver thread timeout [ERROR]:\n"
                         f"error: {thread_timeout_error}\n"
                         f"auth_thread_timeout: {auth_thread_timeout}\n"
                         f"config_name: {config_name}\n"
                         f"telegram_phone: {telegram_phone}\n"
                         f"user_client: {user_client}\n"
                         f"client_is_user_authorised: {client_is_user_authorised}\n"
                         f"auth_type: {auth_type}\n"
                         f"auth_type_choice: {auth_type_choice}\n"
                         f"request_sent_code: {request_sent_code}\n"
                         f"phone_signed_in_user: {phone_signed_in_user}\n"
                         f"qr_code_login: {qr_code_login}\n"
                         f"qr_code_url: {qr_code_url}\n"
                         f"qr_code: {qr_code}\n"
                         f"qrcode_signed_in_user: {qrcode_signed_in_user}\n"
                         f"session_str_info: {session_str_info}\n"
                         f"auth_type_choice: {auth_type_choice}\n")
            auth_resp = AuthResponse(is_authorised=False,
                                     requires_action=False,
                                     auth_by_phone=False,
                                     auth_by_qrcode=False,
                                     auth_via_console=True,
                                     phone_code_hash=None,
                                     qrcode_url=None,
                                     qrcode_fpath=None,
                                     is_auth_error=True,
                                     auth_message="",
                                     auth_error=error_log)
            print(error_log)
            return auth_resp
        except Exception as error:
            error_log = (f"\n\n⚠️ Console Auth Driver [ERROR]:\n"
                         f"error: {error}\n"
                         f"auth_type: {auth_type}\n"
                         f"auth_type_choice: {auth_type_choice}\n"
                         f"request_sent_code: {request_sent_code}\n"
                         f"phone_signed_in_user: {phone_signed_in_user}\n"
                         f"qr_code_login: {qr_code_login}\n"
                         f"qr_code_url: {qr_code_url}\n"
                         f"qr_code: {qr_code}\n"
                         f"qrcode_signed_in_user: {qrcode_signed_in_user}\n"
                         f"session_str_info: {session_str_info}\n"
                         f"auth_type_choice: {auth_type_choice}\n")
            auth_resp = AuthResponse(is_authorised=False,
                                     requires_action=False,
                                     auth_by_phone=False,
                                     auth_by_qrcode=False,
                                     auth_via_console=True,
                                     phone_code_hash=None,
                                     qrcode_url=None,
                                     qrcode_fpath=None,
                                     is_auth_error=True,
                                     auth_message="",
                                     auth_error=error_log)
            print(error_log)
            return auth_resp
