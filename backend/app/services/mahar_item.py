import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.mahar_item import MaharItem
from app.schemas.mahar_item import MaharItemCreate, MaharItemUpdate


async def list_mahar_items(db: AsyncSession, wedding_id: uuid.UUID) -> list[MaharItem]:
    result = await db.execute(
        select(MaharItem).where(MaharItem.wedding_id == wedding_id).order_by(MaharItem.created_at)
    )
    return list(result.scalars().all())


async def count_mahar_items(db: AsyncSession, wedding_id: uuid.UUID) -> int:
    result = await db.execute(select(func.count()).select_from(MaharItem).where(MaharItem.wedding_id == wedding_id))
    return result.scalar() or 0


async def create_mahar_item(
    db: AsyncSession, wedding_id: uuid.UUID, data: MaharItemCreate
) -> MaharItem:
    item = MaharItem(wedding_id=wedding_id, **data.model_dump())
    db.add(item)
    await db.flush()
    await db.refresh(item)
    return item


async def update_mahar_item(
    db: AsyncSession, wedding_id: uuid.UUID, item_id: uuid.UUID, data: MaharItemUpdate
) -> MaharItem | None:
    result = await db.execute(
        select(MaharItem).where(MaharItem.id == item_id, MaharItem.wedding_id == wedding_id)
    )
    item = result.scalar_one_or_none()
    if item is None:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    await db.flush()
    await db.refresh(item)
    return item


async def get_mahar_item(
    db: AsyncSession, wedding_id: uuid.UUID, item_id: uuid.UUID
) -> MaharItem | None:
    result = await db.execute(
        select(MaharItem).where(MaharItem.id == item_id, MaharItem.wedding_id == wedding_id)
    )
    return result.scalar_one_or_none()


async def delete_mahar_item(
    db: AsyncSession, wedding_id: uuid.UUID, item_id: uuid.UUID
) -> bool:
    item = await get_mahar_item(db, wedding_id, item_id)
    if item is None:
        return False
    await db.delete(item)
    await db.flush()
    return True
