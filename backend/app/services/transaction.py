import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate, TransactionUpdate


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
    db: AsyncSession, wedding_id: uuid.UUID, data: TransactionCreate
) -> Transaction:
    txn = Transaction(wedding_id=wedding_id, **data.model_dump())
    db.add(txn)
    await db.flush()
    await db.refresh(txn)
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
    db: AsyncSession, wedding_id: uuid.UUID, txn_id: uuid.UUID, data: TransactionUpdate
) -> Transaction | None:
    txn = await get_transaction(db, wedding_id, txn_id)
    if txn is None:
        return None
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(txn, k, v)
    await db.flush()
    await db.refresh(txn)
    return txn


async def delete_transaction(
    db: AsyncSession, wedding_id: uuid.UUID, txn_id: uuid.UUID
) -> bool:
    txn = await get_transaction(db, wedding_id, txn_id)
    if txn is None:
        return False
    await db.delete(txn)
    await db.flush()
    return True
