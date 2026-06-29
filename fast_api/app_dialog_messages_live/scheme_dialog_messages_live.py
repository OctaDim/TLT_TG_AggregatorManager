from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel, model_validator
from starlette import status


class InDialogMessagesLiveData(BaseModel):
    messenger_type: str = "telegram"
    config_name: str
    peer_id: int
    peer_type: str
    peer_storage_type: str
    after_message_id: Optional[int] = None
    messages_limit: int = 50

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
        if self.messages_limit < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="messages_limit must be positive [ERROR]")
        return self

