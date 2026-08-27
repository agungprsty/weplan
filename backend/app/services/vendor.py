import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.vendor import Vendor
from app.schemas.vendor import VendorCreate, VendorUpdate


async def list_vendors(db: AsyncSession, wedding_id: uuid.UUID) -> list[Vendor]:
    result = await db.execute(
        select(Vendor)
        .where(Vendor.wedding_id == wedding_id)
        .order_by(Vendor.created_at)
    )
    return list(result.scalars().all())


async def create_vendor(
    db: AsyncSession, wedding_id: uuid.UUID, data: VendorCreate
) -> Vendor:
    vendor = Vendor(wedding_id=wedding_id, **data.model_dump())
    db.add(vendor)
    await db.flush()
    await db.refresh(vendor)
    return vendor


async def update_vendor(
    db: AsyncSession, wedding_id: uuid.UUID, vendor_id: uuid.UUID, data: VendorUpdate
) -> Vendor | None:
    result = await db.execute(
        select(Vendor).where(Vendor.id == vendor_id, Vendor.wedding_id == wedding_id)
    )
    vendor = result.scalar_one_or_none()
    if vendor is None:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(vendor, field, value)
    await db.flush()
    await db.refresh(vendor)
    return vendor


async def get_vendor(
    db: AsyncSession, wedding_id: uuid.UUID, vendor_id: uuid.UUID
) -> Vendor | None:
    result = await db.execute(
        select(Vendor).where(Vendor.id == vendor_id, Vendor.wedding_id == wedding_id)
    )
    return result.scalar_one_or_none()


async def delete_vendor(
    db: AsyncSession, wedding_id: uuid.UUID, vendor_id: uuid.UUID
) -> bool:
    vendor = await get_vendor(db, wedding_id, vendor_id)
    if vendor is None:
        return False
    await db.delete(vendor)
    await db.flush()
    return True
