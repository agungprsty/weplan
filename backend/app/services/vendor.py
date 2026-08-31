from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.vendor import Vendor
from app.schemas.vendor import VendorCreate, VendorUpdate
from app.services.activity import log_activity

if TYPE_CHECKING:
    from app.models.user import User


async def list_vendors(db: AsyncSession, wedding_id: uuid.UUID) -> list[Vendor]:
    result = await db.execute(
        select(Vendor)
        .where(Vendor.wedding_id == wedding_id)
        .order_by(Vendor.created_at)
    )
    return list(result.scalars().all())


async def create_vendor(
    db: AsyncSession,
    wedding_id: uuid.UUID,
    data: VendorCreate,
    actor: User | None = None,
) -> Vendor:
    vendor = Vendor(wedding_id=wedding_id, **data.model_dump())
    db.add(vendor)
    await db.flush()
    await db.refresh(vendor)
    await log_activity(
        db,
        wedding_id,
        actor,
        "created",
        "vendor",
        vendor.id,
        vendor.vendor_name,
    )
    return vendor


async def update_vendor(
    db: AsyncSession,
    wedding_id: uuid.UUID,
    vendor_id: uuid.UUID,
    data: VendorUpdate,
    actor: User | None = None,
) -> Vendor | None:
    result = await db.execute(
        select(Vendor).where(Vendor.id == vendor_id, Vendor.wedding_id == wedding_id)
    )
    vendor = result.scalar_one_or_none()
    if vendor is None:
        return None

    old_status = vendor.status
    payload = data.model_dump(exclude_unset=True)
    for field, value in payload.items():
        setattr(vendor, field, value)
    await db.flush()
    await db.refresh(vendor)

    new_status = vendor.status
    if "status" in payload and old_status != new_status:
        await log_activity(
            db,
            wedding_id,
            actor,
            "status_changed",
            "vendor",
            vendor.id,
            vendor.vendor_name,
            meta={"from": old_status, "to": new_status},
        )
    elif payload:
        await log_activity(
            db,
            wedding_id,
            actor,
            "updated",
            "vendor",
            vendor.id,
            vendor.vendor_name,
        )
    return vendor


async def get_vendor(
    db: AsyncSession, wedding_id: uuid.UUID, vendor_id: uuid.UUID
) -> Vendor | None:
    result = await db.execute(
        select(Vendor).where(Vendor.id == vendor_id, Vendor.wedding_id == wedding_id)
    )
    return result.scalar_one_or_none()


async def delete_vendor(
    db: AsyncSession,
    wedding_id: uuid.UUID,
    vendor_id: uuid.UUID,
    actor: User | None = None,
) -> bool:
    vendor = await get_vendor(db, wedding_id, vendor_id)
    if vendor is None:
        return False
    name = vendor.vendor_name
    await db.delete(vendor)
    await db.flush()
    await log_activity(
        db,
        wedding_id,
        actor,
        "deleted",
        "vendor",
        vendor_id,
        name,
    )
    return True
