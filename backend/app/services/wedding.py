import uuid
from typing import TYPE_CHECKING

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.models.wedding import Wedding
from app.models.wedding_user import WeddingUser
from app.schemas.wedding import WeddingCreate
from app.services.activity import log_activity

if TYPE_CHECKING:
    pass


async def _attach_member_count(
    db: AsyncSession, wedding: Wedding | None
) -> Wedding | None:
    """Best practice: centralize count logic in service, not API. Single place, type-safe via setattr."""  # noqa: E501
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


async def sync_savings_target(db: AsyncSession, wedding: Wedding) -> None:
    """Sinkronkan savings_targets.target_amount & deadline
    dari weddings.total_budget & wedding_date.
    Dipanggil saat create / update wedding agar keuangan otomatis
    mengikuti onboarding.
    """
    from app.models.savings_target import SavingsTarget

    result = await db.execute(
        select(SavingsTarget).where(SavingsTarget.wedding_id == wedding.id)
    )
    target = result.scalar_one_or_none()
    desired_amount = wedding.total_budget or 0
    desired_deadline = wedding.wedding_date
    if target is None:
        target = SavingsTarget(
            wedding_id=wedding.id,
            target_amount=desired_amount,
            deadline=desired_deadline,
        )
        db.add(target)
        await db.flush()
    else:
        changed = False
        if target.target_amount != desired_amount:
            target.target_amount = desired_amount
            changed = True
        if target.deadline != desired_deadline:
            target.deadline = desired_deadline
            changed = True
        if changed:
            await db.flush()


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
    await sync_savings_target(db, wedding)
    await db.flush()
    # reload dengan selectinload(plan) agar tidak MissingGreenlet saat serialisasi response (async lazy load)
    result = await db.execute(
        select(Wedding).options(selectinload(Wedding.plan)).where(Wedding.id == wedding.id)
    )
    wedding = result.scalar_one()
    wedding.member_count = 1
    await log_activity(
        db,
        wedding.id,
        user,
        "created",
        "wedding",
        wedding.id,
        wedding.title,
    )
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
    # reload dengan selectinload(plan) agar tidak MissingGreenlet saat serialisasi response
    result = await db.execute(
        select(Wedding).options(selectinload(Wedding.plan)).where(Wedding.id == wedding.id)
    )
    wedding = result.scalar_one()
    # After pairing, wedding has 2 partners
    wedding.member_count = 2
    await log_activity(
        db,
        wedding.id,
        user,
        "updated",
        "wedding",
        wedding.id,
        wedding.title,
        meta={"action": "pair_joined"},
    )
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
    result = await db.execute(
        select(Wedding).options(selectinload(Wedding.plan)).where(Wedding.id == wedding_id)
    )
    wedding = result.scalar_one_or_none()
    if wedding is not None:
        return await _attach_member_count(db, wedding)
    return None


async def update_wedding(
    db: AsyncSession, wedding: Wedding, data, actor: User | None = None
) -> Wedding:
    """Business logic for PATCH /weddings/{id}: apply updates, sync savings, reload, log."""

    # Normalize WeddingUpdate dict
    update_data = data.model_dump(exclude_unset=True) if hasattr(data, "model_dump") else dict(data)

    for field, value in update_data.items():
        setattr(wedding, field, value)
    await db.flush()

    if "total_budget" in update_data or "wedding_date" in update_data:
        await sync_savings_target(db, wedding)

    # Reload with plan to avoid MissingGreenlet
    result = await db.execute(
        select(Wedding).options(selectinload(Wedding.plan)).where(Wedding.id == wedding.id)
    )
    wedding = result.scalar_one()
    wedding = await _attach_member_count(db, wedding)  # type: ignore[assignment]
    assert wedding is not None

    if update_data and actor is not None:
        await log_activity(
            db,
            wedding.id,
            actor,
            "updated",
            "wedding",
            wedding.id,
            wedding.title,
        )
    return wedding
