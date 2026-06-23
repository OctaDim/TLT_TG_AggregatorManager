import os
import sys
from configparser import ConfigParser
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

from utils_common.get_cur_ip_address import (
    get_cur_external_ip_via_google_dns, get_cur_internal_ip)
from utils_common.normalized_path import get_full_file_normal_path

BASE_DIR = Path(__file__).resolve().parent.parent

# GETTING TEST ENV CONFIGS #############################################
test_env_normal_path = get_full_file_normal_path(
    all_dir_str_parts=[BASE_DIR],
    file_name_with_ext=".env")
env = load_dotenv(test_env_normal_path)  # for future
API_TEST_USERNAME = os.getenv("API_TEST_USERNAME")
API_TEST_PASSWORD = os.getenv("API_TEST_PASSWORD")

# GETTING CURRENT INTERNAL AND EXTERNAL IPs #############################
get_cur_internal_ip(log_ip=True)
cur_external_ip = get_cur_external_ip_via_google_dns(log_ip=True)


# GETTING API INI CONFIGS ##############################################
@dataclass(frozen=True)
class API_CONFIG_NAMES:
    API_PRODUCTION = "API_production"
    API_TEST = "API_test"
    API_TEST_ANY_IP = "API_any_ips"
    API_TEST_WIN_LOCALHOST = "API_win_localhost"
    API_TEST_UNIX_LOCALHOST = "API_unix_localhost"


api_ini_normal_path = get_full_file_normal_path(
    all_dir_str_parts=[BASE_DIR],
    file_name_with_ext=".configs_api.ini")
api_conf_parser = ConfigParser()
api_conf_parser.read(filenames=api_ini_normal_path)

if cur_external_ip == "___.___.___.___":  # Just example
    api_conf_name = API_CONFIG_NAMES.API_TEST
elif cur_external_ip == "P.R.O.D":
    api_conf_name = API_CONFIG_NAMES.API_PRODUCTION
elif cur_external_ip == "192.168.21.22":
    api_conf_name = API_CONFIG_NAMES.API_TEST
elif sys.platform == "linux":
    api_conf_name = API_CONFIG_NAMES.API_TEST_UNIX_LOCALHOST
elif sys.platform == "win32":
    api_conf_name = API_CONFIG_NAMES.API_TEST_WIN_LOCALHOST
else:
    api_conf_name = API_CONFIG_NAMES.API_TEST_ANY_IP

API_HOST: str = api_conf_parser.get(section=api_conf_name, option="API_HOST")
API_PORT: int = int(api_conf_parser.get(section=api_conf_name, option="API_PORT"))
API_USERNAME: str = api_conf_parser.get(section=api_conf_name, option="API_USERNAME")
API_PASSWORD: str = api_conf_parser.get(section=api_conf_name, option="API_PASSWORD")
FASTAPI_SESSION_KEY: str = api_conf_parser.get(section=api_conf_name, option="FASTAPI_SESSION_KEY")


# GETTING TELEGRAM API INI CONFIGS #####################################
@dataclass(frozen=True)
class TELEGRAM_API_CONFIG_NAMES:
    TG_OFFICIAL_API_production = "TELEGRAM_OFFICIAL_API_production"
    TG_OFFICIAL_API_test = "TELEGRAM_OFFICIAL_API_test_375296085622"


telegram_api_ini_normal_path = get_full_file_normal_path(
    all_dir_str_parts=[BASE_DIR],
    file_name_with_ext=".configs_telegram.ini")
telegram_api_conf_parser = ConfigParser()
telegram_api_conf_parser.read(filenames=telegram_api_ini_normal_path)

if cur_external_ip == "___.___.___.___":  # Just example
    telegram_api_conf_name = TELEGRAM_API_CONFIG_NAMES.TG_OFFICIAL_API_test  # Certain configs can be defined
if cur_external_ip == "P.R.O.D":
    telegram_api_conf_name = TELEGRAM_API_CONFIG_NAMES.TG_OFFICIAL_API_production
if cur_external_ip == "192.168.21.22":
    telegram_api_conf_name = TELEGRAM_API_CONFIG_NAMES.TG_OFFICIAL_API_test
else:
    telegram_api_conf_name = TELEGRAM_API_CONFIG_NAMES.TG_OFFICIAL_API_test

TELEGRAM_OFFICIAL_APP_API_ID = int(telegram_api_conf_parser.get(
    section=telegram_api_conf_name, option="TG_OFFICIAL_APP_API_ID"))
TELEGRAM_OFFICIAL_APP_API_HASH = telegram_api_conf_parser.get(
    section=telegram_api_conf_name, option="TG_OFFICIAL_APP_API_HASH")


# GETTING PROXY INI CONFIGS ##############################################
@dataclass(frozen=True)
class PROXY_CONFIG_NAMES:
    PROXY_PRODUCTION = "PROXY_production"
    PROXY_TEST = "PROXY_test"
    PROXY_TEST_ANY_IP = "PROXY_any_ips"
    PROXY_TEST_WIN_LOCALHOST = "PROXY_win_localhost"
    PROXY_TEST_UNIX_LOCALHOST = "PROXY_unix_localhost"


proxy_ini_normal_path = get_full_file_normal_path(
    all_dir_str_parts=[BASE_DIR],
    file_name_with_ext=".configs_proxy.ini")
proxy_conf_parser = ConfigParser()
proxy_conf_parser.read(filenames=proxy_ini_normal_path)

if cur_external_ip == "___.___.___.___":  # Just example
    proxy_conf_name = PROXY_CONFIG_NAMES.PROXY_TEST
elif cur_external_ip == "P.R.O.D":
    proxy_conf_name = PROXY_CONFIG_NAMES.PROXY_PRODUCTION
elif cur_external_ip == "192.168.21.22":
    proxy_conf_name = PROXY_CONFIG_NAMES.PROXY_TEST
elif sys.platform == "linux":
    proxy_conf_name = PROXY_CONFIG_NAMES.PROXY_TEST_UNIX_LOCALHOST
elif sys.platform == "win32":
    proxy_conf_name = PROXY_CONFIG_NAMES.PROXY_TEST_WIN_LOCALHOST
else:
    proxy_conf_name = PROXY_CONFIG_NAMES.PROXY_TEST_ANY_IP

PROXY_TYPE: str = proxy_conf_parser.get(section=proxy_conf_name, option="PROXY_TYPE")
PROXY_ADDR: str = proxy_conf_parser.get(section=proxy_conf_name, option="PROXY_ADDR")
PROXY_PORT: int = int(proxy_conf_parser.get(section=proxy_conf_name, option="PROXY_PORT"))
PROXY_RDNS: int = bool(proxy_conf_parser.get(section=proxy_conf_name, option="PROXY_RDNS"))
PROXY_USERNAME: str = proxy_conf_parser.get(section=proxy_conf_name, option="PROXY_USERNAME")
PROXY_PASSWORD: str = proxy_conf_parser.get(section=proxy_conf_name, option="PROXY_PASSWORD")


# GETTING SQLADMIN INI CONFIGS #########################################
@dataclass(frozen=True)
class SQLADMIN_CONFIG_NAMES:
    SQLADMIN_PRODUCTION = "SQLADMIN_production"
    SQLADMIN_TEST = "SQLADMIN_test"


sqladmin_ini_normal_path = get_full_file_normal_path(
    all_dir_str_parts=[BASE_DIR],
    file_name_with_ext=".configs_sqladmin.ini")
sqladmin_conf_parser = ConfigParser()
sqladmin_conf_parser.read(filenames=sqladmin_ini_normal_path)

if cur_external_ip == "___.___.___.___":  # Just example
    sqladmin_conf_name = SQLADMIN_CONFIG_NAMES.SQLADMIN_TEST
elif cur_external_ip == "P.R.O.D":
    sqladmin_conf_name = SQLADMIN_CONFIG_NAMES.SQLADMIN_PRODUCTION
elif cur_external_ip == "192.168.21.22":
    sqladmin_conf_name = SQLADMIN_CONFIG_NAMES.SQLADMIN_TEST
else:
    sqladmin_conf_name = SQLADMIN_CONFIG_NAMES.SQLADMIN_TEST

SQLADMIN_SUPERADMIN_USERNAME = sqladmin_conf_parser.get(
    section=sqladmin_conf_name, option="SQLADMIN_SUPERADMIN_USERNAME")
SQLADMIN_ADMIN_PASSWORD = sqladmin_conf_parser.get(
    section=sqladmin_conf_name, option="SQLADMIN_ADMIN_PASSWORD")
SQLADMIN_ADMIN_USERNAME = sqladmin_conf_parser.get(
    section=sqladmin_conf_name, option="SQLADMIN_ADMIN_USERNAME")
SQLADMIN_SUPERADMIN_PASSWORD = sqladmin_conf_parser.get(
    section=sqladmin_conf_name, option="SQLADMIN_SUPERADMIN_PASSWORD")


# GETTING POSTGRES INI CONFIGS #########################################
@dataclass(frozen=True)
class POSTGRES_CONFIG_NAMES:
    POSTGRES_PRODUCTION = "POSTGRES_production"
    POSTGRES_TEST = "POSTGRES_test"
    POSTGRES_TEST_ANY_IP = "POSTGRES_any_ips"
    POSTGRES_TEST_WIN_LOCALHOST = "POSTGRES_win_localhost"
    POSTGRES_TEST_UNIX_LOCALHOST = "POSTGRES_unix_localhost"


postgres_ini_normal_path = get_full_file_normal_path(
    all_dir_str_parts=[BASE_DIR],
    file_name_with_ext=".configs_postgres.ini")
postgres_conf_parser = ConfigParser()
postgres_conf_parser.read(filenames=postgres_ini_normal_path)

if cur_external_ip == "___.___.___.___":  # Just example
    postgres_conf_name = POSTGRES_CONFIG_NAMES.POSTGRES_TEST
elif cur_external_ip == "P.R.O.D":
    postgres_conf_name = POSTGRES_CONFIG_NAMES.POSTGRES_PRODUCTION
elif cur_external_ip == "192.168.21.22":
    postgres_conf_name = POSTGRES_CONFIG_NAMES.POSTGRES_TEST
elif sys.platform == "linux":
    postgres_conf_name = POSTGRES_CONFIG_NAMES.POSTGRES_TEST_UNIX_LOCALHOST
elif sys.platform == "win32":
    postgres_conf_name = POSTGRES_CONFIG_NAMES.POSTGRES_TEST_WIN_LOCALHOST
else:
    postgres_conf_name = POSTGRES_CONFIG_NAMES.POSTGRES_TEST_ANY_IP

POSTGRES_USER = postgres_conf_parser.get(section=postgres_conf_name, option="POSTGRES_USER")
POSTGRES_PASSWORD = postgres_conf_parser.get(section=postgres_conf_name, option="POSTGRES_PASSWORD")
POSTGRES_HOST = postgres_conf_parser.get(section=postgres_conf_name, option="POSTGRES_HOST")
POSTGRES_PORT = postgres_conf_parser.get(section=postgres_conf_name, option="POSTGRES_PORT") or None
POSTGRES_DB_NAME = postgres_conf_parser.get(section=postgres_conf_name, option="POSTGRES_DB_NAME")


# GETTING AGGREGATOR INI CONFIGS #########################################
@dataclass(frozen=True)
class AGGREGATOR_CONFIG_NAMES:
    AGGREGATOR_PRODUCTION = "AGGREGATOR_production"
    AGGREGATOR_TEST = "AGGREGATOR_test"
    AGGREGATOR_TEST_ANY_IP = "AGGREGATOR_any_ips"
    AGGREGATOR_TEST_WIN_LOCALHOST = "AGGREGATOR_win_localhost"
    AGGREGATOR_TEST_UNIX_LOCALHOST = "AGGREGATOR_unix_localhost"


aggregator_ini_normal_path = get_full_file_normal_path(
    all_dir_str_parts=[BASE_DIR],
    file_name_with_ext=".configs_aggregator.ini")
aggregator_conf_parser = ConfigParser()
aggregator_conf_parser.read(filenames=aggregator_ini_normal_path)

if cur_external_ip == "___.___.___.___":  # Just example
    aggregator_conf_name = AGGREGATOR_CONFIG_NAMES.AGGREGATOR_TEST
elif cur_external_ip == "192.168.21.22":
    aggregator_conf_name = AGGREGATOR_CONFIG_NAMES.AGGREGATOR_TEST
elif sys.platform == "linux":
    aggregator_conf_name = AGGREGATOR_CONFIG_NAMES.AGGREGATOR_TEST_UNIX_LOCALHOST
elif sys.platform == "win32":
    aggregator_conf_name = AGGREGATOR_CONFIG_NAMES.AGGREGATOR_TEST_WIN_LOCALHOST
else:
    aggregator_conf_name = AGGREGATOR_CONFIG_NAMES.AGGREGATOR_TEST

AGGREGATOR_USERNAME = aggregator_conf_parser.get(section=aggregator_conf_name, option="AGGREGATOR_USERNAME")
AGGREGATOR_PASSWORD = aggregator_conf_parser.get(section=aggregator_conf_name, option="AGGREGATOR_PASSWORD")
AGGREGATOR_HOST = aggregator_conf_parser.get(section=aggregator_conf_name, option="AGGREGATOR_HOST")
AGGREGATOR_PORT = aggregator_conf_parser.get(section=aggregator_conf_name, option="AGGREGATOR_PORT") or None

# Server-port for BERT classifier API to request
AGGREGATOR_API_SEVER_PORT = "{api_host}:{api_port}".format(
    api_host=AGGREGATOR_HOST, api_port=AGGREGATOR_PORT)


# GETTING S3 CONFIGS ###################################################
@dataclass(frozen=True)
class S3_CONFIG_NAMES:
    S3_PRODUCTION = "S3_production"
    S3_TEST = "S3_test"
    S3_TEST_ANY_IP = "S3_any_ips"
    S3_TEST_WIN_LOCALHOST = "S3_win_localhost"
    S3_TEST_UNIX_LOCALHOST = "S3_unix_localhost"


s3_ini_normal_path = get_full_file_normal_path(
    all_dir_str_parts=[BASE_DIR],
    file_name_with_ext=".configs_s3_aws_api.ini")
s3_conf_parser = ConfigParser()
s3_conf_parser.read(filenames=s3_ini_normal_path)

if cur_external_ip == "___.___.___.___":  # Just example
    s3_conf_name = S3_CONFIG_NAMES.S3_TEST
elif cur_external_ip == "P.R.O.D":
    s3_conf_name = S3_CONFIG_NAMES.S3_PRODUCTION
elif cur_external_ip == "192.168.21.22":
    s3_conf_name = S3_CONFIG_NAMES.S3_TEST
elif sys.platform == "linux":
    s3_conf_name = S3_CONFIG_NAMES.S3_TEST_UNIX_LOCALHOST
elif sys.platform == "win32":
    s3_conf_name = S3_CONFIG_NAMES.S3_TEST_WIN_LOCALHOST
else:
    s3_conf_name = S3_CONFIG_NAMES.S3_TEST_ANY_IP

S3_HOST = s3_conf_parser.get(section=s3_conf_name, option="S3_HOST")
S3_PORT = s3_conf_parser.get(section=s3_conf_name, option="S3_PORT")
S3_ACCESS_KEY = s3_conf_parser.get(section=s3_conf_name, option="S3_ACCESS_KEY")
S3_SECRET_KEY = s3_conf_parser.get(section=s3_conf_name, option="S3_SECRET_KEY")
S3_DEFAULT_BUCKET = s3_conf_parser.get(section=s3_conf_name, option="S3_DEFAULT_BUCKET")
S3_SERVICE_NAME = s3_conf_parser.get(section=s3_conf_name, option="S3_SERVICE_NAME")
S3_REGION_NAME = s3_conf_parser.get(section=s3_conf_name, option="S3_REGION_NAME")

# Server-port for BERT classifier API to request
S3_API_ENDPOINT = "http://{s3_api_host}:{s3_api_port}".format(  # HTTP, Server doesn't have SSL certificates
    s3_api_host=S3_HOST, s3_api_port=S3_PORT)
# S3_API_ENDPOINT = "https://{s3_api_host}:{s3_api_port}".format(
#     s3_api_host=S3_HOST, s3_api_port=S3_PORT)
