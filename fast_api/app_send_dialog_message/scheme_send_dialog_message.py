from fastapi import HTTPException
from pydantic import BaseModel, model_validator
from starlette import status


class InSendDialogMessageData(BaseModel):
    messenger_type: str = "telegram"
    config_name: str
    peer_id: int
    peer_type: str
    peer_storage_type: str
    message_text: str

    @model_validator(mode="after")
    def validate_fields(self):
        if not self.config_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="config_name is empty [ERROR]")
        if self.peer_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="peer_id is empty [ERROR]")
        if not (self.message_text or "").strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="message_text is empty [ERROR]")
        return self

