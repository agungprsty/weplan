import uuid

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.mahar_item import MaharItem
from app.schemas.mahar_item import MaharItemCreate, MaharItemUpdate


def _ensure_selesai_has_actual_cost(
    item_status: str | None, actual_cost: int | None
) -> None:
    if item_status == "selesai" and actual_cost is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "VALIDATION_ERROR",
                "message": "Biaya aktual wajib diisi untuk tandai selesai",
                "errors": [
                    {
                        "field": "actual_cost",
                        "message": "Wajib diisi saat status selesai",
                    }
                ],
            },
        )


async def list_mahar_items(db: AsyncSession, wedding_id: uuid.UUID) -> list[MaharItem]:
    result = await db.execute(
        select(MaharItem)
        .where(MaharItem.wedding_id == wedding_id)
        .order_by(MaharItem.created_at)
    )
    return list(result.scalars().all())


async def count_mahar_items(db: AsyncSession, wedding_id: uuid.UUID) -> int:
    result = await db.execute(
        select(func.count())
        .select_from(MaharItem)
        .where(MaharItem.wedding_id == wedding_id)
    )
    return result.scalar() or 0


async def create_mahar_item(
    db: AsyncSession, wedding_id: uuid.UUID, data: MaharItemCreate
) -> MaharItem:
    _ensure_selesai_has_actual_cost(data.status, data.actual_cost)
    item = MaharItem(wedding_id=wedding_id, **data.model_dump())
    db.add(item)
    await db.flush()
    await db.refresh(item)
    return item


async def update_mahar_item(
    db: AsyncSession, wedding_id: uuid.UUID, item_id: uuid.UUID, data: MaharItemUpdate
) -> MaharItem | None:
    result = await db.execute(
        select(MaharItem).where(
            MaharItem.id == item_id, MaharItem.wedding_id == wedding_id
        )
    )
    item = result.scalar_one_or_none()
    if item is None:
        return None
    payload = data.model_dump(exclude_unset=True)
    merged_status: str = payload.get("status", item.status)  # type: ignore[assignment]
    # actual_cost: None = explicit null, missing = keep existing
    if "actual_cost" in payload:
        merged_actual: int | None = payload["actual_cost"]  # type: ignore[assignment]
    else:
        merged_actual = item.actual_cost
    _ensure_selesai_has_actual_cost(merged_status, merged_actual)
    for field, value in payload.items():
        setattr(item, field, value)
    await db.flush()
    await db.refresh(item)
    return item


async def get_mahar_item(
    db: AsyncSession, wedding_id: uuid.UUID, item_id: uuid.UUID
) -> MaharItem | None:
    result = await db.execute(
        select(MaharItem).where(
            MaharItem.id == item_id, MaharItem.wedding_id == wedding_id
        )
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
