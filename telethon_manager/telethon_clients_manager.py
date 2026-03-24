import asyncio
import weakref
from asyncio import Task
from typing import Dict, List, Literal, Callable

import qrcode
from telethon import TelegramClient
from telethon.sessions import StringSession, SQLiteSession

from configs.enums import (
    TELEGRAM_ACCOUNT_TYPE, QR_CODE_ERROR_CORRECTION)
from configs.settings import (
    BASE_DIR)
from configs.options import ALCHEMY_OPTIONS, TELETHON_OPTIONS
from db_postgres.postgres_conn.pgs_connection import PgsAsyncConnection
from db_postgres.postgres_conn.postgres_session import PgsAsyncSession
from db_postgres.postgres_queries.qry_get_telethon_configs_objs import (
    get_telethon_configs_objs_qry)
from db_postgres.postgres_queries.qry_update_telethon_session_data import (
    update_telethon_session_data_qry)
from meta_classes.singlton_meta import SingletonMeta
from telethon_manager.telethon_client_config import TelethonConfig
from telethon_manager.telethon_register_handlers import (
    add_all_telethon_client_handlers)
from utils_common.normalized_path import get_full_file_normal_path
from utils_specific.get_valid_proxy_config import get_valid_proxy_tuple


class TelethonManagerSingleton(metaclass=SingletonMeta):
    _obj_instance = None

    def __init__(self):
        self.clients: Dict[str, TelegramClient] = {}
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.running_tasks: Dict[str, asyncio.Task] = {}
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
                is_active=cur_config_obj.telethon_is_active)
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
                    print(f"Waiting to start next account client right after account client...\n"
                          f"acc_delay_secs: {acc_delay_secs}\n"
                          f"prev_is_acc_flag: {prev_is_acc_flag}\n"
                          f"prev_is_bot_flag: {prev_is_bot_flag}\n")
                    await asyncio.sleep(acc_delay_secs)
                prev_is_bot_flag = False
                prev_is_acc_flag = True
            elif account_type == TELEGRAM_ACCOUNT_TYPE.BOT:
                bot_delay_secs = TELETHON_OPTIONS.EACH_BOT_CLIENT_START_DELAY_SEC
                if prev_is_bot_flag and bot_delay_secs != 0:
                    print(f"Waiting to start next bot client right after bot client...\n"
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
                continue

            cur_client = await self.run_single_telethon_client(
                telethon_config=cur_config)
            if not cur_client:
                print(f"Current Telethon client not authorised and skipped [ERROR]\n"
                      f"cur_client: {cur_client}\n")
                continue  # Not necessary

        if self.clients:
            print(f"\nTelethon clients started successfully:")
            counter = 1
            for cur_tlt_config, cur_tlt_client in self.clients.items():
                print(f"{counter}. cur_telethon_config: {cur_tlt_config}, "
                      f"cur_telethon_client: {cur_tlt_client}")
                counter += 1

    async def run_single_telethon_client(
            self, telethon_config: TelethonConfig
    ) -> TelegramClient | None:
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
                single_tlt_client = await self.start_tlt_user_client(
                    telethon_config=telethon_config)
            elif account_type == TELEGRAM_ACCOUNT_TYPE.BOT:
                print(f"{'>' * 55}\n{'>' * 55}\n"
                      f">>>>>>> START SINGLE TELEGRAM BOT TELETHON CLIENT:\n"
                      f"telethon_config_id: {telethon_config_id}\n"
                      f"account_type: {account_type}\n"
                      f"telegram_phone: {telegram_phone}\n"
                      f"bot_token_info: {bot_token_info}\n"
                      f"config_name: {config_name}\n")
                single_tlt_client = await self.start_tlt_bot_client(
                    telethon_config=telethon_config)
            else:  # Telethon account type not defined
                print(f"Telethon client with empty account_type [ERROR]\n"
                      f"telethon_config_id: {telethon_config_id}\n"
                      f"account_type: {account_type}\n"
                      f"telegram_phone: {telegram_phone}\n"
                      f"bot_token_info: {bot_token_info}\n"
                      f"config_name: {config_name}\n")
                return None

            if not single_tlt_client:
                print(f"Not created or not authorised Telethon client [ERROR]:\n"
                      f"single_tlt_client: {single_tlt_client}\n"
                      f"telethon_config_id: {telethon_config_id}\n"
                      f"account_type: {account_type}\n"
                      f"telegram_phone: {telegram_phone}\n"
                      f"bot_token_info: {bot_token_info}\n"
                      f"config_name: {config_name}\n")
                return None
            print(f"Telethon client created and authorised [OK]:\n"
                  f"single_tlt_client: {single_tlt_client}\n"
                  f"telethon_config_id: {telethon_config_id}\n"
                  f"account_type: {account_type}\n"
                  f"telegram_phone: {telegram_phone}\n"
                  f"bot_token_info: {bot_token_info}\n"
                  f"config_name: {config_name}\n")

            print("Telethon client PGS-SQLite session saving:")
            # session_str = StringSession.save(single_tlt_client.session)  # Obtain session str from tlt client for PGS
            await self.postgres_db_save_tlt_session(
                telethon_client=single_tlt_client,
                telethon_config=telethon_config)
            print("Telethon client PGS-SQLite session saved [OK]\n")

            self.clients[config_name] = single_tlt_client

            print("Telethon client all handlers registering:")
            await self.register_tlt_client_handlers(
                telethon_client=single_tlt_client,
                telethon_config=telethon_config)
            print("Telethon client all handlers registered [OK]\n")
            return single_tlt_client
        except Exception as error:
            error_log = (f"Run single Telethon client [ERROR]:\n"
                         f"error: {error}\n"
                         f"config_name: {config_name}\n"
                         f"telethon_config_id: {telethon_config_id}\n"
                         f"account_type: {account_type}\n"
                         f"telegram_phone: {telegram_phone}\n"
                         f"bot_token_info: {bot_token_info}\n")
            print(error_log)

    async def start_tlt_user_client(
            self,
            telethon_config: TelethonConfig
    ) -> TelegramClient | None:
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

            session = SQLiteSession(session_id=session_full_file_path)
            print(f"New Telethon session created via SQLiteSession [OK]:\n"
                  f"session_str_info: {session_str_info}\n"
                  f"config_name: {config_name}\n"
                  f"new_session_id: {new_session_id}\n"
                  f"session_full_file_path: {session_full_file_path}\n"
                  f"session: {session}\n")

        if telethon_config.proxy:
            valid_proxy_config = await get_valid_proxy_tuple(
                raw_proxy_config=telethon_config.proxy)
        else:
            valid_proxy_config = None

        user_client = TelegramClient(
            session=session,
            api_id=telethon_config.api_id,
            api_hash=telethon_config.api_hash,
            proxy=valid_proxy_config,
            connection_retries=TELETHON_OPTIONS.TELEGRAM_CLIENT_CONNECT_RETRIES,
            request_retries=TELETHON_OPTIONS.TELEGRAM_CLIENT_REQUEST_RETRIES,
            flood_sleep_threshold=TELETHON_OPTIONS.FLOOD_SLEEP_THRESHOLD, )

        before_connect_is_connected = user_client.is_connected()
        print(f"Telethon User client state before connect():\n"
              f"before_connect_is_connected: {before_connect_is_connected}\n")

        if not before_connect_is_connected:
            await user_client.connect()

        after_connect_is_connected = user_client.is_connected()
        after_connect_is_authorised = await user_client.is_user_authorized()
        print(f"Telethon User client state after connect():\n"
              f"after_connect_is_connected: {after_connect_is_connected}\n"
              f"after_connect_is_authorised: {after_connect_is_authorised}\n")

        if not after_connect_is_authorised:
            await self.authorise_tlt_user_client(
                telethon_user_client=user_client,
                telethon_config=telethon_config)
            after_auth_is_connected = user_client.is_connected()
            after_auth_is_authorised = await user_client.is_user_authorized()
            print(f"Telethon User client state after authorise_tlt_user_client():\n"
                  f"after_auth_is_connected: {after_auth_is_connected}\n"
                  f"after_auth_is_authorised: {after_auth_is_authorised}\n")
            if after_auth_is_authorised:
                return user_client
            # return None  # Not necessary
        else:
            print(f"Telethon User client initially authorised:\n"
                  f"after_connect_is_connected: {after_connect_is_connected}\n"
                  f"after_connect_is_authorised: {after_connect_is_authorised}\n")
            return user_client

    @staticmethod
    async def postgres_db_save_tlt_session(
            telethon_config: TelethonConfig,
            telethon_client: TelegramClient
    ) -> bool:
        session_str = StringSession.save(telethon_client.session)  # Obtain session str from tlt client for PGS
        session_str_info = f"...{session_str[-15:]}" if session_str else None
        print(f"Telethon session string obtained from tlt client[OK]:\n"
              f"session_str_info: {session_str_info}\n")

        session_update_data = {"telethon_session_str": session_str}
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

    @staticmethod
    async def authorise_tlt_user_client(
            telethon_user_client: TelegramClient,
            telethon_config: TelethonConfig
    ) -> bool:
        config_name = telethon_config.name
        telegram_phone = telethon_config.phone
        user_client = telethon_user_client
        client_is_user_authorised = await user_client.is_user_authorized()
        if client_is_user_authorised:
            return True

        auth_type_choice = None
        request_sent_code = None
        phone_signed_in_user = None
        qr_code_login = None
        qr_code = None
        qrcode_signed_in_user = None
        session_str = None
        session_str_info = f"...{session_str[-15:]}" if session_str else None
        try:
            input_text = (f"Choose authorisation type for "
                          f"phone: {telegram_phone}, config name: {config_name}:\n"
                          f"1 - by telephone \n"
                          f"2 - by QR code \n"
                          f"3 - skip client\n"
                          f"Enter your choice: ")
            auth_type_choice = await asyncio.to_thread(
                input, input_text)

            if auth_type_choice == "1" and telegram_phone:
                print("Telethon user client authorising via phone")
                request_sent_code = await user_client.send_code_request(
                    phone=telegram_phone,
                    force_sms=False,  # Deprecated
                    _retry_count=0)
                print(f"Phone authorisation code sent to phone [OK]:\n"
                      f"request_sent_code: {request_sent_code}\n")

                input_text = "Enter Telegram code: "
                phone_auth_code = await asyncio.to_thread(
                    input, input_text)
                phone_signed_in_user = await user_client.sign_in(
                    phone=telegram_phone,
                    code=phone_auth_code,
                    password=None,
                    bot_token=None,
                    phone_code_hash=None)
                print(f"Phone user client authorised successfully [OK]:\n"
                      f"request_sent_code: {request_sent_code}\n"
                      f"phone_signed_in_user: {phone_signed_in_user}\n")
                return True
            elif auth_type_choice == "2":
                print("Telethon user client authorisation via QR code")
                qr_code_login = await user_client.qr_login(
                    ignored_ids=None)
                print(f"####### QR Сode object: {qr_code_login}")
                print(f"####### QR Code url: {qr_code_login.url}")

                print("Generating QR code in console")
                qr_code = qrcode.main.QRCode(
                    version=None,
                    error_correction=QR_CODE_ERROR_CORRECTION.LEVEL_M.value,
                    box_size=10,
                    border=4,
                    image_factory=None,
                    mask_pattern=None, )
                qr_code.add_data(qr_code_login.url, optimize=20)
                await asyncio.to_thread(qr_code.print_ascii)
                qrcode_signed_in_user = await qr_code_login.wait()
                print(f"QR Code user client authorised successfully [OK]:\n"
                      f"qr_code_login: {qr_code_login}\n"
                      f"qr_code: {qr_code}\n"
                      f"qrcode_signed_in_user: {qrcode_signed_in_user}\n")
                return True
            else:  # auth_type_choice == "3": or any other value
                return False
        except Exception as error:
            error_log = (f"Telethon User Client authorisation [ERROR]: \n"
                         f"error: {error}\n"
                         f"auth_type_choice: {auth_type_choice}\n"
                         f"request_sent_code: {request_sent_code}\n"
                         f"phone_signed_in_user: {phone_signed_in_user}\n"
                         f"qr_code_login: {qr_code_login}\n"
                         f"qr_code: {qr_code}\n"
                         f"qrcode_signed_in_user: {qrcode_signed_in_user}\n"
                         f"session_str_info: {session_str_info}\n"
                         f"auth_type_choice: {auth_type_choice}\n")
            print(error_log)
            return False

    @staticmethod
    async def start_tlt_bot_client(
            telethon_config: TelethonConfig
    ) -> TelegramClient | None:
        session_prefix = TELETHON_OPTIONS.BOT_SESSION_FILE_PREFIX
        config_name = telethon_config.name
        new_session_id = f"{session_prefix}{config_name}"
        telethon_sessions_dir = TELETHON_OPTIONS.BASE_TELETHON_SESSIONS_DIR
        session_full_file_path = get_full_file_normal_path(
            all_dir_str_parts=[BASE_DIR, telethon_sessions_dir],
            file_name_with_ext=new_session_id)

        if telethon_config.proxy:
            valid_proxy_config = await get_valid_proxy_tuple(
                raw_proxy_config=telethon_config.proxy)
        else:
            valid_proxy_config = None

        bot_client = TelegramClient(
            session=session_full_file_path,
            api_id=telethon_config.api_id,
            api_hash=telethon_config.api_hash,
            proxy=valid_proxy_config,
            connection_retries=TELETHON_OPTIONS.TELEGRAM_CLIENT_CONNECT_RETRIES,
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

        if not after_connect_is_authorised:
            await bot_client.start(  # Telethon bug: await is necessary. Error without await but sync start()
                bot_token=telethon_config.bot_token,
                force_sms=False,
                code_callback=None,
                first_name=telethon_config.web_account_id,
                last_name=telethon_config.web_account_username,
                max_attempts=3)

            after_start_is_connected = bot_client.is_connected()
            after_start_is_authorised = await bot_client.is_user_authorized()
            after_start_is_bot = await bot_client.is_bot()
            print(f"Telethon Bot client state after start():\n"
                  f"after_start_is_connected: {after_start_is_connected}\n"
                  f"after_start_is_authorised: {after_start_is_authorised}\n"
                  f"after_start_is_bot: {after_start_is_bot}\n")
            if after_start_is_authorised:
                return bot_client
            # return None  # Not necessary
        else:
            print(f"Telethon Bot client initially authorised:\n"
                  f"after_connect_is_connected: {after_connect_is_connected}\n"
                  f"after_connect_is_authorised: {after_connect_is_authorised}\n"
                  f"after_connect_is_bot: {after_connect_is_bot}\n")
            return bot_client

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
