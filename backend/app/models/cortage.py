from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import BigInteger, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, utcnow


class CortageItem(Base):
    __tablename__ = "cortage_items"
    __table_args__ = (UniqueConstraint("guest_id", name="bridesmaid_items_guest_id_key"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    wedding_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("weddings.id", ondelete="CASCADE"), index=True
    )
    guest_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("guests.id", ondelete="CASCADE"), index=True
    )
    uniform_size: Mapped[str | None] = mapped_column(String(20), nullable=True)
    fitting_status: Mapped[str] = mapped_column(String(20), default="pending")
    payment_status: Mapped[str] = mapped_column(String(20), default="belum_bayar")
    price: Mapped[int] = mapped_column(BigInteger, default=0)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow)

    wedding: Mapped[Wedding] = relationship(back_populates="cortage_items")  # noqa: F821
    guest: Mapped[Guest] = relationship(back_populates="cortage_detail")  # noqa: F821
