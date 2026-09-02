from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.kua_document import KuaDocument
from app.schemas.kua_document import KuaDocumentUpdate
from app.services.activity import log_activity

if TYPE_CHECKING:
    from app.models.user import User

KUA_TEMPLATE = [
    {
        "document_key": "ktp_cpp",
        "title": "FC KTP",
        "owner_type": "cpp",
        "is_required": True,
    },
    {
        "document_key": "ktp_cpw",
        "title": "FC KTP",
        "owner_type": "cpw",
        "is_required": True,
    },
    {
        "document_key": "kk_cpp",
        "title": "FC KK",
        "owner_type": "cpp",
        "is_required": True,
    },
    {
        "document_key": "kk_cpw",
        "title": "FC KK",
        "owner_type": "cpw",
        "is_required": True,
    },
    {
        "document_key": "akta_cpp",
        "title": "FC Akta Kelahiran",
        "owner_type": "cpp",
        "is_required": True,
    },
    {
        "document_key": "akta_cpw",
        "title": "FC Akta Kelahiran",
        "owner_type": "cpw",
        "is_required": True,
    },
    {
        "document_key": "n1_n4",
        "title": "Surat Pengantar N1-N4 dari Kelurahan",
        "owner_type": "both",
        "is_required": True,
    },
    {
        "document_key": "pas_foto",
        "title": "Pas foto 2x3 & 4x6 background biru (4 lembar)",
        "owner_type": "both",
        "is_required": True,
    },
    {
        "document_key": "sehat",
        "title": "Surat Keterangan Sehat Puskesmas",
        "owner_type": "both",
        "is_required": True,
    },
    {
        "document_key": "numpang_nikah",
        "title": "Surat Numpang Nikah (jika beda kecamatan)",
        "owner_type": "cpp",
        "is_required": False,
    },
]


async def list_kua_documents(
    db: AsyncSession, wedding_id: uuid.UUID
) -> list[KuaDocument]:
    result = await db.execute(
        select(KuaDocument)
        .where(KuaDocument.wedding_id == wedding_id)
        .order_by(KuaDocument.created_at)
    )
    return list(result.scalars().all())


async def seed_kua_documents(
    db: AsyncSession, wedding_id: uuid.UUID
) -> list[KuaDocument]:
    existing = await list_kua_documents(db, wedding_id)
    if existing:
        return existing
    docs = []
    for tmpl in KUA_TEMPLATE:
        doc = KuaDocument(wedding_id=wedding_id, **tmpl)
        db.add(doc)
        docs.append(doc)
    await db.flush()
    for d in docs:
        await db.refresh(d)
    return docs


async def create_kua_document(
    db: AsyncSession,
    wedding_id: uuid.UUID,
    data: dict,
    actor: User | None = None,
) -> KuaDocument:
    # Generate unique document_key for custom docs if not provided or collides
    key = data.get("document_key")
    if not key:
        # slug from title + short uuid to avoid collision across regions/jobs
        slug = data["title"].strip().lower().replace(" ", "_")[:30]
        # sanitize: keep alnum and underscore
        slug = (
            "".join(c if c.isalnum() or c == "_" else "_" for c in slug).strip("_")
            or "custom"
        )
        key = f"custom_{slug}_{uuid.uuid4().hex[:6]}"
        data["document_key"] = key
    else:
        # ensure custom prefix to distinguish from template keys when user provides key
        if key in {t["document_key"] for t in KUA_TEMPLATE}:
            key = f"custom_{key}_{uuid.uuid4().hex[:4]}"
            data["document_key"] = key
    doc = KuaDocument(wedding_id=wedding_id, **data)
    db.add(doc)
    await db.flush()
    await db.refresh(doc)
    await log_activity(
        db,
        wedding_id,
        actor,
        "created",
        "kua_document",
        doc.id,
        doc.title,
    )
    return doc


async def delete_kua_document(
    db: AsyncSession,
    wedding_id: uuid.UUID,
    doc_id: uuid.UUID,
    actor: User | None = None,
) -> bool:
    result = await db.execute(
        select(KuaDocument).where(
            KuaDocument.id == doc_id, KuaDocument.wedding_id == wedding_id
        )
    )
    doc = result.scalar_one_or_none()
    if doc is None:
        return False
    title = doc.title
    await db.delete(doc)
    await db.flush()
    await log_activity(
        db,
        wedding_id,
        actor,
        "deleted",
        "kua_document",
        doc_id,
        title,
    )
    return True


async def update_kua_document(
    db: AsyncSession,
    wedding_id: uuid.UUID,
    doc_id: uuid.UUID,
    data: KuaDocumentUpdate,
    actor: User | None = None,
) -> KuaDocument | None:
    result = await db.execute(
        select(KuaDocument).where(
            KuaDocument.id == doc_id, KuaDocument.wedding_id == wedding_id
        )
    )
    doc = result.scalar_one_or_none()
    if doc is None:
        return None
    old_status = doc.status
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(doc, field, value)
    await db.flush()
    await db.refresh(doc)

    new_status = doc.status
    if "status" in update_data and old_status != new_status:
        await log_activity(
            db,
            wedding_id,
            actor,
            "status_changed",
            "kua_document",
            doc.id,
            doc.title,
            meta={"from": old_status, "to": new_status},
        )
    elif update_data:
        await log_activity(
            db,
            wedding_id,
            actor,
            "updated",
            "kua_document",
            doc.id,
            doc.title,
        )
    return doc


async def get_kua_document(
    db: AsyncSession, wedding_id: uuid.UUID, doc_id: uuid.UUID
) -> KuaDocument | None:
    result = await db.execute(
        select(KuaDocument).where(
            KuaDocument.id == doc_id, KuaDocument.wedding_id == wedding_id
        )
    )
    return result.scalar_one_or_none()
