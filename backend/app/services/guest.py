import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.guest import Guest
from app.schemas.guest import GuestCreate, GuestUpdate


async def list_guests(db: AsyncSession, wedding_id: uuid.UUID) -> list[Guest]:
    result = await db.execute(select(Guest).where(Guest.wedding_id == wedding_id))
    return list(result.scalars().all())


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
