import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class OrderCreate(BaseModel):
    plan_id: uuid.UUID
    payment_method: str | None = Field(default=None, max_length=50)
    proof_url: str | None = Field(default=None, max_length=500)
    notes: str | None = None


class OrderConfirm(BaseModel):
    payment_method: str = Field(max_length=50)
    notes: str | None = None


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    wedding_id: uuid.UUID
    plan_id: uuid.UUID
    status: Literal["pending", "confirmed", "cancelled"]
    amount: int
    payment_method: str | None
    proof_url: str | None
    notes: str | None
    confirmed_by: uuid.UUID | None
    confirmed_at: datetime | None
    created_at: datetime
    updated_at: datetime
