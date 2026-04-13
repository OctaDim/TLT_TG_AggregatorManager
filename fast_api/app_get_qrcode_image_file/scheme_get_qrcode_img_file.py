from pydantic import BaseModel, model_validator
from starlette import status
from starlette.exceptions import HTTPException


class InQRCodeImgData(BaseModel):
    qr_code_fpath: str
    qr_code_url: str

    @model_validator(mode="before")
    def validate_fields(cls, data):
        qr_code_fpath = data.get("qr_code_fpath")
        qr_code_url = data.get("qr_code_url")

        if not qr_code_fpath or not qr_code_url:
            error_log = (f"\nEmpty parameters passed [ERROR]:\n"
                         f"Possible combinations: "
                         f"[qr_code_fpath AND qr_code_url]\n"
                         f"qr_code_fpath: {qr_code_fpath}\n"
                         f"qr_code_url: {qr_code_url}\n")
            print(error_log)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=error_log)
        return data
