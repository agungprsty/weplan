import uuid
from datetime import date, datetime

from sqlalchemy import BigInteger, Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, utcnow


class Wedding(Base):
    __tablename__ = "weddings"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255))
    wedding_date: Mapped[date | None] = mapped_column(Date(), nullable=True)
    partner1_name: Mapped[str] = mapped_column(String(255))
    partner2_name: Mapped[str] = mapped_column(String(255))
    total_budget: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    plan_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("plans.id", ondelete="SET NULL"), nullable=True
    )
    pair_code: Mapped[str] = mapped_column(String(8), unique=True, index=True)
    plan_expires_at: Mapped[datetime | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow)

    wedding_users: Mapped[list["WeddingUser"]] = relationship(
        back_populates="wedding", cascade="all, delete-orphan"
    )
    guests: Mapped[list["Guest"]] = relationship(
        back_populates="wedding", cascade="all, delete-orphan"
    )
    checklists: Mapped[list["Checklist"]] = relationship(
        back_populates="wedding", cascade="all, delete-orphan"
    )
    vendors: Mapped[list["Vendor"]] = relationship(
        back_populates="wedding", cascade="all, delete-orphan"
    )
    kua_documents: Mapped[list["KuaDocument"]] = relationship(
        back_populates="wedding", cascade="all, delete-orphan"
    )
    mahar_items: Mapped[list["MaharItem"]] = relationship(
        back_populates="wedding", cascade="all, delete-orphan"
    )
    savings_target: Mapped["SavingsTarget | None"] = relationship(
        back_populates="wedding", cascade="all, delete-orphan", uselist=False
    )
    transactions: Mapped[list["Transaction"]] = relationship(
        back_populates="wedding", cascade="all, delete-orphan"
    )
    cortage_items: Mapped[list["CortageItem"]] = relationship(
        back_populates="wedding", cascade="all, delete-orphan"
    )

    @property
    def bridesmaid_items(self) -> list["CortageItem"]:  # backwards compat
        return self.cortage_items

    @bridesmaid_items.setter
    def bridesmaid_items(self, value: list["CortageItem"]) -> None:
        self.cortage_items = value
    plan: Mapped["Plan | None"] = relationship()
