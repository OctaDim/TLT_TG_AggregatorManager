from typing import Dict

from telethon.tl.custom import QRLogin

from meta_classes.singlton_meta import SingletonMeta


class QRCodeLoginsSingleton(metaclass=SingletonMeta):
    def __init__(self):
        self.qr_logins: Dict[str, QRLogin] = {}

    def get_qr_login(self, config_name: str) -> QRLogin | None:
        qr_login_obj = self.qr_logins.get(config_name)
        return qr_login_obj

    def save_qr_login(self, config_name: str,
                      qr_login_obj: QRLogin
                      ) -> None:
        self.qr_logins[config_name] = qr_login_obj
        return None

    def remove_qr_login(self, config_name: str) -> QRLogin | None:
        removed_qr_login = self.qr_logins.pop(config_name, None)
        return removed_qr_login
