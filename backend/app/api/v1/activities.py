from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, get_current_wedding
from app.core.enums import EntityType
from app.models.user import User
from app.models.wedding import Wedding
from app.schemas.activity import ActivityListResponse, ActivityResponse
from app.services import activity as activity_service

router = APIRouter()


@router.get("/", response_model=ActivityListResponse)
async def list_activities(
    wedding_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    wedding: Annotated[Wedding, Depends(get_current_wedding)],
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=50, description="Page size")] = 20,
    offset: Annotated[int, Query(ge=0, description="Pagination offset")] = 0,
    entity_type: Annotated[EntityType | None, Query(description="Filter")] = None,
) -> dict:
    """List activities — tenant-isolated via wedding_id + get_current_wedding."""
    activities, total = await activity_service.list_activities(
        db, wedding_id, limit=limit, offset=offset, entity_type=entity_type
    )
    data = [
        ActivityResponse(
            id=a.id,
            wedding_id=a.wedding_id,
            actor_user_id=a.actor_user_id,
            actor_name=getattr(a, "actor_name", None),
            action=a.action,
            entity_type=a.entity_type,
            entity_id=a.entity_id,
            title=a.title,
            meta=a.meta_data,
            created_at=a.created_at,
        )
        for a in activities
    ]
    return {"data": data, "meta": {"total": total}}
