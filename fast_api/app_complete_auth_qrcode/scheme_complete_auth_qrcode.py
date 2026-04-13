from pydantic import BaseModel


class InCompleteAuthQRCodeData(BaseModel):
    telethon_config_name: str
    qr_code_file_path: str
    qr_code_url: str
