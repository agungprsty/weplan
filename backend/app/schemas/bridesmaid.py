import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class BridesmaidBase(BaseModel):
    uniform_size: str | None = Field(default=None, max_length=20)
    fitting_status: Literal["pending", "fitting", "done"] = "pending"
    payment_status: Literal["belum_bayar", "dp", "lunas"] = "belum_bayar"
    price: int = Field(default=0, ge=0)
    notes: str | None = None


class BridesmaidUpdate(BaseModel):
    uniform_size: str | None = Field(default=None, max_length=20)
    fitting_status: Literal["pending", "fitting", "done"] | None = None
    payment_status: Literal["belum_bayar", "dp", "lunas"] | None = None
    price: int | None = Field(default=None, ge=0)
    notes: str | None = None


class BridesmaidResponse(BridesmaidBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    wedding_id: uuid.UUID
    guest_id: uuid.UUID
    guest_name: str
    guest_phone: str | None = None
    guest_side: str | None = None
    created_at: datetime
    updated_at: datetime
