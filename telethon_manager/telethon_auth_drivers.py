import asyncio
from abc import ABC

import qrcode
from pydantic.dataclasses import dataclass
from telethon import TelegramClient

from configs.enums import QR_CODE_ERROR_CORRECTION
from configs.options import TELETHON_OPTIONS
from telethon_manager.telethon_client_config import TelethonConfig


@dataclass
class AuthResponse:
    is_authorised: bool = False
    requires_action: bool = False
    auth_by_phone: bool = False
    qrcode_url: str | None = None
    auth_message: str = ""
    is_auth_error: bool = False
    auth_error: str = ""


class AuthDriver(ABC):
    def __init__(self,
                 telethon_user_client: TelegramClient,
                 telethon_config: TelethonConfig):
        self.telethon_user_client = telethon_user_client
        self.telethon_config = telethon_config

    async def auth_user_client_via_driver(self) -> AuthResponse:
        pass


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
            auth_response = AuthResponse(
                is_authorised=True,
                auth_message="WEB QRCode Auth: Client authorised initially")
            return auth_response

        qr_code_login = None
        qr_code_url = None
        try:
            print("Telethon user client auth via WEB QRCode driver:")
            qr_code_login = await user_client.qr_login(
                ignored_ids=None)
            qr_code_url = qr_code_login.url
            print(f"Authorisation QRCode created successfully [OK]:\n"
                  f"qr_code_login: {qr_code_login}\n"
                  f"qr_code_url: {qr_code_url}\n")
            auth_response = AuthResponse(
                is_authorised=False,
                requires_action=True,
                auth_by_phone=False,
                qrcode_url=qr_code_url,
                auth_message="WEB QRCode Auth: QRCode created, waiting scanning")
            return auth_response
        except Exception as error:
            error_log = (f"\n\n⚠️ Web QRCode driver authorisation [ERROR]:\n"
                         f"error: {error}\n"
                         f"config_name: {config_name}\n"
                         f"telegram_phone: {telegram_phone}\n"
                         f"user_client: {user_client}\n"
                         f"client_is_user_authorised: {client_is_user_authorised}\n"
                         f"auth_type: {auth_type}\n"
                         f"qr_code_login: {qr_code_login}\n"
                         f"qr_code_url: {qr_code_url}\n"
                         f"session_str_info: {session_str_info}\n")
            print(error_log)
            auth_response = AuthResponse(
                is_authorised=False,
                auth_message="WEB QRCode Auth: Generating QRCode [ERROR]",
                is_auth_error=True,
                auth_error=error_log)
            return auth_response


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
            auth_response = AuthResponse(
                is_authorised=True,
                auth_message="WEB Phone Auth: Client authorised initially")
            return auth_response

        qr_code_login = None
        qr_code_url = None
        try:
            print("Telethon user client auth via WEB Phone driver:")
            request_sent_code = await user_client.send_code_request(
                phone=telegram_phone,
                force_sms=False,  # Deprecated
                _retry_count=0)
            print(f"Phone authorisation code sent to phone [OK]:\n"
                  f"request_sent_code: {request_sent_code}\n")

            auth_response = AuthResponse(
                is_authorised=False,
                requires_action=True,
                auth_by_phone=True,
                qrcode_url=None,
                auth_message="WEB Phone Auth:  Phone code sent to telegram")
            return auth_response
        except Exception as error:
            error_log = (f"\n\n⚠️ Web Phone Driver authorisation [ERROR]:\n"
                         f"error: {error}\n"
                         f"config_name: {config_name}\n"
                         f"telegram_phone: {telegram_phone}\n"
                         f"user_client: {user_client}\n"
                         f"client_is_user_authorised: {client_is_user_authorised}\n"
                         f"auth_type: {auth_type}\n"
                         f"qr_code_login: {qr_code_login}\n"
                         f"qr_code_url: {qr_code_url}\n"
                         f"session_str_info: {session_str_info}\n")
            print(error_log)
            auth_response = AuthResponse(
                is_authorised=False,
                auth_message="WEB Phone Auth: Phone code sending [ERROR]",
                is_auth_error=True,
                auth_error=error_log)
            return auth_response


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
            auth_response = AuthResponse(
                is_authorised=True,
                auth_message="Console Auth: Client authorised initially")
            return auth_response

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

            if auth_type_choice == "1" and telegram_phone:
                print("Telethon user client authorising via phone:")
                request_sent_code = await user_client.send_code_request(
                    phone=telegram_phone,
                    force_sms=False,  # Deprecated
                    _retry_count=0)
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
                    phone_code_hash=None)
                print(f"Phone user client authorised successfully [OK]:\n"
                      f"request_sent_code: {request_sent_code}\n"
                      f"phone_signed_in_user: {phone_signed_in_user}\n")
                auth_response = AuthResponse(
                    is_authorised=True,
                    requires_action=False,
                    auth_by_phone=True,
                    qrcode_url=None,
                    auth_message="Console Phone Auth: Authorised")
                return auth_response
            elif auth_type_choice == "2":
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
                auth_response = AuthResponse(
                    is_authorised=True,
                    requires_action=False,
                    auth_by_phone=False,
                    qrcode_url=qr_code_url,
                    auth_message="Console QRCode Auth: Authorised")
                return auth_response
            else:  # auth_type_choice == "3": or any other value
                auth_response = AuthResponse(
                    is_authorised=False,
                    is_auth_error=True,
                    auth_message="",
                    auth_error=f"Console QRCode Auth: Wrong auth type choice: "
                               f"{auth_type_choice}"
                )
                return auth_response
        except asyncio.TimeoutError as thread_timeout_error:
            error_log = (f"\n\n⚠️ Console Driver auth thread timeout [ERROR]:\n"
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
            print(error_log)
            auth_response = AuthResponse(
                is_authorised=False,
                is_auth_error=True,
                auth_message="",
                auth_error=error_log)
            return auth_response
        except Exception as error:
            error_log = (f"\n\n⚠️ Console Driver authorisation [ERROR]:\n"
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
            print(error_log)
            auth_response = AuthResponse(
                is_authorised=False,
                is_auth_error=True,
                auth_message="",
                auth_error=error_log)
            return auth_response
