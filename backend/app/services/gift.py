import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.gift import Gift
from app.models.guest import Guest
from app.schemas.gift import GiftCreate, GiftUpdate


def _to_dict(gift: Gift, guest_name: str | None) -> dict:
    return {
        "id": gift.id,
        "wedding_id": gift.wedding_id,
        "guest_id": gift.guest_id,
        "guest_name": guest_name,
        "type": gift.type,
        "description": gift.description,
        "amount": gift.amount,
        "received_at": gift.received_at,
        "created_at": gift.created_at,
        "updated_at": gift.updated_at,
    }


async def _guest_name(db: AsyncSession, guest_id: uuid.UUID | None) -> str | None:
    if guest_id is None:
        return None
    res = await db.execute(select(Guest.name).where(Guest.id == guest_id))
    return res.scalar_one_or_none()


async def list_gifts(db: AsyncSession, wedding_id: uuid.UUID) -> list[dict]:
    res = await db.execute(
        select(Gift)
        .where(Gift.wedding_id == wedding_id)
        .order_by(Gift.received_at.desc().nulls_last(), Gift.created_at.desc())
    )
    gifts = list(res.scalars().all())
    ids = [g.guest_id for g in gifts if g.guest_id is not None]
    names: dict[uuid.UUID, str] = {}
    if ids:
        nres = await db.execute(
            select(Guest.id, Guest.name).where(Guest.id.in_(ids))
        )
        names = {row[0]: row[1] for row in nres.all()}
    return [_to_dict(g, names.get(g.guest_id)) for g in gifts]


async def create_gift(
    db: AsyncSession, wedding_id: uuid.UUID, data: GiftCreate
) -> dict:
    gift = Gift(wedding_id=wedding_id, **data.model_dump())
    db.add(gift)
    await db.flush()
    await db.refresh(gift)
    return _to_dict(gift, await _guest_name(db, gift.guest_id))


async def get_gift(
    db: AsyncSession, wedding_id: uuid.UUID, gift_id: uuid.UUID
) -> dict | None:
    res = await db.execute(
        select(Gift).where(Gift.id == gift_id, Gift.wedding_id == wedding_id)
    )
    gift = res.scalar_one_or_none()
    if gift is None:
        return None
    return _to_dict(gift, await _guest_name(db, gift.guest_id))


async def update_gift(
    db: AsyncSession,
    wedding_id: uuid.UUID,
    gift_id: uuid.UUID,
    data: GiftUpdate,
) -> dict | None:
    res = await db.execute(
        select(Gift).where(Gift.id == gift_id, Gift.wedding_id == wedding_id)
    )
    gift = res.scalar_one_or_none()
    if gift is None:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(gift, field, value)
    await db.flush()
    await db.refresh(gift)
    return _to_dict(gift, await _guest_name(db, gift.guest_id))


async def delete_gift(
    db: AsyncSession, wedding_id: uuid.UUID, gift_id: uuid.UUID
) -> bool:
    gift = await get_gift(db, wedding_id, gift_id)
    if gift is None:
        return False
    res = await db.execute(
        select(Gift).where(Gift.id == gift_id, Gift.wedding_id == wedding_id)
    )
    await db.delete(res.scalar_one())
    return True
