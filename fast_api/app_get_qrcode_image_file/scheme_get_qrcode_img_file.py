from pydantic import BaseModel


class InQRCodeImgData(BaseModel):
    qr_code_fpath: str
    # qr_code_url: str
