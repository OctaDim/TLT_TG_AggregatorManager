from typing import List

from pydantic import BaseModel


class InStopClearTltClients(BaseModel):
    telethon_configs_names: List[str]
