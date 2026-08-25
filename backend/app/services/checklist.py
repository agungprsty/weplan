import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.checklist import Checklist
from app.schemas.checklist import ChecklistCreate, ChecklistUpdate


async def list_checklists(db: AsyncSession, wedding_id: uuid.UUID) -> list[Checklist]:
    result = await db.execute(
        select(Checklist)
        .where(Checklist.wedding_id == wedding_id)
        .order_by(Checklist.order, Checklist.created_at)
    )
    return list(result.scalars().all())


async def create_checklist(
    db: AsyncSession, wedding_id: uuid.UUID, data: ChecklistCreate
) -> Checklist:
    max_order_result = await db.execute(
        select(Checklist.order)
        .where(Checklist.wedding_id == wedding_id)
        .order_by(Checklist.order.desc())
        .limit(1)
    )
    max_order = max_order_result.scalar_one_or_none() or 0

    checklist = Checklist(
        wedding_id=wedding_id,
        order=max_order + 1,
        **data.model_dump(),
    )
    db.add(checklist)
    await db.flush()
    await db.refresh(checklist)
    return checklist


async def update_checklist(
    db: AsyncSession,
    wedding_id: uuid.UUID,
    checklist_id: uuid.UUID,
    data: ChecklistUpdate,
) -> Checklist | None:
    result = await db.execute(
        select(Checklist).where(
            Checklist.id == checklist_id,
            Checklist.wedding_id == wedding_id,
        )
    )
    checklist = result.scalar_one_or_none()

    if checklist is None:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(checklist, field, value)

    await db.flush()
    await db.refresh(checklist)
    return checklist


async def get_checklist(
    db: AsyncSession, wedding_id: uuid.UUID, checklist_id: uuid.UUID
) -> Checklist | None:
    result = await db.execute(
        select(Checklist).where(
            Checklist.id == checklist_id,
            Checklist.wedding_id == wedding_id,
        )
    )
    return result.scalar_one_or_none()
