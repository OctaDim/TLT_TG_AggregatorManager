from typing import Union

from fastapi import HTTPException, status

from configs.settings import API_USERNAME, API_PASSWORD


async def verify_auth_username_password(
        username: str,
        password: str
) -> Union[bool, HTTPException]:
    if (username != API_USERNAME
            or password != API_PASSWORD):
        log_text = (f"Wrong Telethon FastAPI username or password [ERROR]: "
                    f"username: {username[0]}...{username[-1]}, "
                    f"password: ***")
        print(log_text)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=log_text)
    return True
