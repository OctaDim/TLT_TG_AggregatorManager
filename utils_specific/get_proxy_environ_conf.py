from typing import Dict, Union

from configs.environments import (
    PROXY_TYPE, PROXY_ADDR, PROXY_PORT, PROXY_RDNS, PROXY_USERNAME,
    PROXY_PASSWORD)


async def get_proxy_environ_config() -> Dict[str, Union[str, int, bool]]:
    all_environs_flag = all([bool(PROXY_TYPE),
                             bool(PROXY_ADDR),
                             bool(PROXY_PORT),
                             PROXY_RDNS in [True, False],
                             bool(PROXY_USERNAME),
                             bool(PROXY_USERNAME)])

    if all_environs_flag:
        environ_proxy_config = {"proxy_type": PROXY_TYPE,
                                "addr": PROXY_ADDR,
                                "port": PROXY_PORT,
                                "rdns": PROXY_RDNS,
                                "username": PROXY_USERNAME,
                                "password": PROXY_PASSWORD}
    else:
        environ_proxy_config = None
    return environ_proxy_config
