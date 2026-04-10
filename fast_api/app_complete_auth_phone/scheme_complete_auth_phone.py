from pydantic import BaseModel


class InCompleteAuthPhoneData(BaseModel):
    telethon_config_name: str
    telegram_phone: str
    telegram_phone_code: str
    phone_code_hash: str
