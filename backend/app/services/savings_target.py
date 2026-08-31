from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.savings_target import SavingsTarget
from app.models.transaction import Transaction
from app.schemas.savings_target import SavingsTargetUpdate
from app.services.activity import log_activity

if TYPE_CHECKING:
    from app.models.user import User


async def get_savings_target(
    db: AsyncSession, wedding_id: uuid.UUID
) -> SavingsTarget | None:
    result = await db.execute(
        select(SavingsTarget).where(SavingsTarget.wedding_id == wedding_id)
    )
    return result.scalar_one_or_none()


async def upsert_savings_target(
    db: AsyncSession,
    wedding_id: uuid.UUID,
    data: SavingsTargetUpdate,
    actor: User | None = None,
) -> SavingsTarget:
    target = await get_savings_target(db, wedding_id)
    is_new = target is None
    if is_new:
        target = SavingsTarget(wedding_id=wedding_id, **data.model_dump())
        db.add(target)
        await db.flush()
        await db.refresh(target)
        await log_activity(
            db,
            wedding_id,
            actor,
            "created",
            "savings_target",
            target.id,
            "Target Dana",
        )
        return target
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(target, k, v)
    await db.flush()
    await db.refresh(target)
    await log_activity(
        db,
        wedding_id,
        actor,
        "updated",
        "savings_target",
        target.id,
        "Target Dana",
    )
    return target


async def compute_finance_stats(
    db: AsyncSession, wedding_id: uuid.UUID
) -> tuple[int, int, int]:
    """Returns total_masuk, total_keluar, current (masuk - keluar)"""
    masuk_result = await db.execute(
        select(func.coalesce(func.sum(Transaction.amount), 0)).where(
            Transaction.wedding_id == wedding_id, Transaction.type == "masuk"
        )
    )
    keluar_result = await db.execute(
        select(func.coalesce(func.sum(Transaction.amount), 0)).where(
            Transaction.wedding_id == wedding_id, Transaction.type == "keluar"
        )
    )
    total_masuk = masuk_result.scalar() or 0
    total_keluar = keluar_result.scalar() or 0
    current = total_masuk - total_keluar
    return int(total_masuk), int(total_keluar), int(current)
