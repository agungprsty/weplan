from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate, TransactionUpdate
from app.services.activity import log_activity

if TYPE_CHECKING:
    from app.models.user import User


async def list_transactions(
    db: AsyncSession, wedding_id: uuid.UUID
) -> list[Transaction]:
    result = await db.execute(
        select(Transaction)
        .where(Transaction.wedding_id == wedding_id)
        .order_by(Transaction.transaction_date.desc(), Transaction.created_at.desc())
    )
    return list(result.scalars().all())


async def create_transaction(
    db: AsyncSession,
    wedding_id: uuid.UUID,
    data: TransactionCreate,
    actor: User | None = None,
) -> Transaction:
    txn = Transaction(wedding_id=wedding_id, **data.model_dump())
    db.add(txn)
    await db.flush()
    await db.refresh(txn)
    label = f"Transaksi {data.type} Rp {data.amount:,}"
    await log_activity(
        db,
        wedding_id,
        actor,
        "created",
        "transaction",
        txn.id,
        label,
    )
    return txn


async def get_transaction(
    db: AsyncSession, wedding_id: uuid.UUID, txn_id: uuid.UUID
) -> Transaction | None:
    result = await db.execute(
        select(Transaction).where(
            Transaction.id == txn_id, Transaction.wedding_id == wedding_id
        )
    )
    return result.scalar_one_or_none()


async def update_transaction(
    db: AsyncSession,
    wedding_id: uuid.UUID,
    txn_id: uuid.UUID,
    data: TransactionUpdate,
    actor: User | None = None,
) -> Transaction | None:
    txn = await get_transaction(db, wedding_id, txn_id)
    if txn is None:
        return None
    payload = data.model_dump(exclude_unset=True)
    if not payload:
        return txn
    for k, v in payload.items():
        setattr(txn, k, v)
    await db.flush()
    await db.refresh(txn)
    await log_activity(
        db,
        wedding_id,
        actor,
        "updated",
        "transaction",
        txn.id,
        f"Transaksi {txn.type} Rp {txn.amount:,}",
    )
    return txn


async def delete_transaction(
    db: AsyncSession,
    wedding_id: uuid.UUID,
    txn_id: uuid.UUID,
    actor: User | None = None,
) -> bool:
    txn = await get_transaction(db, wedding_id, txn_id)
    if txn is None:
        return False
    label = f"Transaksi {txn.type} Rp {txn.amount:,}"
    await db.delete(txn)
    await db.flush()
    await log_activity(
        db,
        wedding_id,
        actor,
        "deleted",
        "transaction",
        txn_id,
        label,
    )
    return True
