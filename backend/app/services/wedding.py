import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.models.wedding import Wedding
from app.models.wedding_user import WeddingUser
from app.schemas.wedding import WeddingCreate


async def _attach_member_count(
    db: AsyncSession, wedding: Wedding | None
) -> Wedding | None:
    """Best practice: centralize count logic in service, not API. Single place, type-safe via setattr."""
    if wedding is None:
        return None
    cnt = await db.scalar(
        select(func.count())
        .select_from(WeddingUser)
        .where(WeddingUser.wedding_id == wedding.id)
    )
    # Attach transient attribute for Pydantic serialization (no DB column)
    wedding.member_count = int(cnt or 0)
    return wedding


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
    # New wedding always has 1 partner, no extra query needed
    wedding.member_count = 1
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

    partner_count = await db.scalar(
        select(func.count())
        .select_from(WeddingUser)
        .where(
            WeddingUser.wedding_id == wedding.id,
            WeddingUser.role == "partner",
        )
    )
    if partner_count and partner_count >= 2:
        raise ValueError("Wedding already has two partners")

    wedding_user = WeddingUser(
        wedding_id=wedding.id,
        user_id=user.id,
        role="partner",
    )
    db.add(wedding_user)
    await db.flush()
    await db.refresh(wedding)
    # After pairing, wedding has 2 partners
    wedding.member_count = 2
    return wedding


async def get_user_wedding(db: AsyncSession, user: User) -> Wedding | None:
    result = await db.execute(
        select(Wedding)
        .options(selectinload(Wedding.plan))
        .join(WeddingUser)
        .where(WeddingUser.user_id == user.id)
        .limit(1)
    )
    wedding = result.scalar_one_or_none()
    return await _attach_member_count(db, wedding)


async def get_wedding_by_id(db: AsyncSession, wedding_id: uuid.UUID) -> Wedding | None:
    wedding = await db.get(Wedding, wedding_id)
    # Lazy attach if needed
    if wedding is not None and not hasattr(wedding, "member_count"):
        wedding.member_count = 0
    return wedding
