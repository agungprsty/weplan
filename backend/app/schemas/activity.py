from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import ActivityAction, EntityType


class ActivityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    wedding_id: uuid.UUID
    actor_user_id: uuid.UUID | None
    actor_name: str | None = None
    action: ActivityAction = Field(
        description="created | updated | deleted | status_changed"
    )
    entity_type: EntityType = Field(
        description="wedding | guest | gift | checklist ..."
    )
    entity_id: uuid.UUID | None
    title: str
    meta: dict[str, Any] | None = None
    created_at: datetime


class ActivityListResponse(BaseModel):
    data: list[ActivityResponse]
    meta: dict[str, int]
