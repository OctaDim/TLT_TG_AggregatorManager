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
    API_PRODUCT_SERVER_IP = "API_production"
    API_HAKASIA_PROD_SERVER_IP = "API_Hakasia_product_server"
    API_TEST_176_124_136_22_IP = "API_test_server_176_124_136_22_8000"
    API_TEST_192_168_21_22_IP = "API_test_server_192_168_21_22_8000"
    API_TEST_PORT_ANY_IP = "API_port_all_ips_0_0_0_0_8000"
    API_TEST_WIN_LOCALHOST = "API_win_localhost_127_0_0_1_8000"
    API_TEST_UNIX_LOCALHOST = "API_unix_localhost_127_0_1_1_8000"
    API_TEST_DEXP_1_IP = "API_dexp_ip_192_168_0_117_8000"
    API_TEST_DEXP_2_IP = "API_dexp_ip_192_168_0_106_8000"


api_ini_normal_path = get_full_file_normal_path(
    all_dir_str_parts=[BASE_DIR],
    file_name_with_ext=".configs_api.ini")
api_conf_parser = ConfigParser()
api_conf_parser.read(filenames=api_ini_normal_path)

if cur_external_ip == "___.___.___.___":  # Just example
    api_conf_name = API_CONFIG_NAMES.API_TEST_PORT_ANY_IP
elif cur_external_ip == "172.19.201.24":
    api_conf_name = API_CONFIG_NAMES.API_PRODUCT_SERVER_IP
elif cur_external_ip == "172.19.201.24":
    api_conf_name = API_CONFIG_NAMES.API_HAKASIA_PROD_SERVER_IP
elif cur_external_ip == "176.124.136.22":
    api_conf_name = API_CONFIG_NAMES.API_TEST_176_124_136_22_IP
elif cur_external_ip == "192.168.21.22":
    api_conf_name = API_CONFIG_NAMES.API_TEST_192_168_21_22_IP
elif cur_external_ip == "192.168.0.117":
    api_conf_name = API_CONFIG_NAMES.API_TEST_DEXP_1_IP
elif cur_external_ip == "192.168.0.106":
    api_conf_name = API_CONFIG_NAMES.API_TEST_DEXP_2_IP
elif sys.platform == "linux":
    api_conf_name = API_CONFIG_NAMES.API_TEST_UNIX_LOCALHOST
elif sys.platform == "win32":
    api_conf_name = API_CONFIG_NAMES.API_TEST_WIN_LOCALHOST
else:
    api_conf_name = API_CONFIG_NAMES.API_TEST_PORT_ANY_IP

API_HOST: str = api_conf_parser.get(section=api_conf_name, option="API_HOST")
API_PORT: int = int(api_conf_parser.get(section=api_conf_name, option="API_PORT"))
API_USERNAME: str = api_conf_parser.get(section=api_conf_name, option="API_USERNAME")
API_PASSWORD: str = api_conf_parser.get(section=api_conf_name, option="API_PASSWORD")
FASTAPI_SESSION_KEY: str = api_conf_parser.get(section=api_conf_name, option="FASTAPI_SESSION_KEY")


# GETTING TELEGRAM API INI CONFIGS #####################################
@dataclass(frozen=True)
class TELEGRAM_API_CONFIG_NAMES:
    TG_OFFICIAL_API_any_ip_prod = "TELEGRAM_OFFICIAL_API_any_ip_prod"
    TG_OFFICIAL_API_TEST_375296085622 = "TELEGRAM_OFFICIAL_API_TEST_375296085622"


telegram_api_ini_normal_path = get_full_file_normal_path(
    all_dir_str_parts=[BASE_DIR],
    file_name_with_ext=".configs_telegram.ini")
telegram_api_conf_parser = ConfigParser()
telegram_api_conf_parser.read(filenames=telegram_api_ini_normal_path)

if cur_external_ip == "___.___.___.___":  # Just example
    telegram_api_conf_name = TELEGRAM_API_CONFIG_NAMES.TG_OFFICIAL_API_any_ip_prod  # Certain configs can be defined
if cur_external_ip == "176.124.136.22":  # Just example
    telegram_api_conf_name = TELEGRAM_API_CONFIG_NAMES.TG_OFFICIAL_API_TEST_375296085622
else:
    telegram_api_conf_name = TELEGRAM_API_CONFIG_NAMES.TG_OFFICIAL_API_TEST_375296085622

TELEGRAM_OFFICIAL_APP_API_ID = int(telegram_api_conf_parser.get(
    section=telegram_api_conf_name, option="TG_OFFICIAL_APP_API_ID"))
TELEGRAM_OFFICIAL_APP_API_HASH = telegram_api_conf_parser.get(
    section=telegram_api_conf_name, option="TG_OFFICIAL_APP_API_HASH")


# GETTING PROXY INI CONFIGS ##############################################
@dataclass(frozen=True)
class PROXY_CONFIG_NAMES:
    PROXY_PRODUCT_SERVER_IP = "PROXY_production"
    PROXY_HAKASIA_PROD_SERVER_IP = "PROXY_Hakasia_product_server"
    PROXY_TEST_176_124_136_22_IP = "PROXY_test_server_176_124_136_22_8000"
    PROXY_TEST_192_168_21_22_IP = "PROXY_test_server_192_168_21_22_8000"
    PROXY_TEST_PORT_ANY_IP = "PROXY_port_all_ips_0_0_0_0_8000"
    PROXY_TEST_WIN_LOCALHOST = "PROXY_win_localhost_127_0_0_1_8000"
    PROXY_TEST_UNIX_LOCALHOST = "PROXY_unix_localhost_127_0_1_1_8000"
    PROXY_TEST_DEXP_1_IP = "PROXY_dexp_ip_192_168_0_117_8000"
    PROXY_TEST_DEXP_2_IP = "PROXY_dexp_ip_192_168_0_106_8000"


proxy_ini_normal_path = get_full_file_normal_path(
    all_dir_str_parts=[BASE_DIR],
    file_name_with_ext=".configs_proxy.ini")
proxy_conf_parser = ConfigParser()
proxy_conf_parser.read(filenames=proxy_ini_normal_path)

if cur_external_ip == "___.___.___.___":  # Just example
    proxy_conf_name = PROXY_CONFIG_NAMES.PROXY_TEST_PORT_ANY_IP
elif cur_external_ip == "172.19.201.24":
    proxy_conf_name = PROXY_CONFIG_NAMES.PROXY_PRODUCT_SERVER_IP
elif cur_external_ip == "172.19.201.24":
    proxy_conf_name = PROXY_CONFIG_NAMES.PROXY_HAKASIA_PROD_SERVER_IP
elif cur_external_ip == "176.124.136.22":
    proxy_conf_name = PROXY_CONFIG_NAMES.PROXY_TEST_176_124_136_22_IP
elif cur_external_ip == "192.168.21.22":
    proxy_conf_name = PROXY_CONFIG_NAMES.PROXY_TEST_192_168_21_22_IP
elif cur_external_ip == "192.168.0.117":
    proxy_conf_name = PROXY_CONFIG_NAMES.PROXY_TEST_DEXP_1_IP
elif cur_external_ip == "192.168.0.106":
    proxy_conf_name = PROXY_CONFIG_NAMES.PROXY_TEST_DEXP_2_IP
elif sys.platform == "linux":
    proxy_conf_name = PROXY_CONFIG_NAMES.PROXY_TEST_UNIX_LOCALHOST
elif sys.platform == "win32":
    proxy_conf_name = PROXY_CONFIG_NAMES.PROXY_TEST_WIN_LOCALHOST
else:
    proxy_conf_name = PROXY_CONFIG_NAMES.PROXY_TEST_PORT_ANY_IP

PROXY_TYPE: str = proxy_conf_parser.get(section=proxy_conf_name, option="PROXY_TYPE")
PROXY_ADDR: str = proxy_conf_parser.get(section=proxy_conf_name, option="PROXY_ADDR")
PROXY_PORT: int = int(proxy_conf_parser.get(section=proxy_conf_name, option="PROXY_PORT"))
PROXY_RDNS: int = bool(proxy_conf_parser.get(section=proxy_conf_name, option="PROXY_RDNS"))
PROXY_USERNAME: str = proxy_conf_parser.get(section=proxy_conf_name, option="PROXY_USERNAME")
PROXY_PASSWORD: str = proxy_conf_parser.get(section=proxy_conf_name, option="PROXY_PASSWORD")


# GETTING SQLADMIN INI CONFIGS #########################################
@dataclass(frozen=True)
class SQLADMIN_CONFIG_NAMES:
    SQLADMIN_PRODUCT_ANY_IP = "SQLADMIN_any_ip_prod"


sqladmin_ini_normal_path = get_full_file_normal_path(
    all_dir_str_parts=[BASE_DIR],
    file_name_with_ext=".configs_sqladmin.ini")
sqladmin_conf_parser = ConfigParser()
sqladmin_conf_parser.read(filenames=sqladmin_ini_normal_path)

if cur_external_ip == "___.___.___.___":
    sqladmin_conf_name = SQLADMIN_CONFIG_NAMES.SQLADMIN_PRODUCT_ANY_IP  # Certain configs can be defined
else:
    sqladmin_conf_name = SQLADMIN_CONFIG_NAMES.SQLADMIN_PRODUCT_ANY_IP

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
    POSTGRES_PRODUCT_SERVER_IP = "Postgres_production"
    POSTGRES_HAKASIA_PROD_SERVER_IP = "Postgres_Hakasia_product_server"
    POSTGRES_TEST_176_124_136_22_IP = "Postgres_prod_server_176_124_136_22"
    POSTGRES_TEST_PORT_ANY_IP = "Postgres_port_all_ips_0_0_0_0_8000"
    POSTGRES_TEST_WIN_LOCALHOST = "Postgres_win_localhost_127_0_0_1_8000"
    POSTGRES_TEST_UNIX_LOCALHOST = "Postgres_unix_localhost_127_0_1_1_8000"
    POSTGRES_TEST_DEXP_IP = "Postgres_dexp_ip_192_168_0_117_8000"


postgres_ini_normal_path = get_full_file_normal_path(
    all_dir_str_parts=[BASE_DIR],
    file_name_with_ext=".configs_postgres.ini")
postgres_conf_parser = ConfigParser()
postgres_conf_parser.read(filenames=postgres_ini_normal_path)

if cur_external_ip == "___.___.___.___":  # Just example
    postgres_conf_name = POSTGRES_CONFIG_NAMES.POSTGRES_TEST_PORT_ANY_IP
elif cur_external_ip == "172.19.201.24":
    postgres_conf_name = POSTGRES_CONFIG_NAMES.POSTGRES_PRODUCT_SERVER_IP
elif cur_external_ip == "172.19.201.24":
    postgres_conf_name = POSTGRES_CONFIG_NAMES.POSTGRES_HAKASIA_PROD_SERVER_IP
elif cur_external_ip == "176.124.136.22":
    postgres_conf_name = POSTGRES_CONFIG_NAMES.POSTGRES_TEST_176_124_136_22_IP
elif cur_external_ip == "192.168.0.117":
    postgres_conf_name = POSTGRES_CONFIG_NAMES.POSTGRES_TEST_DEXP_IP
elif sys.platform == "linux":
    postgres_conf_name = POSTGRES_CONFIG_NAMES.POSTGRES_TEST_UNIX_LOCALHOST
elif sys.platform == "win32":
    postgres_conf_name = POSTGRES_CONFIG_NAMES.POSTGRES_TEST_WIN_LOCALHOST
else:
    postgres_conf_name = POSTGRES_CONFIG_NAMES.POSTGRES_TEST_PORT_ANY_IP

POSTGRES_USER = postgres_conf_parser.get(section=postgres_conf_name, option="POSTGRES_USER")
POSTGRES_PASSWORD = postgres_conf_parser.get(section=postgres_conf_name, option="POSTGRES_PASSWORD")
POSTGRES_HOST = postgres_conf_parser.get(section=postgres_conf_name, option="POSTGRES_HOST")
POSTGRES_PORT = postgres_conf_parser.get(section=postgres_conf_name, option="POSTGRES_PORT") or None
POSTGRES_DB_NAME = postgres_conf_parser.get(section=postgres_conf_name, option="POSTGRES_DB_NAME")


# GETTING AGGREGATOR INI CONFIGS #########################################
@dataclass(frozen=True)
class AGGREGATOR_CONFIG_NAMES:
    AGGREGATOR_PRODUCT_SERVER_IP = "AGGREGATOR_production"
    AGGREGATOR_HAKASIA_SERVER_IP = "AGGREGATOR_Hakasia_product_server"
    AGGREGATOR_TEST_176_124_136_22_IP = "AGGREGATOR_test_176_124_136_22"
    AGGREGATOR_TEST_PORT_ANY_IP = "AGGREGATOR_all_ips_0_0_0_0"
    AGGREGATOR_TEST_WIN_LOCALHOST = "AGGREGATOR_win_localhost_127_0_0_1"
    AGGREGATOR_TEST_UNIX_LOCALHOST = "AGGREGATOR_unix_localhost_127_0_1_1"
    AGGREGATOR_TEST_DEXP_IP = "AGGREGATOR_dexp_ip_192_168_0_106"


aggregator_ini_normal_path = get_full_file_normal_path(
    all_dir_str_parts=[BASE_DIR],
    file_name_with_ext=".configs_aggregator.ini")
aggregator_conf_parser = ConfigParser()
aggregator_conf_parser.read(filenames=aggregator_ini_normal_path)

if cur_external_ip == "___.___.___.___":  # Just example
    aggregator_conf_name = AGGREGATOR_CONFIG_NAMES.AGGREGATOR_TEST_176_124_136_22_IP
elif cur_external_ip == "172.19.201.24":
    aggregator_conf_name = AGGREGATOR_CONFIG_NAMES.AGGREGATOR_PRODUCT_SERVER_IP
elif cur_external_ip == "172.19.201.24":
    aggregator_conf_name = AGGREGATOR_CONFIG_NAMES.AGGREGATOR_HAKASIA_SERVER_IP
elif cur_external_ip == "176.124.136.22":
    aggregator_conf_name = AGGREGATOR_CONFIG_NAMES.AGGREGATOR_TEST_176_124_136_22_IP
elif cur_external_ip == "192.168.0.117":
    aggregator_conf_name = AGGREGATOR_CONFIG_NAMES.AGGREGATOR_TEST_DEXP_IP
elif sys.platform == "linux":
    aggregator_conf_name = AGGREGATOR_CONFIG_NAMES.AGGREGATOR_TEST_UNIX_LOCALHOST
elif sys.platform == "win32":
    aggregator_conf_name = AGGREGATOR_CONFIG_NAMES.AGGREGATOR_TEST_WIN_LOCALHOST
else:
    aggregator_conf_name = AGGREGATOR_CONFIG_NAMES.AGGREGATOR_TEST_PORT_ANY_IP

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
    S3_PRODUCT_SERVER_IP = "S3_production"
    S3_TEST_SERVER_IP = "S3_test_176_124_136_22"
    S3_TEST_PORT_ANY_IP = "S3_all_ips_0_0_0_0"
    S3_TEST_WIN_LOCALHOST = "S3_win_localhost_127_0_0_1"
    S3_TEST_UNIX_LOCALHOST = "S3_unix_localhost_127_0_1_1"
    S3_TEST_DEXP_IP = "S3_dexp_ip_192_168_0_106"


s3_ini_normal_path = get_full_file_normal_path(
    all_dir_str_parts=[BASE_DIR],
    file_name_with_ext=".configs_s3_aws_api.ini")
s3_conf_parser = ConfigParser()
s3_conf_parser.read(filenames=s3_ini_normal_path)

if cur_external_ip == "___.___.___.___":  # Just example
    s3_conf_name = S3_CONFIG_NAMES.S3_TEST_SERVER_IP
elif cur_external_ip == "172.19.201.24":
    s3_conf_name = S3_CONFIG_NAMES.S3_TEST_SERVER_IP
elif cur_external_ip == "176.124.136.22":
    s3_conf_name = S3_CONFIG_NAMES.S3_TEST_SERVER_IP
elif cur_external_ip == "192.168.0.117":
    s3_conf_name = S3_CONFIG_NAMES.S3_TEST_DEXP_IP
elif sys.platform == "linux":
    s3_conf_name = S3_CONFIG_NAMES.S3_TEST_UNIX_LOCALHOST
elif sys.platform == "win32":
    s3_conf_name = S3_CONFIG_NAMES.S3_TEST_WIN_LOCALHOST
else:
    s3_conf_name = S3_CONFIG_NAMES.S3_TEST_PORT_ANY_IP

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
