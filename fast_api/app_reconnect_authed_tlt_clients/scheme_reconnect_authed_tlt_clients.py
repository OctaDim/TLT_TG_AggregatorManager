from typing import List

from pydantic import BaseModel


class InReconnectAuthedTltClients(BaseModel):
    telethon_configs_names: List[str]
