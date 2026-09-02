from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import BigInteger, Date, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, utcnow


class Vendor(Base):
    __tablename__ = "vendors"
    __table_args__ = (
        Index("ix_vendors_wedding_due", "wedding_id", "due_date"),
        Index("ix_vendors_wedding_status", "wedding_id", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    wedding_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("weddings.id", ondelete="CASCADE"), index=True
    )
    vendor_name: Mapped[str] = mapped_column(String(255))
    category: Mapped[str] = mapped_column(String(50), default="lainnya")
    contact_wa: Mapped[str | None] = mapped_column(String(50), nullable=True)
    total_amount: Mapped[int] = mapped_column(BigInteger, default=0)
    dp_amount: Mapped[int] = mapped_column(BigInteger, default=0)
    paid_amount: Mapped[int] = mapped_column(BigInteger, default=0)
    status: Mapped[str] = mapped_column(String(20), default="belum_bayar")
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    invoice_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow)

    wedding: Mapped[Wedding] = relationship(back_populates="vendors")  # noqa: F821
