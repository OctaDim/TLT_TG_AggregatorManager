from typing import Optional, Union, Tuple, TypeAlias, Literal

import python_socks
import socks
from pydantic import BaseModel, field_validator

from configs.enums import TELEGRAM_ACCOUNT_TYPE

# _PROXY_LIST_ALIAS: TypeAlias = List[Union[str, int, bool]]
_PROXY_TUPLE_ALIAS: TypeAlias = Tuple[str, str, int, bool, str, str]


class TelethonConfig(BaseModel):
    web_account_id: str
    web_account_username: str
    telethon_config_id: int
    name: Optional[str] = None
    account_type: TELEGRAM_ACCOUNT_TYPE
    api_id: int
    api_hash: str
    session_string: Optional[str] = None
    bot_token: Optional[str] = None
    phone: Optional[str] = None
    proxy: Optional[Union[_PROXY_TUPLE_ALIAS]] = None
    is_active: bool = True
    authorisation_type: Literal["console", "phone", "qrcode", "qr+phone"]

    @field_validator("proxy")
    @classmethod
    def validate_proxy(cls, proxy_tuple: tuple | list) -> tuple | list | None:
        if proxy_tuple is None:
            return proxy_tuple
        _ALLOWED_PROTOCOLS = (
            "socks4", socks.SOCKS4, python_socks.ProxyType.SOCKS4,
            "socks5", socks.SOCKS5, python_socks.ProxyType.SOCKS5,
            "http", socks.HTTP, python_socks.ProxyType.HTTP,)
        proxy_protocol = proxy_tuple[0]
        if isinstance(proxy_protocol, str):
            proxy_protocol = proxy_protocol.lower()

        if proxy_protocol not in _ALLOWED_PROTOCOLS:
            error_log = (f"Proxy Protocol [ERROR]: \n"
                         f"proxy_protocol: {proxy_protocol}, \n"
                         f"_ALLOWED_PROTOCOLS: {_ALLOWED_PROTOCOLS}\n")
            print(error_log)
            raise ValueError
        return proxy_tuple
