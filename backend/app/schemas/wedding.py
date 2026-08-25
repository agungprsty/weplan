import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class WeddingBase(BaseModel):
    title: str
    wedding_date: date | None = None
    partner1_name: str
    partner2_name: str
    total_budget: int | None = None


class WeddingCreate(WeddingBase):
    pass


class WeddingUpdate(BaseModel):
    title: str | None = None
    wedding_date: date | None = None
    partner1_name: str | None = None
    partner2_name: str | None = None
    total_budget: int | None = None


class WeddingResponse(WeddingBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    pair_code: str
    created_at: datetime
    updated_at: datetime


class WeddingPairRequest(BaseModel):
    pair_code: str


class WeddingWithPartners(WeddingResponse):
    partner1_email: str | None = None
    partner2_email: str | None = None
