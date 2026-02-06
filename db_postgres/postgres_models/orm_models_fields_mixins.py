from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column


class ActiveMix:
    __abstract__ = True
    active: Mapped[Optional[bool]] = mapped_column(default=True)


class LocalCreateUpdateMix:
    __abstract__ = True
    local_created_at: Mapped[Optional[datetime]] = mapped_column(
        default=datetime.now)
    local_updated_at: Mapped[Optional[datetime]] = mapped_column(
        onupdate=datetime.now)


class CreateUpdateMix:
    __abstract__ = True
    created_at: Mapped[Optional[datetime]] = mapped_column(
        default=datetime.now)
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        onupdate=datetime.now)


class StatusMix:
    __abstract__ = True
    local_status: Mapped[Optional[str]]

class CreateReasonMix:
    __abstract__ = True
    creation_reason: Mapped[Optional[str]]
