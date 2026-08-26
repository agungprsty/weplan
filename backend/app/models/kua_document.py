from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, utcnow


class KuaDocument(Base):
    __tablename__ = "kua_documents"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    wedding_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("weddings.id", ondelete="CASCADE"), index=True
    )
    owner_type: Mapped[str] = mapped_column(String(20), default="both")
    document_key: Mapped[str] = mapped_column(String(50))
    title: Mapped[str] = mapped_column(String(255))
    is_required: Mapped[bool] = mapped_column(Boolean, default=True)
    status: Mapped[str] = mapped_column(String(20), default="belum")
    file_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    expiry_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow)

    wedding: Mapped["Wedding"] = relationship(back_populates="kua_documents")  # noqa: F821
