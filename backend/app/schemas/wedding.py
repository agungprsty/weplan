import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PlanInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    slug: str
    price: int
    max_guests: int
    duration_months: int


class WeddingBase(BaseModel):
    title: str
    wedding_date: date | None = None
    partner1_name: str
    partner2_name: str
    total_budget: int | None = None


class WeddingCreate(WeddingBase):
    pass


class WeddingUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    wedding_date: date | None = None
    partner1_name: str | None = Field(default=None, min_length=1, max_length=255)
    partner2_name: str | None = Field(default=None, min_length=1, max_length=255)
    total_budget: int | None = Field(default=None, ge=0)

    @field_validator("title", "partner1_name", "partner2_name", mode="before")
    @classmethod
    def strip_names(cls, v):
        return v.strip() if isinstance(v, str) else v


class WeddingPairRequest(BaseModel):
    pair_code: str = Field(min_length=6, max_length=8)

    @field_validator("pair_code", mode="before")
    @classmethod
    def normalize_code(cls, v):
        return v.strip().upper() if isinstance(v, str) else v


class WeddingResponse(WeddingBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    pair_code: str
    plan: PlanInfo | None = None
    plan_expires_at: datetime | None = None
    member_count: int = 0
    created_at: datetime
    updated_at: datetime


class WeddingWithPartners(WeddingResponse):
    partner1_email: str | None = None
    partner2_email: str | None = None


class WeddingPreviewResponse(BaseModel):
    """Public preview untuk invite link: hanya info aman, tidak leak email/budget detail."""

    title: str
    partner1_name: str
    partner2_name: str
    wedding_date: date | None = None
    member_count: int = 0
    pair_code: str
    is_full: bool = False
