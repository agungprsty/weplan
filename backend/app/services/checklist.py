from __future__ import annotations

import uuid
from datetime import date, timedelta
from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.checklist import Checklist
from app.schemas.checklist import ChecklistCreate, ChecklistUpdate

if TYPE_CHECKING:
    from app.models.user import User

from app.services.activity import log_activity

# Template 12 bulan default — 30 tugas auto-generate dari wedding_date
CHECKLIST_TEMPLATE_12BULAN: list[dict] = [
    {
        "title": "Tentukan tanggal akad & resepsi",
        "category": "lainnya",
        "offset_days": 365,
    },
    {
        "title": "Tentukan total anggaran & gaya adat",
        "category": "lainnya",
        "offset_days": 360,
    },
    {"title": "Estimasi jumlah tamu awal", "category": "undangan", "offset_days": 355},
    {"title": "Booking venue/gedung", "category": "vendor", "offset_days": 340},
    {"title": "Booking catering", "category": "catering", "offset_days": 335},
    {"title": "Booking MUA & busana", "category": "busana", "offset_days": 330},
    {
        "title": "Booking fotografer & videografer",
        "category": "dokumentasi",
        "offset_days": 325,
    },
    {"title": "Booking WO / koordinator", "category": "vendor", "offset_days": 320},
    {"title": "Pilih cincin kawin", "category": "seserahan", "offset_days": 300},
    {
        "title": "Pre-wedding & foto engagement",
        "category": "dokumentasi",
        "offset_days": 280,
    },
    {
        "title": "Desain & sebar Save the Date",
        "category": "undangan",
        "offset_days": 270,
    },
    {
        "title": "Pilih hiburan (band/DJ/organ)",
        "category": "hiburan",
        "offset_days": 260,
    },
    {"title": "Booking dekorasi pelaminan", "category": "dekorasi", "offset_days": 250},
    {"title": "Tes kesehatan TORCH", "category": "lainnya", "offset_days": 180},
    {
        "title": "Bimbingan Perkawinan (Bimwin) KUA",
        "category": "kua",
        "offset_days": 120,
    },
    {
        "title": "Daftar KUA & lengkapi berkas N1-N4",
        "category": "kua",
        "offset_days": 90,
    },
    {
        "title": "Surat Numpang Nikah (jika beda kecamatan)",
        "category": "kua",
        "offset_days": 85,
    },
    {"title": "Final fitting gaun & jas", "category": "busana", "offset_days": 60},
    {
        "title": "Pesan souvenir & undangan cetak",
        "category": "undangan",
        "offset_days": 55,
    },
    {
        "title": "Konfirmasi vendor & rundown H-30",
        "category": "vendor",
        "offset_days": 30,
    },
    {"title": "Gladi resik di venue", "category": "lainnya", "offset_days": 14},
    {
        "title": "Packing seserahan & hantaran",
        "category": "seserahan",
        "offset_days": 10,
    },
    {
        "title": "Ambil buku nikah & cek berkas akad",
        "category": "kua",
        "offset_days": 7,
    },
    {
        "title": "Konfirmasi kehadiran tamu (H-7)",
        "category": "undangan",
        "offset_days": 7,
    },
    {"title": "Siapkan angpao & buku tamu", "category": "lainnya", "offset_days": 3},
    {"title": "Check-in vendor H-1", "category": "vendor", "offset_days": 1},
    {"title": "Akad nikah", "category": "kua", "offset_days": 0},
    {"title": "Resepsi & dokumentasi", "category": "hiburan", "offset_days": 0},
    {
        "title": "Kirim terima kasih & angpao tracker",
        "category": "lainnya",
        "offset_days": -3,
    },
    {"title": "Honeymoon", "category": "lainnya", "offset_days": -7},
]


async def list_checklists(db: AsyncSession, wedding_id: uuid.UUID) -> list[Checklist]:
    result = await db.execute(
        select(Checklist)
        .where(Checklist.wedding_id == wedding_id)
        .order_by(Checklist.order, Checklist.created_at)
    )
    return list(result.scalars().all())


async def create_checklist(
    db: AsyncSession,
    wedding_id: uuid.UUID,
    data: ChecklistCreate,
    actor: User | None = None,
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
    await log_activity(
        db,
        wedding_id,
        actor,
        "created",
        "checklist",
        checklist.id,
        checklist.title,
    )
    return checklist


async def update_checklist(
    db: AsyncSession,
    wedding_id: uuid.UUID,
    checklist_id: uuid.UUID,
    data: ChecklistUpdate,
    actor: User | None = None,
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

    old_status = checklist.status
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(checklist, field, value)

    await db.flush()
    await db.refresh(checklist)

    new_status = checklist.status
    if "status" in update_data and old_status != new_status:
        await log_activity(
            db,
            wedding_id,
            actor,
            "status_changed",
            "checklist",
            checklist.id,
            checklist.title,
            meta={"from": old_status, "to": new_status},
        )
    elif update_data:
        await log_activity(
            db,
            wedding_id,
            actor,
            "updated",
            "checklist",
            checklist.id,
            checklist.title,
        )

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


async def delete_checklist(
    db: AsyncSession,
    wedding_id: uuid.UUID,
    checklist_id: uuid.UUID,
    actor: User | None = None,
) -> bool:
    checklist = await get_checklist(db, wedding_id, checklist_id)
    if checklist is None:
        return False
    title = checklist.title
    await db.delete(checklist)
    await db.flush()
    await log_activity(
        db,
        wedding_id,
        actor,
        "deleted",
        "checklist",
        checklist_id,
        title,
    )
    return True


async def auto_generate_checklists(
    db: AsyncSession,
    wedding_id: uuid.UUID,
    wedding_date: date | None,
    actor: User | None = None,
) -> list[Checklist]:
    existing = await list_checklists(db, wedding_id)
    if existing:
        return existing
    if wedding_date is None:
        # fallback: buat tanpa due_date jika tanggal belum diisi
        items = []
        for idx, tmpl in enumerate(CHECKLIST_TEMPLATE_12BULAN):
            item = Checklist(
                wedding_id=wedding_id,
                title=tmpl["title"],
                category=tmpl["category"],
                order=idx + 1,
            )
            db.add(item)
            items.append(item)
        await db.flush()
        for it in items:
            await db.refresh(it)
        await log_activity(
            db,
            wedding_id,
            actor,
            "auto_generated",
            "checklist",
            None,
            f"{len(items)} tugas",
        )
        return items
    items = []
    for idx, tmpl in enumerate(CHECKLIST_TEMPLATE_12BULAN):
        due = wedding_date - timedelta(days=tmpl["offset_days"])
        item = Checklist(
            wedding_id=wedding_id,
            title=tmpl["title"],
            category=tmpl["category"],
            due_date=due,
            order=idx + 1,
        )
        db.add(item)
        items.append(item)
    await db.flush()
    for it in items:
        await db.refresh(it)
    await log_activity(
        db,
        wedding_id,
        actor,
        "auto_generated",
        "checklist",
        None,
        f"{len(items)} tugas",
    )
    return items
