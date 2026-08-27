import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, get_current_wedding
from app.models.user import User
from app.models.wedding import Wedding
from app.schemas.kua_document import KuaDocumentResponse, KuaDocumentUpdate
from app.services import kua_document as kua_service

router = APIRouter()


@router.get("/", response_model=list[KuaDocumentResponse])
async def list_kua_documents(
    wedding_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    wedding: Annotated[Wedding, Depends(get_current_wedding)],
    db: AsyncSession = Depends(get_db),
) -> list[KuaDocumentResponse]:
    docs = await kua_service.list_kua_documents(db, wedding_id)
    if not docs:
        docs = await kua_service.seed_kua_documents(db, wedding_id)
    return docs


@router.post(
    "/seed",
    response_model=list[KuaDocumentResponse],
    status_code=status.HTTP_201_CREATED,
)
async def seed_kua(
    wedding_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    wedding: Annotated[Wedding, Depends(get_current_wedding)],
    db: AsyncSession = Depends(get_db),
) -> list[KuaDocumentResponse]:
    return await kua_service.seed_kua_documents(db, wedding_id)


@router.patch("/{doc_id}", response_model=KuaDocumentResponse)
async def update_kua_document(
    wedding_id: uuid.UUID,
    doc_id: uuid.UUID,
    data: KuaDocumentUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    wedding: Annotated[Wedding, Depends(get_current_wedding)],
    db: AsyncSession = Depends(get_db),
) -> KuaDocumentResponse:
    # Jika upload file_url dan bukan premium, tetap izinkan karena Berkas KUA gratis dasar
    # Premium hanya untuk expiry alert — untuk MVP gratis semua
    doc = await kua_service.update_kua_document(db, wedding_id, doc_id, data)
    if doc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Dokumen tidak ditemukan"
        )
    return doc


@router.get("/{doc_id}", response_model=KuaDocumentResponse)
async def get_kua_document(
    wedding_id: uuid.UUID,
    doc_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    wedding: Annotated[Wedding, Depends(get_current_wedding)],
    db: AsyncSession = Depends(get_db),
) -> KuaDocumentResponse:
    doc = await kua_service.get_kua_document(db, wedding_id, doc_id)
    if doc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Dokumen tidak ditemukan"
        )
    return doc
