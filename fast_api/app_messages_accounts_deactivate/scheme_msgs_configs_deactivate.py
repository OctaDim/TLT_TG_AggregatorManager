from typing import List

from pydantic import BaseModel


class InDeactivateMsgsConfigs(BaseModel):
    telethon_configs_names: List[str]
