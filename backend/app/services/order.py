import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order
from app.schemas.order import OrderCreate


async def create_order(
    db: AsyncSession, wedding_id: uuid.UUID, data: OrderCreate, amount: int
) -> Order:
    order = Order(
        wedding_id=wedding_id,
        plan_id=data.plan_id,
        amount=amount,
        payment_method=data.payment_method,
        proof_url=data.proof_url,
        notes=data.notes,
        status="pending",
    )
    db.add(order)
    await db.flush()
    await db.refresh(order)
    return order


async def list_orders(db: AsyncSession, wedding_id: uuid.UUID) -> list[Order]:
    result = await db.execute(
        select(Order)
        .where(Order.wedding_id == wedding_id)
        .order_by(Order.created_at.desc())
    )
    return list(result.scalars().all())


async def get_order(
    db: AsyncSession, wedding_id: uuid.UUID, order_id: uuid.UUID
) -> Order | None:
    result = await db.execute(
        select(Order).where(
            Order.id == order_id,
            Order.wedding_id == wedding_id,
        )
    )
    return result.scalar_one_or_none()


async def confirm_order(
    db: AsyncSession,
    order_id: uuid.UUID,
    admin_id: uuid.UUID,
    payment_method: str,
    notes: str | None = None,
) -> Order | None:
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if order is None:
        return None

    order.status = "confirmed"
    order.confirmed_by = admin_id
    order.confirmed_at = datetime.now(UTC)
    order.payment_method = payment_method
    if notes:
        order.notes = notes

    await db.flush()
    await db.refresh(order)
    return order


async def get_pending_order_for_wedding(
    db: AsyncSession, wedding_id: uuid.UUID
) -> Order | None:
    result = await db.execute(
        select(Order).where(
            Order.wedding_id == wedding_id,
            Order.status == "pending",
        )
    )
    return result.scalar_one_or_none()
