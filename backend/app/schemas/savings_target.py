import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class SavingsTargetBase(BaseModel):
    target_amount: int = Field(ge=0, default=0)
    deadline: date | None = None


class SavingsTargetUpdate(SavingsTargetBase):
    pass


class SavingsTargetResponse(SavingsTargetBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    wedding_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    # computed
    current_amount: int = 0
    total_masuk: int = 0
    total_keluar: int = 0
    progress_pct: float = 0.0
