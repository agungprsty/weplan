import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PlanBase(BaseModel):
    name: str
    slug: str
    price: int = 0
    max_guests: int = 50


class PlanResponse(PlanBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    is_active: bool
    created_at: datetime
