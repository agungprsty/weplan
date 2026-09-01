from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, utcnow


class Guest(Base):
    __tablename__ = "guests"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    wedding_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("weddings.id", ondelete="CASCADE")
    )
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    category: Mapped[str] = mapped_column(String(50), default="general")
    rsvp_status: Mapped[str] = mapped_column(String(20), default="pending")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    side: Mapped[str] = mapped_column(String(10), default="both")
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow)

    wedding: Mapped[Wedding] = relationship(back_populates="guests")
    cortage_detail: Mapped[CortageItem | None] = relationship(
        back_populates="guest", cascade="all, delete-orphan", uselist=False
    )

    @property
    def bridesmaid_detail(self) -> CortageItem | None:  # backwards compat
        return self.cortage_detail

    @bridesmaid_detail.setter
    def bridesmaid_detail(self, value: CortageItem | None) -> None:
        self.cortage_detail = value
