import uuid
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class GiftBase(BaseModel):
    guest_id: uuid.UUID | None = None
    type: Literal["kado", "uang", "other"] = "kado"
    description: str | None = Field(default=None, max_length=255)
    amount: int | None = Field(default=None, ge=0)
    received_at: date | None = None


class GiftCreate(GiftBase):
    guest_id: uuid.UUID


class GiftUpdate(BaseModel):
    guest_id: uuid.UUID | None = None
    type: Literal["kado", "uang", "other"] | None = None
    description: str | None = Field(default=None, max_length=255)
    amount: int | None = Field(default=None, ge=0)
    received_at: date | None = None


class GiftResponse(GiftBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    wedding_id: uuid.UUID
    guest_name: str | None = None
    created_at: datetime
    updated_at: datetime
