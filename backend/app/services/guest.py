import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.gift import Gift
from app.models.guest import Guest
from app.schemas.guest import GuestCreate, GuestUpdate


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
    db: AsyncSession, wedding_id: uuid.UUID, data: GuestCreate
) -> Guest:
    guest = Guest(wedding_id=wedding_id, **data.model_dump())
    db.add(guest)
    await db.flush()
    await db.refresh(guest)
    return guest


async def update_guest(
    db: AsyncSession, wedding_id: uuid.UUID, guest_id: uuid.UUID, data: GuestUpdate
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

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(guest, field, value)

    await db.flush()
    await db.refresh(guest)
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
