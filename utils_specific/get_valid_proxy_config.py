from copy import copy
from typing import Tuple

import python_socks

from utils_common.get_bool_or_none_from_str import get_bool_none_from_str


async def get_valid_proxy_tuple(
        raw_proxy_config: tuple | list | dict
) -> Tuple[str, str, int, bool, str, str]:
    _PROXY_TYPE_ASSOC = {"socks4": python_socks.ProxyType.SOCKS4,
                         "socks5": python_socks.ProxyType.SOCKS5,
                         "http": python_socks.ProxyType.HTTP}

    if isinstance(raw_proxy_config, (list, tuple)):
        raw_proxy_type = raw_proxy_config[0].lower()
        if raw_proxy_type in _PROXY_TYPE_ASSOC.keys():
            valid_proxy_type = _PROXY_TYPE_ASSOC[raw_proxy_type]
        else:
            valid_proxy_type = raw_proxy_type

        raw_proxy_rdns = raw_proxy_config[3]
        valid_proxy_rdns = await get_bool_none_from_str(raw_proxy_rdns)

        valid_proxy_config = list(copy(raw_proxy_config))
        valid_proxy_config[0] = valid_proxy_type
        valid_proxy_config[3] = valid_proxy_rdns
        valid_proxy_config = tuple(valid_proxy_config)
    elif isinstance(raw_proxy_config, dict):
        raw_proxy_type = raw_proxy_config["proxy_type"]
        if raw_proxy_type in _PROXY_TYPE_ASSOC.keys():
            valid_proxy_type = _PROXY_TYPE_ASSOC[raw_proxy_type]
        else:
            valid_proxy_type = raw_proxy_type

        raw_proxy_rdns = raw_proxy_config["rdns"]
        valid_proxy_rdns = await get_bool_none_from_str(raw_proxy_rdns)
        valid_proxy_config = (valid_proxy_type,  # validated
                              raw_proxy_config["addr"],
                              raw_proxy_config["port"],
                              valid_proxy_rdns,  # validated
                              raw_proxy_config["username"],
                              raw_proxy_config["password"])
    else:
        valid_proxy_config = raw_proxy_config
    print("################################################################### valid_proxy_config", valid_proxy_config)
    return valid_proxy_config
