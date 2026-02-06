from typing import Optional

from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column

from db_postgres.postgres_init.declarative_base_model import Base
from db_postgres.postgres_models.orm_models_fields_mixins import (
    ActiveMix, CreateUpdateMix)


class TelethonConfigModel(Base, ActiveMix, CreateUpdateMix):
    __tablename__ = "telethon_config"

    id: Mapped[int] = mapped_column(primary_key=True)
    # customer_id: Mapped[int] = mapped_column(
    #     BigInteger, ForeignKey("customer.id"))

    # config_name: Mapped[Optional[str]] = None
    web_account_id: Mapped[str]
    web_account_username: Mapped[str]
    tg_account_type: Mapped[str]
    tg_api_id: Mapped[Optional[int]]
    tg_api_hash: Mapped[Optional[str]]
    telethon_session_str: Mapped[Optional[str]]
    tg_bot_token: Mapped[Optional[str]]
    tg_personal_phone: Mapped[Optional[str]]
    telethon_proxy_config: Mapped[Optional[dict]] = mapped_column(JSON)
    telethon_is_active: Mapped[bool] = mapped_column(default=False)
