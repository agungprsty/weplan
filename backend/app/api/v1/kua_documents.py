import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, get_current_wedding
from app.models.user import User
from app.models.wedding import Wedding
from app.schemas.kua_document import (
    KuaDocumentCreate,
    KuaDocumentResponse,
    KuaDocumentUpdate,
)
from app.services import kua_document as kua_service

router = APIRouter()


@router.get("/", response_model=list[KuaDocumentResponse])
async def list_kua_documents(
    wedding_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    wedding: Annotated[Wedding, Depends(get_current_wedding)],
    db: Annotated[AsyncSession, Depends(get_db)],
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
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[KuaDocumentResponse]:
    return await kua_service.seed_kua_documents(db, wedding_id)


@router.post(
    "/", response_model=KuaDocumentResponse, status_code=status.HTTP_201_CREATED
)
async def create_kua_document(
    wedding_id: uuid.UUID,
    data: KuaDocumentCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    wedding: Annotated[Wedding, Depends(get_current_wedding)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> KuaDocumentResponse:
    """Tambah berkas custom — untuk kebutuhan per daerah / pekerjaan masing-masing."""
    payload = data.model_dump(exclude_unset=True)
    # ensure status defaults to 'belum' if not supplied
    payload.setdefault("status", "belum")
    doc = await kua_service.create_kua_document(
        db, wedding_id, payload, actor=current_user
    )
    return doc


@router.patch("/{doc_id}", response_model=KuaDocumentResponse)
async def update_kua_document(
    wedding_id: uuid.UUID,
    doc_id: uuid.UUID,
    data: KuaDocumentUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    wedding: Annotated[Wedding, Depends(get_current_wedding)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> KuaDocumentResponse:
    # Jika upload file_url dan bukan premium, tetap izinkan karena Berkas KUA gratis dasar  # noqa: E501
    # Premium hanya untuk expiry alert — untuk MVP gratis semua
    doc = await kua_service.update_kua_document(
        db, wedding_id, doc_id, data, actor=current_user
    )
    if doc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Dokumen tidak ditemukan"
        )
    return doc


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_kua_document(
    wedding_id: uuid.UUID,
    doc_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    wedding: Annotated[Wedding, Depends(get_current_wedding)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    ok = await kua_service.delete_kua_document(
        db, wedding_id, doc_id, actor=current_user
    )
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Dokumen tidak ditemukan"
        )


@router.get("/{doc_id}", response_model=KuaDocumentResponse)
async def get_kua_document(
    wedding_id: uuid.UUID,
    doc_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    wedding: Annotated[Wedding, Depends(get_current_wedding)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> KuaDocumentResponse:
    doc = await kua_service.get_kua_document(db, wedding_id, doc_id)
    if doc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Dokumen tidak ditemukan"
        )
    return doc
