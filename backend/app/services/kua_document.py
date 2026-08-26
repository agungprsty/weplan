import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.kua_document import KuaDocument
from app.schemas.kua_document import KuaDocumentUpdate

# Template dasar 10 berkas KUA (gratis) — dipakai saat wedding dibuat
KUA_TEMPLATE = [
    {"document_key": "ktp_cpp", "title": "FC KTP CPP", "owner_type": "cpp", "is_required": True},
    {"document_key": "ktp_cpw", "title": "FC KTP CPW", "owner_type": "cpw", "is_required": True},
    {"document_key": "kk_cpp", "title": "FC KK CPP", "owner_type": "cpp", "is_required": True},
    {"document_key": "kk_cpw", "title": "FC KK CPW", "owner_type": "cpw", "is_required": True},
    {"document_key": "akta_cpp", "title": "FC Akta Kelahiran CPP", "owner_type": "cpp", "is_required": True},
    {"document_key": "akta_cpw", "title": "FC Akta Kelahiran CPW", "owner_type": "cpw", "is_required": True},
    {"document_key": "n1_n4", "title": "Surat Pengantar N1-N4 dari Kelurahan", "owner_type": "both", "is_required": True},
    {"document_key": "pas_foto", "title": "Pas foto 2x3 & 4x6 background biru (4 lembar)", "owner_type": "both", "is_required": True},
    {"document_key": "sehat", "title": "Surat Keterangan Sehat Puskesmas", "owner_type": "both", "is_required": True},
    {"document_key": "numpang_nikah", "title": "Surat Numpang Nikah (jika beda kecamatan)", "owner_type": "cpp", "is_required": False},
]


async def list_kua_documents(db: AsyncSession, wedding_id: uuid.UUID) -> list[KuaDocument]:
    result = await db.execute(
        select(KuaDocument).where(KuaDocument.wedding_id == wedding_id).order_by(KuaDocument.created_at)
    )
    return list(result.scalars().all())


async def seed_kua_documents(db: AsyncSession, wedding_id: uuid.UUID) -> list[KuaDocument]:
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


async def update_kua_document(
    db: AsyncSession, wedding_id: uuid.UUID, doc_id: uuid.UUID, data: KuaDocumentUpdate
) -> KuaDocument | None:
    result = await db.execute(
        select(KuaDocument).where(KuaDocument.id == doc_id, KuaDocument.wedding_id == wedding_id)
    )
    doc = result.scalar_one_or_none()
    if doc is None:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(doc, field, value)
    await db.flush()
    await db.refresh(doc)
    return doc


async def get_kua_document(
    db: AsyncSession, wedding_id: uuid.UUID, doc_id: uuid.UUID
) -> KuaDocument | None:
    result = await db.execute(
        select(KuaDocument).where(KuaDocument.id == doc_id, KuaDocument.wedding_id == wedding_id)
    )
    return result.scalar_one_or_none()
