import uuid
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class TransactionBase(BaseModel):
    type: Literal["masuk", "keluar"]
    amount: int = Field(ge=1)
    category: str = Field(default="lainnya", max_length=50)
    source: str | None = Field(default=None, max_length=255)
    proof_url: str | None = Field(default=None, max_length=500)
    transaction_date: date | None = None
    notes: str | None = None


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    type: Literal["masuk", "keluar"] | None = None
    amount: int | None = Field(default=None, ge=1)
    category: str | None = Field(default=None, max_length=50)
    source: str | None = Field(default=None, max_length=255)
    proof_url: str | None = Field(default=None, max_length=500)
    transaction_date: date | None = None
    notes: str | None = None


class TransactionResponse(TransactionBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    wedding_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class PaginatedTransactionResponse(BaseModel):
    data: list[TransactionResponse]
    meta: dict
