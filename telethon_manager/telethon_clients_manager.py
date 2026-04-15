import asyncio
import sqlite3
import weakref
from asyncio import Task
from typing import Dict, List, Literal, Callable, Tuple, Union

from telethon import TelegramClient
from telethon.sessions import StringSession, SQLiteSession
from telethon.tl.custom import QRLogin

from configs.console_colors import CONSOLE_COLORS
from configs.enums import (
    TELEGRAM_ACCOUNT_TYPE)
from configs.environments import (
    BASE_DIR)
from configs.options import ALCHEMY_OPTIONS, TELETHON_OPTIONS
from db_postgres.postgres_conn.pgs_connection import PgsAsyncConnection
from db_postgres.postgres_conn.postgres_session import PgsAsyncSession
from db_postgres.postgres_queries.qry_get_telethon_configs_objs import (
    get_telethon_configs_objs_qry)
from db_postgres.postgres_queries.qry_update_telethon_session_data import (
    update_telethon_session_data_qry)
from meta_classes.singlton_meta import SingletonMeta
from telethon_manager.telethon_auth_drivers import (
    TltAuthConsoleDriver, TltAuthWebPhoneDriver,
    TltAuthWebQRCodeDriver, TltAuthWebQRAndPhoneDriver, AuthDriver)
from telethon_manager.telethon_auth_response import AuthResponse
from telethon_manager.telethon_client_config import TelethonConfig
from telethon_manager.telethon_register_handlers import (
    add_all_telethon_client_handlers)
from utils_common.normalized_path import get_full_file_normal_path
from utils_specific.get_proxy_environ_conf import get_proxy_environ_config
from utils_specific.get_valid_proxy_config import get_valid_proxy_tuple


class TelethonManagerSingleton(metaclass=SingletonMeta):
    def __init__(self):
        self.clients: Dict[str, TelegramClient] = {}
        self.not_started_configs: Dict[str, TelethonConfig] = {}
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.qrcode_logins: Dict[str, QRLogin] = {}
        self.running_state = False

    async def get_postgres_db_tlt_configs(self) -> List[TelethonConfig]:
        log_pgs_good_ops = ALCHEMY_OPTIONS.ALCHEMY_SESSION_OK_ACTIONS_LOGS
        pgs_conn = PgsAsyncConnection()
        async with PgsAsyncSession(engine=pgs_conn.engine,
                                   log_good_ops=log_pgs_good_ops
                                   ) as pgs_session:
            pgs_telethon_configs_objs = await get_telethon_configs_objs_qry(
                ongoing_session=pgs_session)

        pgs_telethon_configs_list = []
        for cur_config_obj in pgs_telethon_configs_objs:
            telethon_account_type = cur_config_obj.tg_account_type

            new_config_name = await self.create_session_name(
                telethon_db_config_id=cur_config_obj.id,
                web_account_id=cur_config_obj.web_account_id,
                web_account_username=cur_config_obj.web_account_username,
                telegram_phone=cur_config_obj.tg_personal_phone,
                telegram_bot=cur_config_obj.tg_bot_token,
                telethon_account_type=telethon_account_type)

            cur_telethon_config = TelethonConfig(
                telethon_config_id=cur_config_obj.id,
                web_account_id=cur_config_obj.web_account_id,
                web_account_username=cur_config_obj.web_account_username,
                name=new_config_name,
                account_type=cur_config_obj.tg_account_type,
                api_id=cur_config_obj.tg_api_id,
                api_hash=cur_config_obj.tg_api_hash,
                session_string=cur_config_obj.telethon_session_str,
                bot_token=cur_config_obj.tg_bot_token,
                phone=cur_config_obj.tg_personal_phone,
                proxy=cur_config_obj.telethon_proxy_config,
                telethon_is_active=cur_config_obj.telethon_is_active,
                is_active=cur_config_obj.telethon_is_active,
                authorisation_type=cur_config_obj.authorisation_type)
            pgs_telethon_configs_list.append(cur_telethon_config)
        return pgs_telethon_configs_list

    @staticmethod
    async def create_session_name(
            telethon_db_config_id: int,
            web_account_id: str,
            web_account_username: str,
            telegram_phone: str,
            telegram_bot: str,
            telethon_account_type: Literal[
                TELEGRAM_ACCOUNT_TYPE.ACCOUNT,
                TELEGRAM_ACCOUNT_TYPE.BOT],
    ) -> str:
        if telegram_phone:
            additional_info = f"tel_{telegram_phone.lstrip("+")}"
        else:
            additional_info = f"tkn_{telegram_bot[:10]}"

        new_session_name = (
            f"id_{telethon_db_config_id}_"
            f"type_{telethon_account_type}_"
            f"acc_{web_account_id}_{web_account_username}_"
            f"{additional_info}")
        return new_session_name

    async def run_all_telethon_clients(
            self, telethon_configs: List[TelethonConfig]
    ) -> None:
        print(f"\nRunning all telethon telegram clients by list:")
        prev_is_bot_flag = False
        prev_is_acc_flag = False

        yellow_clr = CONSOLE_COLORS.BRIGHT_YELLOW
        margenta_clr = CONSOLE_COLORS.BRIGHT_MAGENTA
        reset_clr = CONSOLE_COLORS.RESET
        for cur_config in telethon_configs:
            account_type = cur_config.account_type
            telethon_config_id = cur_config.telethon_config_id
            config_name = cur_config.name
            telegram_phone = cur_config.phone
            bot_token = cur_config.bot_token
            bot_token_info = f"{bot_token[:10]}..." if bot_token else None

            if account_type == TELEGRAM_ACCOUNT_TYPE.ACCOUNT:
                acc_delay_secs = TELETHON_OPTIONS.EACH_ACC_CLIENT_START_DELAY_SEC
                if prev_is_acc_flag and acc_delay_secs != 0:
                    print(f"{margenta_clr}Waiting to start next account client "
                          f"right after account client...{reset_clr}\n"
                          f"acc_delay_secs: {acc_delay_secs}\n"
                          f"prev_is_acc_flag: {prev_is_acc_flag}\n"
                          f"prev_is_bot_flag: {prev_is_bot_flag}\n")
                    await asyncio.sleep(acc_delay_secs)
                prev_is_bot_flag = False
                prev_is_acc_flag = True
            elif account_type == TELEGRAM_ACCOUNT_TYPE.BOT:
                bot_delay_secs = TELETHON_OPTIONS.EACH_BOT_CLIENT_START_DELAY_SEC
                if prev_is_bot_flag and bot_delay_secs != 0:
                    print(f"{yellow_clr}Waiting to start next bot client "
                          f"right after bot client...{reset_clr}\n"
                          f"bot_delay_secs: {bot_delay_secs}\n"
                          f"prev_is_acc_flag: {prev_is_acc_flag}\n"
                          f"prev_is_bot_flag: {prev_is_bot_flag}\n")
                    await asyncio.sleep(bot_delay_secs)
                prev_is_bot_flag = True
                prev_is_acc_flag = False
            else:  # Telethon account type not defined
                print(f"Telethon client with empty account_type skipped [ERROR]\n"
                      f"telethon_config_id: {telethon_config_id}\n"
                      f"account_type: {account_type}\n"
                      f"telegram_phone: {telegram_phone}\n"
                      f"bot_token_info: {bot_token_info}\n"
                      f"config_name: {config_name}\n")
                self.not_started_configs[config_name] = cur_config
                continue

            cur_client, auth_resp = await self.run_telethon_client(
                telethon_config=cur_config)

            if cur_client and auth_resp.is_authorised:
                self.clients[config_name] = cur_client  # Double. First check and assignment in start User, Bot client
            else:
                self.not_started_configs[config_name] = cur_config  # Double. First assignment in start User, Bot client

            if not cur_client:
                print(f"Telethon client not created [ERROR]\n"
                      f"telethon_config_id: {telethon_config_id}\n"
                      f"account_type: {account_type}\n"
                      f"telegram_phone: {telegram_phone}\n"
                      f"bot_token_info: {bot_token_info}\n"
                      f"config_name: {config_name}\n"
                      f"cur_client: {cur_client}\n"
                      f"auth_resp.is_authorised: {auth_resp.is_authorised}\n")
            continue  # Not necessary, just to show bottom loop border

        if self.not_started_configs:
            print(f"\nTELETHON CLIENTS NOT CREATED [ERROR]:")
            counter = 1
            for cur_conf_name, cur_tlt_conf in self.not_started_configs.items():
                print(f"{counter}. cur_conf_name: {cur_conf_name}, "
                      f"cur_tlt_conf: {cur_tlt_conf}")
                counter += 1

        if self.clients:
            print(f"\nTELETHON CLIENTS CREATED [SUCCESS]:")
            counter = 1
            for cur_tlt_config, cur_tlt_client in self.clients.items():
                print(f"{counter}. cur_telethon_config: {cur_tlt_config}, "
                      f"cur_telethon_client: {cur_tlt_client}")
                counter += 1

    async def run_telethon_client(
            self, telethon_config: TelethonConfig
    ) -> Tuple[Union[TelegramClient | None], AuthResponse]:
        telethon_config_id = telethon_config.telethon_config_id
        account_type = telethon_config.account_type
        config_name = telethon_config.name
        telegram_phone = telethon_config.phone
        bot_token = telethon_config.bot_token
        bot_token_info = f"{bot_token[:10]}..." if bot_token else None

        try:
            if account_type == TELEGRAM_ACCOUNT_TYPE.ACCOUNT:
                print(f"{'>' * 55}\n{'>' * 55}\n"
                      f">>>>>>> START SINGLE PERSONAL TELETHON CLIENT:\n"
                      f"telethon_config_id: {telethon_config_id}\n"
                      f"account_type: {account_type}\n"
                      f"telegram_phone: {telegram_phone}\n"
                      f"bot_token_info: {bot_token_info}\n"
                      f"config_name: {config_name}\n")
                tlt_client, auth_resp = await self.start_user_client(
                    telethon_config=telethon_config,
                    skip_authorisation=False,
                    connect_retries=TELETHON_OPTIONS.CLIENT_CONNECT_RETRIES,
                    connect_delay_sec=TELETHON_OPTIONS.CLIENT_CONNECT_DELAY_SEC)
            elif account_type == TELEGRAM_ACCOUNT_TYPE.BOT:
                print(f"{'>' * 55}\n{'>' * 55}\n"
                      f">>>>>>> START SINGLE TELEGRAM BOT TELETHON CLIENT:\n"
                      f"telethon_config_id: {telethon_config_id}\n"
                      f"account_type: {account_type}\n"
                      f"telegram_phone: {telegram_phone}\n"
                      f"bot_token_info: {bot_token_info}\n"
                      f"config_name: {config_name}\n")
                tlt_client, auth_resp = await self.start_bot_client(
                    telethon_config=telethon_config)
            else:  # Telethon account type not defined
                tlt_client = None
                auth_error = "Not created client, account type not defined"
                auth_resp = AuthResponse(is_authorised=False,
                                         requires_action=False,
                                         auth_by_phone=False,
                                         auth_by_qrcode=False,
                                         auth_via_console=False,
                                         phone_code_hash=None,
                                         qrcode_url=None,
                                         qrcode_fpath=None,
                                         is_auth_error=True,
                                         auth_message="",
                                         auth_error=auth_error)
                print(f"Telethon client with empty account_type [ERROR]\n"
                      f"telethon_config_id: {telethon_config_id}\n"
                      f"account_type: {account_type}\n"
                      f"telegram_phone: {telegram_phone}\n"
                      f"bot_token_info: {bot_token_info}\n"
                      f"config_name: {config_name}\n")
                return tlt_client, auth_resp

            if tlt_client:
                log_text = "Telethon client created successfully [OK]:"
            else:
                log_text = "Telethon client not created [ERROR]:"

            print(f"{log_text}\n"
                  f"tlt_client: {tlt_client}\n"
                  f"auth_resp: {auth_resp}\n"
                  f"telethon_config_id: {telethon_config_id}\n"
                  f"account_type: {account_type}\n"
                  f"telegram_phone: {telegram_phone}\n"
                  f"bot_token_info: {bot_token_info}\n"
                  f"config_name: {config_name}\n")

            print("Telethon client PGS-SQLite session saving:")
            proxy_environ_config = await get_proxy_environ_config()
            if proxy_environ_config:
                valid_proxy_config = await get_valid_proxy_tuple(
                    raw_proxy_config=proxy_environ_config,
                    use_socks_objs=False)
                telethon_config.proxy = valid_proxy_config

            if tlt_client:
                # session_str = StringSession.save(tlt_client.session)  # Obtain session str from tlt client for PGS
                await self.postgres_db_save_tlt_session(
                    telethon_client=tlt_client,
                    telethon_config=telethon_config)
                print("Telethon client PGS-SQLite session saved [OK]\n")

                print("Telethon client all handlers registering:")
                await self.register_tlt_client_handlers(
                    telethon_client=tlt_client,
                    telethon_config=telethon_config)
                print("Telethon client all handlers registered [OK]\n")
            return tlt_client, auth_resp
        except Exception as error:
            tlt_client = None
            error_log = (f"Run single Telethon client [ERROR]:\n"
                         f"error: {error}\n"
                         f"config_name: {config_name}\n"
                         f"telethon_config_id: {telethon_config_id}\n"
                         f"account_type: {account_type}\n"
                         f"telegram_phone: {telegram_phone}\n"
                         f"bot_token_info: {bot_token_info}\n")
            auth_resp = AuthResponse(is_authorised=False,
                                     requires_action=False,
                                     auth_by_phone=False,
                                     auth_by_qrcode=False,
                                     auth_via_console=False,
                                     phone_code_hash=None,
                                     qrcode_url=None,
                                     qrcode_fpath=None,
                                     is_auth_error=True,
                                     auth_message="",
                                     auth_error=error_log)
            print(error_log)
            return tlt_client, auth_resp

    async def start_user_client(
            self, telethon_config: TelethonConfig,
            skip_authorisation: bool = False,
            connect_retries: int | None = 60,
            connect_delay_sec: int | None = 1
    ) -> Tuple[Union[TelegramClient | None], AuthResponse]:
        print("Creating existing or new Telethon session:")
        session_str = telethon_config.session_string
        session_str_info = f"...{session_str[-15:]}" if session_str else None

        if session_str:
            session = StringSession(string=session_str)
            print(f"Existing Telethon session used via StringSession [OK]:\n"
                  f"session_str_info: {session_str_info}\n"
                  f"session: {session}\n")
        else:
            session_prefix = TELETHON_OPTIONS.ACCOUNT_SESSION_FILE_PREFIX
            config_name = telethon_config.name
            new_session_id = f"{session_prefix}{config_name}"
            telethon_sessions_dir = TELETHON_OPTIONS.BASE_TELETHON_SESSIONS_DIR
            session_full_file_path = get_full_file_normal_path(
                all_dir_str_parts=[BASE_DIR, telethon_sessions_dir],
                file_name_with_ext=new_session_id)
            # if os.path.isfile(session_full_file_path):
            #     os.remove(session_full_file_path)

            session = SQLiteSession(session_id=session_full_file_path)
            print(f"New Telethon session created via SQLiteSession [OK]:\n"
                  f"session_str_info: {session_str_info}\n"
                  f"config_name: {config_name}\n"
                  f"new_session_id: {new_session_id}\n"
                  f"session_full_file_path: {session_full_file_path}\n"
                  f"session: {session}\n")

        if not TELETHON_OPTIONS.USE_TELETHON_PROXY:
            valid_proxy_config = None
        else:
            proxy_environ_config = await get_proxy_environ_config()
            if proxy_environ_config:  # Environments proxy config exists
                valid_proxy_config = await get_valid_proxy_tuple(
                    raw_proxy_config=proxy_environ_config,
                    use_socks_objs=True)
            elif telethon_config.proxy:  # DB proxy config exists
                valid_proxy_config = await get_valid_proxy_tuple(
                    raw_proxy_config=telethon_config.proxy,
                    use_socks_objs=True)
            else:
                valid_proxy_config = None

        user_client = TelegramClient(
            session=session,
            api_id=telethon_config.api_id,
            api_hash=telethon_config.api_hash,
            proxy=valid_proxy_config,
            connection_retries=TELETHON_OPTIONS.TELEGRAM_CLIENT_CONNECT_RETRIES,
            retry_delay=TELETHON_OPTIONS.TELEGRAM_CLIENT_CONNECT_RETRY_DELAY,
            timeout=TELETHON_OPTIONS.TELEGRAM_CLIENT_CONNECT_TIMEOUT,
            request_retries=TELETHON_OPTIONS.TELEGRAM_CLIENT_REQUEST_RETRIES,
            flood_sleep_threshold=TELETHON_OPTIONS.FLOOD_SLEEP_THRESHOLD, )

        before_connect_is_connected = user_client.is_connected()
        print(f"Telethon User client state before connect():\n"
              f"before_connect_is_connected: {before_connect_is_connected}\n")
        if not before_connect_is_connected:
            connection_retries = 1 if not connect_retries else connect_retries
            for cur_attempt in range(connection_retries):
                try:
                    await user_client.connect()
                    break  # if connection executed successfully
                except sqlite3.OperationalError as locked_db_error:
                    if cur_attempt + 1 < connection_retries:
                        break
                    print(f"Waiting client connection.....\n"
                          f"locked_db_error: {locked_db_error}\n")
                    await asyncio.sleep(connect_delay_sec)

        after_connect_is_connected = user_client.is_connected()
        after_connect_is_authorised = await user_client.is_user_authorized()
        print(f"Telethon User client state after connect():\n"
              f"after_connect_is_connected: {after_connect_is_connected}\n"
              f"after_connect_is_authorised: {after_connect_is_authorised}\n")

        if after_connect_is_connected and after_connect_is_authorised:
            auth_message = "Start User Client: User authorised initially"
            self.clients[telethon_config.name] = user_client
            self.not_started_configs.pop(telethon_config.name, None)
            auth_resp = AuthResponse(is_authorised=True,
                                     requires_action=False,
                                     auth_by_phone=False,
                                     auth_by_qrcode=False,
                                     auth_via_console=False,
                                     phone_code_hash=None,
                                     qrcode_url=None,
                                     qrcode_fpath=None,
                                     is_auth_error=False,
                                     auth_message=auth_message,
                                     auth_error="")
            print(f"Telethon User client initially authorised:\n"
                  f"after_connect_is_connected: {after_connect_is_connected}\n"
                  f"after_connect_is_authorised: {after_connect_is_authorised}\n")
            return user_client, auth_resp  # Return tlt client immediately as it is authorised

        if not skip_authorisation:
            _AUTH_DRIVER = {"console": TltAuthConsoleDriver,
                            "phone": TltAuthWebPhoneDriver,
                            "qrcode": TltAuthWebQRCodeDriver,
                            "qr+phone": TltAuthWebQRAndPhoneDriver}
            auth_type = telethon_config.authorisation_type
            auth_driver_class = _AUTH_DRIVER[auth_type]
            auth_driver_obj = auth_driver_class(
                telethon_user_client=user_client,
                telethon_config=telethon_config)
            auth_resp = await self.authorise_tlt_user_client(
                auth_driver=auth_driver_obj)
        else:
            auth_message = "Start User Client: Authorisation skipped"
            auth_resp = AuthResponse(is_authorised=False,
                                     requires_action=False,
                                     auth_by_phone=False,
                                     auth_by_qrcode=False,
                                     auth_via_console=False,
                                     phone_code_hash=None,
                                     qrcode_url=None,
                                     qrcode_fpath=None,
                                     is_auth_error=False,
                                     auth_message=auth_message,
                                     auth_error="")
            print(f"Telethon User client created and authorisation skipped:\n"
                  f"after_connect_is_connected: {after_connect_is_connected}\n"
                  f"after_connect_is_authorised: {after_connect_is_authorised}\n"
                  f"skip_authorisation: {skip_authorisation}\n")
            return user_client, auth_resp

        after_auth_is_connected = user_client.is_connected()
        after_auth_is_authorised = await user_client.is_user_authorized()

        if after_auth_is_connected and after_auth_is_authorised:
            self.clients[telethon_config.name] = user_client
            self.not_started_configs.pop(telethon_config.name, None)
            auth_resp.is_authorised = True  # Double check and assignment
        else:
            self.not_started_configs[telethon_config.name] = telethon_config
            auth_resp.is_authorised = False  # Double check and assignment
            print(f"Telethon User client state after authorise_tlt_user_client():\n"
                  f"after_auth_is_connected: {after_auth_is_connected}\n"
                  f"after_auth_is_authorised: {after_auth_is_authorised}\n")
        return user_client, auth_resp  # Return tlt client creation result after authorisation attempt

    @staticmethod
    async def postgres_db_save_tlt_session(
            telethon_config: TelethonConfig,
            telethon_client: TelegramClient
    ) -> bool:
        session_str = StringSession.save(telethon_client.session)  # Obtain session str from tlt client for PGS
        session_str_info = f"...{session_str[-15:]}" if session_str else None
        print(f"Telethon session string obtained from tlt client[OK]:\n"
              f"session_str_info: {session_str_info}\n")

        session_update_data = {
            "telethon_session_str": session_str,
            "telethon_proxy_config": telethon_config.proxy,
            "telethon_config_name": telethon_config.name}
        session_is_updated = await update_telethon_session_data_qry(
            # Non Telethon standard Postgres saving session string
            telethon_config_id=telethon_config.telethon_config_id,
            web_account_id=telethon_config.web_account_id,
            web_account_username=telethon_config.web_account_username,
            telegram_phone=telethon_config.phone,
            telegram_bot_token=telethon_config.bot_token,
            update_data=session_update_data)

        if session_is_updated:
            print(f"DB Telethon session saved in Postgres [OK]\n"
                  f"session_str_info: {session_str_info}\n")

        telethon_client.session.save()  # Standard Telethon session saving in SQLite session file
        print(f"DB Telethon session saved in SQLite [OK]\n"
              f"session_str_info: {session_str_info}\n")
        return session_str

    async def authorise_tlt_user_client(
            self,
            auth_driver: AuthDriver
    ) -> AuthResponse:
        """Authorisation via various drivers: console, phone, qrcode"""
        auth_result = await auth_driver.auth_user_client_via_driver()
        return auth_result

    async def start_bot_client(
            self, telethon_config: TelethonConfig
    ) -> Tuple[Union[TelegramClient | None], AuthResponse]:
        session_prefix = TELETHON_OPTIONS.BOT_SESSION_FILE_PREFIX
        config_name = telethon_config.name
        new_session_id = f"{session_prefix}{config_name}"
        telethon_sessions_dir = TELETHON_OPTIONS.BASE_TELETHON_SESSIONS_DIR
        session_full_file_path = get_full_file_normal_path(
            all_dir_str_parts=[BASE_DIR, telethon_sessions_dir],
            file_name_with_ext=new_session_id)

        if not TELETHON_OPTIONS.USE_TELETHON_PROXY:
            valid_proxy_config = None
        else:
            proxy_environ_config = await get_proxy_environ_config()
            if proxy_environ_config:  # Environments proxy config exists
                valid_proxy_config = await get_valid_proxy_tuple(
                    raw_proxy_config=proxy_environ_config,
                    use_socks_objs=True)
            elif telethon_config.proxy:  # DB proxy config exists
                valid_proxy_config = await get_valid_proxy_tuple(
                    raw_proxy_config=telethon_config.proxy,
                    use_socks_objs=True)
            else:
                valid_proxy_config = None

        bot_client = TelegramClient(
            session=session_full_file_path,
            api_id=telethon_config.api_id,
            api_hash=telethon_config.api_hash,
            proxy=valid_proxy_config,
            connection_retries=TELETHON_OPTIONS.TELEGRAM_CLIENT_CONNECT_RETRIES,
            retry_delay=TELETHON_OPTIONS.TELEGRAM_CLIENT_CONNECT_RETRY_DELAY,
            timeout=TELETHON_OPTIONS.TELEGRAM_CLIENT_CONNECT_TIMEOUT,
            request_retries=TELETHON_OPTIONS.TELEGRAM_CLIENT_REQUEST_RETRIES,
            flood_sleep_threshold=TELETHON_OPTIONS.FLOOD_SLEEP_THRESHOLD, )

        before_connect_is_connected = bot_client.is_connected()
        print(f"Telethon Bot client state before start():\n"
              f"before_connect_is_connected: {before_connect_is_connected}\n")

        if not before_connect_is_connected:
            await bot_client.connect()

        after_connect_is_connected = bot_client.is_connected()
        after_connect_is_authorised = await bot_client.is_user_authorized()
        after_connect_is_bot = await bot_client.is_bot()
        print(f"Telethon Bot client state after connect():\n"
              f"after_connect_is_connected: {after_connect_is_connected}\n"
              f"after_connect_is_authorised: {after_connect_is_authorised}\n"
              f"after_connect_is_bot: {after_connect_is_bot}\n")

        if after_connect_is_connected and after_connect_is_authorised:
            self.clients[telethon_config.name] = bot_client
            auth_message = "Start Bot Client: Bot authorised initially"
            auth_resp = AuthResponse(is_authorised=True,
                                     requires_action=False,
                                     auth_by_phone=False,
                                     auth_by_qrcode=False,
                                     auth_via_console=False,
                                     phone_code_hash=None,
                                     qrcode_url=None,
                                     qrcode_fpath=None,
                                     is_auth_error=False,
                                     auth_message=auth_message,
                                     auth_error="")
            print(f"Telethon Bot client initially authorised:\n"
                  f"after_connect_is_connected: {after_connect_is_connected}\n"
                  f"after_connect_is_authorised: {after_connect_is_authorised}\n"
                  f"after_connect_is_bot: {after_connect_is_bot}\n")
            return bot_client, auth_resp  # Return tlt bot client immediately as it is authorised

        try:
            await bot_client.start(  # Telethon bug: await is necessary. Error without await but sync start()
                bot_token=telethon_config.bot_token,
                force_sms=False,
                code_callback=None,
                first_name=telethon_config.web_account_id,
                last_name=telethon_config.web_account_username,
                max_attempts=TELETHON_OPTIONS.TELEGRAM_BOT_CLIENT_START_ATTEMPTS)
        except Exception as error:
            print(f"Telethon Bot client start [ERROR]:\n"
                  f"error: {error}\n")

        after_start_is_connected = bot_client.is_connected()
        after_start_is_authorised = await bot_client.is_user_authorized()
        after_start_is_bot = await bot_client.is_bot()

        if after_start_is_connected and after_start_is_authorised:
            self.clients[telethon_config.name] = bot_client
            self.not_started_configs.pop(telethon_config.name, None)
            auth_message = "Start Bot Client: Bot authorised after start"
            auth_resp = AuthResponse(is_authorised=True,
                                     requires_action=False,
                                     auth_by_phone=False,
                                     auth_by_qrcode=False,
                                     auth_via_console=False,
                                     phone_code_hash=None,
                                     qrcode_url=None,
                                     qrcode_fpath=None,
                                     is_auth_error=False,
                                     auth_message=auth_message,
                                     auth_error="")
        else:
            self.not_started_configs[telethon_config.name] = telethon_config
            auth_error = "Start Bot Client: Bot not authorised after start error"
            auth_resp = AuthResponse(is_authorised=False,
                                     requires_action=False,
                                     auth_by_phone=False,
                                     auth_by_qrcode=False,
                                     auth_via_console=False,
                                     phone_code_hash=None,
                                     qrcode_url=None,
                                     qrcode_fpath=None,
                                     is_auth_error=True,
                                     auth_message="",
                                     auth_error=auth_error)
            print(f"Telethon Bot client state after start():\n"
                  f"after_start_is_connected: {after_start_is_connected}\n"
                  f"after_start_is_authorised: {after_start_is_authorised}\n"
                  f"after_start_is_bot: {after_start_is_bot}\n")
        return bot_client, auth_resp  # Return tlt bot client after authorisation attempt

    async def register_tlt_client_handlers(
            self,
            telethon_client: TelegramClient,
            telethon_config: TelethonConfig
    ) -> None:
        # TODO: Decide use weak_ref or ordinal variables
        telethon_client_weak_ref = weakref.ref(telethon_client)
        telethon_config_weak_ref = weakref.ref(telethon_config)

        await add_all_telethon_client_handlers(
            telethon_manager=self,
            # telethon_client=telethon_client,
            # telethon_config=telethon_config
            telethon_client_weak_ref=telethon_client_weak_ref,
            telethon_config_weak_ref=telethon_config_weak_ref)

    async def execute_async_periodic_task(self):
        print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        print("^^^^^^^^^ Executing any async periodic task ^^^^^^^^^^^")
        print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        periodic_task_interval = TELETHON_OPTIONS.PERIODIC_ASYNC_TASK_INTERVAL_SEC
        await asyncio.sleep(periodic_task_interval)

    async def run_all_tlt_clients_async_tasks(self) -> List[Task] | None:
        print("\nTelethon clients async tasks startup and executing:\n")

        def done_callback(task):
            print(f"Async task done callback:\n"
                  f"finished task: {task.get_name()}\n")

        self.running_state = True
        try:
            for cur_config_name, cur_tlt_client in self.clients.items():
                cur_tlt_client_task = asyncio.create_task(
                    coro=cur_tlt_client.run_until_disconnected(),
                    name=cur_config_name,
                    context=None)  # Context vars can be passed/gotten
                self.running_tasks[cur_config_name] = cur_tlt_client_task
                cur_tlt_client_task.add_done_callback(done_callback)

            periodic_async_task = asyncio.create_task(
                coro=self.execute_async_periodic_task(),
                name="periodic_async_task",
                context=None)  # Context vars can be passed/gotten
            self.running_tasks["periodic_async_task"] = periodic_async_task

            # Telethon async tasks will be started later, together with uvicorn server in main.py
            # coros_or_futures = self.running_tasks.values()
            # await asyncio.gather(*coros_or_futures, return_exceptions=True)
            # done, pending = await asyncio.wait(fs=coros_or_futures, timeout=None, return_when=asyncio.ALL_COMPLETED)

            print(f"Telethon async tasks started (not gathered) and returned [OK]:\n")
            tlt_clients_async_tasks_list = list(self.running_tasks.values())
            return tlt_clients_async_tasks_list
        except KeyboardInterrupt as keyboard_interr_error:
            error_log = (f"Keyboard stop signal error [ERROR]:\n"
                         f"keyboard_interr_error: {keyboard_interr_error}\n")
            print(error_log)
            await self.disconnect_all_tlt_clients()  # Also in FastAPI shutdown lifespan
            await self.cancel_all_telethon_async_tasks()  # Also in FastAPI shutdown lifespan
        except Exception as error:
            error_log = (f"Running up asyncio tasks [ERROR]:\n"
                         f"error: {error}")
            print(error_log)
            await self.disconnect_all_tlt_clients()  # Also in FastAPI shutdown lifespan
            await self.cancel_all_telethon_async_tasks()  # Also in FastAPI shutdown lifespan
        finally:
            pass

    async def disconnect_all_tlt_clients(self):
        errors_list = []
        for cur_config_name, cur_tlt_client in self.clients.items():
            try:
                client_is_connected = cur_tlt_client.is_connected()
                if not client_is_connected:
                    print(f"{'>' * 55}\n{'>' * 55}\n"
                          f"Already disconnected Telethon client skipped [OK]:\n"
                          f"cur_config_name: {cur_config_name}\n"
                          f"client_is_connected: {client_is_connected}\n")
                    continue

                await cur_tlt_client.disconnect()
                client_is_connected = cur_tlt_client.is_connected()
                print(f"{'>' * 55}\n{'>' * 55}\n"
                      f"Current Telethon client disconnected [OK]:\n"
                      f"cur_config_name: {cur_config_name}\n"
                      f"client_is_connected: {client_is_connected}\n")
            except Exception as error:
                print(f"Telethon client disconnection [ERROR]:\n"
                      f"error: {error}\n"
                      f"cur_config_name: {cur_config_name}\n")
                errors_list.append(f"cur_config_name: {cur_config_name}, "
                                   f"error: {error}")
        self.running_state = False
        if errors_list:
            print("Not all Telethon clients asyncio tasks disconnected [ERROR]:\n")
            for cur_error in errors_list:
                print(f"\t{cur_error}")
        else:
            print("All Telethon clients disconnected successfully [OK]\n")

    async def cancel_all_telethon_async_tasks(self):
        errors_list = []
        for cur_config_name, cur_tlt_task in self.running_tasks.items():
            try:
                if cur_tlt_task.done():
                    print(f"{'>' * 55}\n{'>' * 55}\n"
                          f"Already done Telethon client asyncio task skipped [OK]:\n"
                          f"cur_config_name: {cur_config_name}\n"
                          f"cur_tlt_task.cancelled(): {cur_tlt_task.cancelled()}\n"
                          f"cur_tlt_task.done(): {cur_tlt_task.done()}\n")
                    continue
                if cur_tlt_task.cancelled():
                    print(f"{'>' * 55}\n{'>' * 55}\n"
                          f"Already canceled Telethon client asyncio task skipped [OK]:\n"
                          f"cur_config_name: {cur_config_name}\n"
                          f"cur_tlt_task.cancelled(): {cur_tlt_task.cancelled()}\n"
                          f"cur_tlt_task.done(): {cur_tlt_task.done()}\n")
                    continue

                cur_tlt_task.cancel()
                print(f"{'>' * 55}\n{'>' * 55}\n"
                      f"Current Telethon client async task canceled [OK]:\n"
                      f"cur_config_name: {cur_config_name}\n"
                      f"cur_tlt_task.cancelled(): {cur_tlt_task.cancelled()}\n"
                      f"cur_tlt_task.done(): {cur_tlt_task.done()}\n")
            except Exception as error:
                print(f"Canceling Telethon client asyncio task [ERROR]:\n"
                      f"error: {error}\n"
                      f"cur_config_name: {cur_config_name}\n")
                errors_list.append(f"cur_config_name: {cur_config_name}, "
                                   f"error: {error}")
        self.running_state = False
        self.running_tasks.clear()
        if errors_list:
            print("Not all Telethon clients asyncio tasks canceled [ERROR]:\n")
            for cur_error in errors_list:
                print(f"\t{cur_error}")
        else:
            print("All Telethon clients asyncio tasks canceled successfully [OK]\n")

    async def disconnect_tlt_client(self,
                                    config_name: str) -> Tuple[bool, str]:
        if config_name not in self.clients:
            log_message = (f"TLT client not found and skipped [OK]:\n"
                           f"config_name: {config_name}\n")
            print(f"{'>' * 55}\n{'>' * 55}\n"
                  f"{log_message}\n")
            return True, log_message

        try:
            tlt_client = self.clients[config_name]
            client_is_connected = tlt_client.is_connected()
            if not client_is_connected:
                log_message = (
                    f"Already disconnected TLT client skipped [OK]:\n"
                    f"config_name: {config_name}\n"
                    f"client_is_connected: {client_is_connected}\n")
                print(f"{'>' * 55}\n{'>' * 55}\n"
                      f"{log_message}\n")
                return True, log_message

            await tlt_client.disconnect()
            client_is_connected = tlt_client.is_connected()
            log_message = (f"TLT client disconnected [OK]:\n"
                           f"config_name: {config_name}\n"
                           f"client_is_connected: {client_is_connected}\n")
            print(f"{'>' * 55}\n{'>' * 55}\n"
                  f"{log_message}\n")
            return True, log_message
        except Exception as error:
            error_log = (f"Telethon client disconnection [ERROR]:\n"
                         f"error: {error}\n"
                         f"config_name: {config_name}\n")
            print(f"{'>' * 55}\n{'>' * 55}\n"
                  f"{error_log}\n")
            return False, error_log

    async def cancel_tlt_async_task(self, config_name: str) -> Tuple[bool, str]:
        if config_name not in self.running_tasks:
            log_message = (
                f"TLT client asyncio task not found and skipped [OK]:\n"
                f"config_name: {config_name}\n")
            print(f"{'>' * 55}\n{'>' * 55}\n"
                  f"{log_message}\n")
            return True, log_message

        try:
            tlt_async_task = self.running_tasks[config_name]
            if tlt_async_task.done():
                log_message = (
                    f"Already done TLT client asyncio task skipped [OK]:\n"
                    f"config_name: {config_name}\n"
                    f"tlt_async_task.cancelled(): {tlt_async_task.cancelled()}\n"
                    f"tlt_async_task.done(): {tlt_async_task.done()}\n")
                print(f"{'>' * 55}\n{'>' * 55}\n"
                      f"{log_message}\n")
                return True, log_message

            if tlt_async_task.cancelled():
                log_message = (
                    f"Already canceled TLT client asyncio task skipped [OK]:\n"
                    f"config_name: {config_name}\n"
                    f"tlt_async_task.cancelled(): {tlt_async_task.cancelled()}\n"
                    f"tlt_async_task.done(): {tlt_async_task.done()}\n")
                print(f"{'>' * 55}\n{'>' * 55}\n"
                      f"{log_message}\n")
                return True, log_message

            tlt_async_task.cancel()
            log_message = (
                f"Telethon client async task canceled [OK]:\n"
                f"config_name: {config_name}\n"
                f"tlt_async_task.cancelled(): {tlt_async_task.cancelled()}\n"
                f"tlt_async_task.done(): {tlt_async_task.done()}\n")
            print(f"{'>' * 55}\n{'>' * 55}\n"
                  f"{log_message}\n")
            return True, log_message
        except Exception as error:
            error_log = (
                f"Canceling Telethon client asyncio task [ERROR]:\n"
                f"error: {error}\n"
                f"config_name: {config_name}\n")
            print(error_log)
            return False, error_log
