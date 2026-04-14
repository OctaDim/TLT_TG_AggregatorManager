from typing import List

from pydantic import BaseModel


class InStopTltClients(BaseModel):
    telethon_configs_names: List[str]
