import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, get_current_wedding
from app.models.user import User
from app.models.wedding import Wedding
from app.schemas.wedding import (
    WeddingCreate,
    WeddingPairRequest,
    WeddingResponse,
    WeddingUpdate,
)
from app.services import wedding as wedding_service

router = APIRouter()


@router.post("/", response_model=WeddingResponse, status_code=status.HTTP_201_CREATED)
async def create_wedding(
    data: WeddingCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> WeddingResponse:
    existing = await wedding_service.get_user_wedding(db, current_user)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have a wedding",
        )
    wedding = await wedding_service.create_wedding(db, data, current_user)
    return wedding


@router.post("/pair", response_model=WeddingResponse)
async def pair_wedding(
    data: WeddingPairRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> WeddingResponse:
    existing = await wedding_service.get_user_wedding(db, current_user)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have a wedding",
        )
    try:
        wedding = await wedding_service.pair_wedding(db, data.pair_code, current_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    return wedding


@router.get("/me", response_model=WeddingResponse | None)
async def get_my_wedding(
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> WeddingResponse | None:
    wedding = await wedding_service.get_user_wedding(db, current_user)
    return wedding


@router.patch("/{wedding_id}", response_model=WeddingResponse)
async def update_wedding(
    wedding_id: uuid.UUID,
    data: WeddingUpdate,
    wedding: Annotated[Wedding, Depends(get_current_wedding)],
    db: AsyncSession = Depends(get_db),
) -> WeddingResponse:
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(wedding, field, value)
    await db.flush()
    await db.refresh(wedding)
    return wedding
