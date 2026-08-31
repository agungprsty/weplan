import uuid
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, get_current_wedding
from app.models.user import User
from app.models.wedding import Wedding
from app.schemas.mahar_item import MaharItemCreate, MaharItemResponse, MaharItemUpdate
from app.services import mahar_item as mahar_service

router = APIRouter()

FREE_MAHAR_LIMIT = 5


def _is_premium(wedding: Wedding) -> bool:
    if wedding.plan_expires_at is None:
        return False
    now = datetime.now(UTC).replace(tzinfo=None)
    return wedding.plan_expires_at > now and wedding.plan_id is not None


@router.get("/", response_model=list[MaharItemResponse])
async def list_mahar_items(
    wedding_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    wedding: Annotated[Wedding, Depends(get_current_wedding)],
    db: AsyncSession = Depends(get_db),
) -> list[MaharItemResponse]:
    return await mahar_service.list_mahar_items(db, wedding_id)


@router.post("/", response_model=MaharItemResponse, status_code=status.HTTP_201_CREATED)
async def create_mahar_item(
    wedding_id: uuid.UUID,
    data: MaharItemCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    wedding: Annotated[Wedding, Depends(get_current_wedding)],
    db: AsyncSession = Depends(get_db),
) -> MaharItemResponse:
    if not _is_premium(wedding):
        count = await mahar_service.count_mahar_items(db, wedding_id)
        if count >= FREE_MAHAR_LIMIT:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "PREMIUM_REQUIRED",
                    "message": f"Gratis hanya {FREE_MAHAR_LIMIT} item Mahar & Seserahan. Upgrade Premium 50k/6 bulan untuk unlimited + cicilan.",
                },
            )
    return await mahar_service.create_mahar_item(
        db, wedding_id, data, actor=current_user
    )


@router.patch("/{item_id}", response_model=MaharItemResponse)
async def update_mahar_item(
    wedding_id: uuid.UUID,
    item_id: uuid.UUID,
    data: MaharItemUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    wedding: Annotated[Wedding, Depends(get_current_wedding)],
    db: AsyncSession = Depends(get_db),
) -> MaharItemResponse:
    item = await mahar_service.update_mahar_item(
        db, wedding_id, item_id, data, actor=current_user
    )
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item tidak ditemukan"
        )
    return item


@router.get("/{item_id}", response_model=MaharItemResponse)
async def get_mahar_item(
    wedding_id: uuid.UUID,
    item_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    wedding: Annotated[Wedding, Depends(get_current_wedding)],
    db: AsyncSession = Depends(get_db),
) -> MaharItemResponse:
    item = await mahar_service.get_mahar_item(db, wedding_id, item_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item tidak ditemukan"
        )
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mahar_item(
    wedding_id: uuid.UUID,
    item_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    wedding: Annotated[Wedding, Depends(get_current_wedding)],
    db: AsyncSession = Depends(get_db),
) -> None:
    ok = await mahar_service.delete_mahar_item(
        db, wedding_id, item_id, actor=current_user
    )
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item tidak ditemukan"
        )
