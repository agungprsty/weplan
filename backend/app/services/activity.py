from __future__ import annotations

import logging
import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import ActivityAction, EntityType
from app.models.activity import Activity
from app.models.user import User

logger = logging.getLogger(__name__)

# Re-export for callers & API validation (single source)
ALLOWED_ACTIONS = {a.value for a in ActivityAction}
ALLOWED_ENTITY_TYPES = {e.value for e in EntityType}


async def log_activity(
    db: AsyncSession,
    wedding_id: uuid.UUID,
    actor: User | None,
    action: ActivityAction | str,
    entity_type: EntityType | str,
    entity_id: uuid.UUID | None,
    title: str,
    meta: dict[str, Any] | None = None,
) -> Activity | None:
    """Create activity row reliably without breaking parent transaction.

    - Validates action/entity_type against enum (fail-open: log warning).
    - Truncates title to 255 chars.
    - Swallows DB errors so main operation tetap commit.
    """
    action_val = action.value if isinstance(action, ActivityAction) else str(action)
    entity_val = (
        entity_type.value if isinstance(entity_type, EntityType) else str(entity_type)
    )

    if action_val not in ALLOWED_ACTIONS:
        logger.warning(
            "log_activity: unknown action %r (entity=%s)", action_val, entity_val
        )
    if entity_val not in ALLOWED_ENTITY_TYPES:
        logger.warning(
            "log_activity: unknown entity_type %r (action=%s)", entity_val, action_val
        )

    try:
        activity = Activity(
            wedding_id=wedding_id,
            actor_user_id=actor.id if actor else None,
            action=action_val,  # type: ignore[arg-type]
            entity_type=entity_val,  # type: ignore[arg-type]
            entity_id=entity_id,
            title=(title[:255] if title else "-"),
            meta_data=meta,
        )
        db.add(activity)
        await db.flush()
        await db.refresh(activity)
        return activity
    except Exception:  # pragma: no cover
        logger.exception(
            "log_activity failed: wedding=%s action=%s entity=%s",
            wedding_id,
            action_val,
            entity_val,
        )
        await db.rollback()
        return None


async def list_activities(
    db: AsyncSession,
    wedding_id: uuid.UUID,
    limit: int = 20,
    offset: int = 0,
    entity_type: EntityType | str | None = None,
) -> tuple[list[Activity], int]:
    """List with pagination + tenant isolation.

    Single query untuk actor names (hindari N+1).
    """
    entity_val = (
        entity_type.value if isinstance(entity_type, EntityType) else entity_type
    )
    filters = [Activity.wedding_id == wedding_id]
    if entity_val:
        if entity_val not in ALLOWED_ENTITY_TYPES:
            return [], 0
        filters.append(Activity.entity_type == entity_val)

    total: int = (
        await db.execute(select(func.count()).select_from(Activity).where(*filters))
    ).scalar() or 0

    stmt = (
        select(Activity)
        .where(*filters)
        .order_by(Activity.created_at.desc(), Activity.id.desc())
        .limit(limit)
        .offset(offset)
    )
    activities = list((await db.execute(stmt)).scalars().all())

    if not activities:
        return activities, total

    user_ids = {a.actor_user_id for a in activities if a.actor_user_id}
    name_map: dict[uuid.UUID, str] = {}
    if user_ids:
        rows = (
            await db.execute(
                select(User.id, User.full_name).where(User.id.in_(user_ids))
            )
        ).all()
        name_map = {r[0]: r[1] for r in rows}

    for a in activities:
        object.__setattr__(
            a, "actor_name", name_map.get(a.actor_user_id) if a.actor_user_id else None
        )

    return activities, total
