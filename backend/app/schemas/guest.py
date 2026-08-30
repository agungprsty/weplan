import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class GuestBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=50)
    category: Literal[
        "family", "friend", "vip", "general", "bridesmaid", "groomsman",
        "family_groom", "family_bride",
    ] = "general"
    side: Literal["bride", "groom", "both"] = "both"
    notes: str | None = None


class GuestCreate(GuestBase):
    pass


class GuestUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=50)
    category: Literal[
        "family", "friend", "vip", "general", "bridesmaid", "groomsman",
        "family_groom", "family_bride",
    ] | None = None
    rsvp_status: Literal["pending", "attending", "declined"] | None = None
    side: Literal["bride", "groom", "both"] | None = None
    notes: str | None = None


class GuestResponse(GuestBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    wedding_id: uuid.UUID
    rsvp_status: str
    gift_count: int = 0
    gift_total: int = 0
    created_at: datetime
    updated_at: datetime
