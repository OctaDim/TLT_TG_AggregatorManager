from pydantic.dataclasses import dataclass


@dataclass
class AuthResponse:
    is_authorised: bool = False
    requires_action: bool = False
    auth_by_phone: bool = False
    auth_by_qrcode: bool = False
    auth_via_console: bool = False
    phone_code_hash: str | None = None
    qrcode_url: str | None = None
    qrcode_fpath: str | None = None
    is_auth_error: bool = False
    auth_message: str = ""
    auth_error: str = ""
