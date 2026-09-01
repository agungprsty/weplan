from __future__ import annotations

import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cortage import CortageItem
from app.models.guest import Guest
from app.models.transaction import Transaction
from app.schemas.cortage import CortageUpdate
from app.services.activity import log_activity

if TYPE_CHECKING:
    from app.models.user import User


_ROLE_LABELS: dict[str, str] = {
    "groomsman": "Groomsman",
    "family_groom": "Keluarga Mempelai Pria",
    "family_bride": "Keluarga Mempelai Wanita",
    "bridesmaid": "Bridesmaid",
}


def _role_label(category: str | None) -> str:
    return _ROLE_LABELS.get(category or "", "Bridesmaid")


async def list_cortage(db: AsyncSession, wedding_id: uuid.UUID) -> list[dict]:
    # ensure every guest bridesmaid/groomsman has a detail row
    guests_res = await db.execute(
        select(Guest).where(
            Guest.wedding_id == wedding_id,
            Guest.category.in_(
                ["bridesmaid", "groomsman", "family_groom", "family_bride"]
            ),
        )
    )
    guests = list(guests_res.scalars().all())

    # fetch existing details
    details_res = await db.execute(
        select(CortageItem).where(CortageItem.wedding_id == wedding_id)
    )
    details_by_guest = {d.guest_id: d for d in details_res.scalars().all()}

    result: list[CortageItem] = []
    for g in guests:
        d = details_by_guest.get(g.id)
        if d is None:
            d = CortageItem(wedding_id=wedding_id, guest_id=g.id)
            db.add(d)
            await db.flush()
            await db.refresh(d)
            details_by_guest[g.id] = d
        result.append(d)

    # urutan terbaru (desc) — terbaru di atas
    result.sort(key=lambda x: x.created_at, reverse=True)

    # build response dicts with guest info
    guest_map = {g.id: g for g in guests}
    out: list[dict] = []
    for d in result:
        g = guest_map[d.guest_id]
        out.append(
            {
                "id": d.id,
                "wedding_id": d.wedding_id,
                "guest_id": d.guest_id,
                "guest_name": g.name,
                "guest_phone": g.phone,
                "guest_side": g.side,
                "guest_category": g.category,
                "uniform_size": d.uniform_size,
                "fitting_status": d.fitting_status,
                "payment_status": d.payment_status,
                "price": d.price,
                "notes": d.notes,
                "created_at": d.created_at,
                "updated_at": d.updated_at,
            }
        )
    return out


async def update_cortage(
    db: AsyncSession,
    wedding_id: uuid.UUID,
    cortage_id: uuid.UUID,
    data: CortageUpdate,
    actor: User | None = None,
) -> dict | None:
    res = await db.execute(
        select(CortageItem).where(
            CortageItem.id == cortage_id, CortageItem.wedding_id == wedding_id
        )
    )
    item = res.scalar_one_or_none()
    if item is None:
        return None
    old_payment = item.payment_status
    old_fitting = item.fitting_status

    payload = data.model_dump(exclude_unset=True)
    for field, value in payload.items():
        setattr(item, field, value)
    await db.flush()
    await db.refresh(item)

    g_res = await db.execute(select(Guest).where(Guest.id == item.guest_id))
    g = g_res.scalar_one_or_none()
    guest_name = g.name if g else ""
    guest_category = g.category if g else None

    # activity: log each status field independently (fix elif bug — previously fitting change ignored when both changed)  # noqa: E501
    title = f"{_role_label(guest_category)} - {guest_name}"
    status_logged = False
    if "payment_status" in payload and old_payment != item.payment_status:
        await log_activity(
            db,
            wedding_id,
            actor,
            "status_changed",
            "cortage",
            item.id,
            title,
            meta={
                "field": "payment_status",
                "from": old_payment,
                "to": item.payment_status,
            },
        )
        status_logged = True
    if "fitting_status" in payload and old_fitting != item.fitting_status:
        await log_activity(
            db,
            wedding_id,
            actor,
            "status_changed",
            "cortage",
            item.id,
            title,
            meta={
                "field": "fitting_status",
                "from": old_fitting,
                "to": item.fitting_status,
            },
        )
        status_logged = True
    if payload and not status_logged:
        await log_activity(
            db,
            wedding_id,
            actor,
            "updated",
            "cortage",
            item.id,
            title,
        )

    is_payment_done = item.payment_status == "lunas" and old_payment != "lunas"
    is_fitting_done = item.fitting_status == "done" and old_fitting != "done"
    should_expense = (
        (is_payment_done or is_fitting_done) and item.price and item.price > 0
    )
    if should_expense:
        source = f"{_role_label(guest_category)} - {guest_name}"
        existing_res = await db.execute(
            select(Transaction).where(
                Transaction.wedding_id == wedding_id,
                Transaction.source == source,
                Transaction.category == "busana",
                Transaction.type == "keluar",
            )
        )
        exists = existing_res.scalars().first()
        if not exists:
            tx = Transaction(
                wedding_id=wedding_id,
                type="keluar",
                amount=item.price,
                category="busana",
                source=source,
                transaction_date=date.today(),
                notes=(
                    f"Seragam {item.uniform_size or '-'} · "
                    f"fitting {item.fitting_status}"
                ),
            )
            db.add(tx)
            await db.flush()

    return {
        "id": item.id,
        "wedding_id": item.wedding_id,
        "guest_id": item.guest_id,
        "guest_name": guest_name,
        "guest_phone": g.phone if g else None,
        "guest_side": g.side if g else None,
        "guest_category": guest_category,
        "uniform_size": item.uniform_size,
        "fitting_status": item.fitting_status,
        "payment_status": item.payment_status,
        "price": item.price,
        "notes": item.notes,
        "created_at": item.created_at,
        "updated_at": item.updated_at,
    }


async def get_cortage(
    db: AsyncSession, wedding_id: uuid.UUID, cortage_id: uuid.UUID
) -> dict | None:
    res = await db.execute(
        select(CortageItem).where(
            CortageItem.id == cortage_id, CortageItem.wedding_id == wedding_id
        )
    )
    item = res.scalar_one_or_none()
    if item is None:
        return None
    g_res = await db.execute(select(Guest).where(Guest.id == item.guest_id))
    g = g_res.scalar_one_or_none()
    return {
        "id": item.id,
        "wedding_id": item.wedding_id,
        "guest_id": item.guest_id,
        "guest_name": g.name if g else "",
        "guest_phone": g.phone if g else None,
        "guest_side": g.side if g else None,
        "guest_category": g.category if g else None,
        "uniform_size": item.uniform_size,
        "fitting_status": item.fitting_status,
        "payment_status": item.payment_status,
        "price": item.price,
        "notes": item.notes,
        "created_at": item.created_at,
        "updated_at": item.updated_at,
    }


# backwards compat wrappers (delegating to cortage)
list_bridesmaids = list_cortage
update_bridesmaid = update_cortage
get_bridesmaid = get_cortage
