import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, get_current_wedding
from app.models.user import User
from app.models.wedding import Wedding
from app.schemas.gift import GiftCreate, GiftResponse, GiftUpdate
from app.services import gift as gift_service

router = APIRouter()


@router.get("/", response_model=list[GiftResponse])
async def list_gifts(
    wedding_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    wedding: Annotated[Wedding, Depends(get_current_wedding)],
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    return await gift_service.list_gifts(db, wedding_id)


@router.post("/", response_model=GiftResponse, status_code=status.HTTP_201_CREATED)
async def create_gift(
    wedding_id: uuid.UUID,
    data: GiftCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    wedding: Annotated[Wedding, Depends(get_current_wedding)],
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await gift_service.create_gift(db, wedding_id, data)


@router.get("/{gift_id}", response_model=GiftResponse)
async def get_gift(
    wedding_id: uuid.UUID,
    gift_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    wedding: Annotated[Wedding, Depends(get_current_wedding)],
    db: AsyncSession = Depends(get_db),
) -> dict:
    gift = await gift_service.get_gift(db, wedding_id, gift_id)
    if gift is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gift not found",
        )
    return gift


@router.patch("/{gift_id}", response_model=GiftResponse)
async def update_gift(
    wedding_id: uuid.UUID,
    gift_id: uuid.UUID,
    data: GiftUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    wedding: Annotated[Wedding, Depends(get_current_wedding)],
    db: AsyncSession = Depends(get_db),
) -> dict:
    gift = await gift_service.update_gift(db, wedding_id, gift_id, data)
    if gift is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gift not found",
        )
    return gift


@router.delete("/{gift_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_gift(
    wedding_id: uuid.UUID,
    gift_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    wedding: Annotated[Wedding, Depends(get_current_wedding)],
    db: AsyncSession = Depends(get_db),
) -> None:
    deleted = await gift_service.delete_gift(db, wedding_id, gift_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gift not found",
        )
