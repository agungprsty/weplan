import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.wedding import Wedding
from app.models.wedding_user import WeddingUser
from app.schemas.wedding import WeddingCreate


async def create_wedding(db: AsyncSession, data: WeddingCreate, user: User) -> Wedding:
    from app.services.auth import generate_pair_code

    wedding = Wedding(
        title=data.title,
        wedding_date=data.wedding_date,
        partner1_name=data.partner1_name,
        partner2_name=data.partner2_name,
        total_budget=data.total_budget,
        pair_code=generate_pair_code(),
    )
    db.add(wedding)
    await db.flush()

    wedding_user = WeddingUser(
        wedding_id=wedding.id,
        user_id=user.id,
        role="partner",
    )
    db.add(wedding_user)
    await db.flush()
    await db.refresh(wedding)
    return wedding


async def pair_wedding(db: AsyncSession, pair_code: str, user: User) -> Wedding:
    result = await db.execute(select(Wedding).where(Wedding.pair_code == pair_code))
    wedding = result.scalar_one_or_none()

    if wedding is None:
        raise ValueError("Invalid pair code")

    existing = await db.execute(
        select(WeddingUser).where(
            WeddingUser.wedding_id == wedding.id,
            WeddingUser.user_id == user.id,
        )
    )
    if existing.scalar_one_or_none() is not None:
        raise ValueError("Already paired to this wedding")

    partner_count = await db.execute(
        select(WeddingUser).where(
            WeddingUser.wedding_id == wedding.id,
            WeddingUser.role == "partner",
        )
    )
    if partner_count.scalar_one_or_none() is not None:
        raise ValueError("Wedding already has two partners")

    wedding_user = WeddingUser(
        wedding_id=wedding.id,
        user_id=user.id,
        role="partner",
    )
    db.add(wedding_user)
    await db.flush()
    await db.refresh(wedding)
    return wedding


async def get_user_wedding(db: AsyncSession, user: User) -> Wedding | None:
    result = await db.execute(
        select(Wedding).join(WeddingUser).where(WeddingUser.user_id == user.id).limit(1)
    )
    return result.scalar_one_or_none()


async def get_wedding_by_id(db: AsyncSession, wedding_id: uuid.UUID) -> Wedding | None:
    return await db.get(Wedding, wedding_id)
