from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import ActivityAction, EntityType
from app.models.base import Base, utcnow

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.wedding import Wedding


class Activity(Base):
    __tablename__ = "activities"
    __table_args__ = (
        Index("ix_activities_wedding_created", "wedding_id", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    wedding_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("weddings.id", ondelete="CASCADE"), index=True
    )
    actor_user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    # StrEnum → still stored as String, type-safe in Python
    action: Mapped[ActivityAction] = mapped_column(String(30))
    entity_type: Mapped[EntityType] = mapped_column(String(30))
    entity_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
    title: Mapped[str] = mapped_column(String(255))
    meta_data: Mapped[dict[str, Any] | None] = mapped_column(
        "meta", JSON, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(default=utcnow, index=True)

    wedding: Mapped["Wedding"] = relationship(back_populates="activities")  # noqa: F821, UP037
    actor: Mapped["User | None"] = relationship()  # noqa: F821, UP037
