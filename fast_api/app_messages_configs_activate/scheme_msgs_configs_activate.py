from typing import List

from pydantic import BaseModel


class InActivateMsgsConfigs(BaseModel):
    telethon_configs_names: List[str]
