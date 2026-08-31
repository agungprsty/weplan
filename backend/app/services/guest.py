from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.gift import Gift
from app.models.guest import Guest
from app.schemas.guest import GuestCreate, GuestUpdate
from app.services.activity import log_activity

if TYPE_CHECKING:
    from app.models.user import User


async def list_guests(db: AsyncSession, wedding_id: uuid.UUID) -> list[Guest]:
    """List guests with gift summary counts attached as transient attributes."""
    result = await db.execute(select(Guest).where(Guest.wedding_id == wedding_id))
    guests = list(result.scalars().all())
    agg = await db.execute(
        select(
            Gift.guest_id,
            func.count(Gift.id),
            func.coalesce(func.sum(Gift.amount), 0),
        )
        .where(Gift.wedding_id == wedding_id)
        .group_by(Gift.guest_id)
    )
    summaries = {
        row[0]: (row[1], int(row[2])) for row in agg.all() if row[0] is not None
    }
    for guest in guests:
        count, total = summaries.get(guest.id, (0, 0))
        guest.gift_count = count
        guest.gift_total = total
    return guests


async def create_guest(
    db: AsyncSession,
    wedding_id: uuid.UUID,
    data: GuestCreate,
    actor: User | None = None,
) -> Guest:
    guest = Guest(wedding_id=wedding_id, **data.model_dump())
    db.add(guest)
    await db.flush()
    await db.refresh(guest)
    await log_activity(
        db,
        wedding_id,
        actor,
        "created",
        "guest",
        guest.id,
        guest.name,
    )
    return guest


async def update_guest(
    db: AsyncSession,
    wedding_id: uuid.UUID,
    guest_id: uuid.UUID,
    data: GuestUpdate,
    actor: User | None = None,
) -> Guest | None:
    result = await db.execute(
        select(Guest).where(
            Guest.id == guest_id,
            Guest.wedding_id == wedding_id,
        )
    )
    guest = result.scalar_one_or_none()

    if guest is None:
        return None

    old_rsvp = guest.rsvp_status
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(guest, field, value)

    await db.flush()
    await db.refresh(guest)

    new_rsvp = guest.rsvp_status
    if "rsvp_status" in update_data and old_rsvp != new_rsvp:
        await log_activity(
            db,
            wedding_id,
            actor,
            "status_changed",
            "guest",
            guest.id,
            guest.name,
            meta={"field": "rsvp_status", "from": old_rsvp, "to": new_rsvp},
        )
    elif update_data:
        await log_activity(
            db,
            wedding_id,
            actor,
            "updated",
            "guest",
            guest.id,
            guest.name,
        )
    return guest


async def get_guest(
    db: AsyncSession, wedding_id: uuid.UUID, guest_id: uuid.UUID
) -> Guest | None:
    result = await db.execute(
        select(Guest).where(
            Guest.id == guest_id,
            Guest.wedding_id == wedding_id,
        )
    )
    return result.scalar_one_or_none()


async def delete_guest(
    db: AsyncSession,
    wedding_id: uuid.UUID,
    guest_id: uuid.UUID,
    actor: User | None = None,
) -> bool:
    guest = await get_guest(db, wedding_id, guest_id)
    if guest is None:
        return False
    name = guest.name
    await db.delete(guest)
    await db.flush()
    await log_activity(
        db,
        wedding_id,
        actor,
        "deleted",
        "guest",
        guest_id,
        name,
    )
    return True
