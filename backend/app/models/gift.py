from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import BigInteger, Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, utcnow


class Gift(Base):
    __tablename__ = "gifts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    wedding_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("weddings.id", ondelete="CASCADE"), index=True
    )
    guest_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("guests.id", ondelete="SET NULL"), nullable=True, index=True
    )
    type: Mapped[str] = mapped_column(String(20), default="kado")  # kado / uang / other
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    amount: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    received_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow)

    guest: Mapped[Guest | None] = relationship()  # noqa: F821
