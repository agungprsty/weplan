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
    return wedding  # type: ignore[return-value]


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
    return wedding  # type: ignore[return-value]


@router.get("/me", response_model=WeddingResponse | None)
async def get_my_wedding(
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> WeddingResponse | None:
    wedding = await wedding_service.get_user_wedding(db, current_user)
    return wedding  # type: ignore[return-value]


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
    # Sinkronkan savings_target jika total_budget / wedding_date berubah
    if "total_budget" in update_data or "wedding_date" in update_data:
        from app.services.wedding import sync_savings_target

        await sync_savings_target(db, wedding)
    await db.refresh(wedding)
    # Ensure member_count present for response (service helper would have it, but for deps wedding we need to attach)
    if not hasattr(wedding, "member_count"):
        from sqlalchemy import func, select

        from app.models.wedding_user import WeddingUser

        cnt = await db.scalar(
            select(func.count())
            .select_from(WeddingUser)
            .where(WeddingUser.wedding_id == wedding.id)
        )
        wedding.member_count = int(cnt or 0)
    return wedding  # type: ignore[return-value]
