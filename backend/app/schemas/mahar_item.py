import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class MaharItemBase(BaseModel):
    type: Literal["mahar", "seserahan_cpp", "seserahan_cpw", "hantaran"] = "mahar"
    title: str = Field(min_length=1, max_length=255)
    qty: int = Field(default=1, ge=1)
    estimated_cost: int | None = Field(default=None, ge=0)
    actual_cost: int | None = Field(default=None, ge=0)
    status: Literal["rencana", "dibeli", "dicicil", "selesai"] = "rencana"
    tenor_total: int | None = Field(default=None, ge=1)
    tenor_paid: int = Field(default=0, ge=0)
    notes: str | None = None


class MaharItemCreate(MaharItemBase):
    pass


class MaharItemUpdate(BaseModel):
    type: Literal["mahar", "seserahan_cpp", "seserahan_cpw", "hantaran"] | None = None
    title: str | None = Field(default=None, min_length=1, max_length=255)
    qty: int | None = Field(default=None, ge=1)
    estimated_cost: int | None = Field(default=None, ge=0)
    actual_cost: int | None = Field(default=None, ge=0)
    status: Literal["rencana", "dibeli", "dicicil", "selesai"] | None = None
    tenor_total: int | None = Field(default=None, ge=1)
    tenor_paid: int | None = Field(default=None, ge=0)
    notes: str | None = None


class MaharItemResponse(MaharItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    wedding_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
