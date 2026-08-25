import uuid
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ChecklistBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    category: Literal[
        "seserahan",
        "kua",
        "vendor",
        "dekorasi",
        "undangan",
        "catering",
        "busana",
        "dokumentasi",
        "hiburan",
        "lainnya",
    ]
    due_date: date | None = None


class ChecklistCreate(ChecklistBase):
    assignee_id: uuid.UUID | None = None


class ChecklistUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    category: (
        Literal[
            "seserahan",
            "kua",
            "vendor",
            "dekorasi",
            "undangan",
            "catering",
            "busana",
            "dokumentasi",
            "hiburan",
            "lainnya",
        ]
        | None
    ) = None
    status: Literal["todo", "in_progress", "done"] | None = None
    assignee_id: uuid.UUID | None = None
    due_date: date | None = None
    order: int | None = None


class ChecklistResponse(ChecklistBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    wedding_id: uuid.UUID
    assignee_id: uuid.UUID | None
    status: str
    order: int
    created_at: datetime
    updated_at: datetime
