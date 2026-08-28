import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, get_current_wedding
from app.models.user import User
from app.models.wedding import Wedding
from app.schemas.bridesmaid import BridesmaidResponse, BridesmaidUpdate
from app.services import bridesmaid as bridesmaid_service

router = APIRouter()


@router.get("/", response_model=list[BridesmaidResponse])
async def list_bridesmaids(
    wedding_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    wedding: Annotated[Wedding, Depends(get_current_wedding)],
    db: AsyncSession = Depends(get_db),
) -> list[BridesmaidResponse]:
    return await bridesmaid_service.list_bridesmaids(db, wedding_id)  # type: ignore[return-value]


@router.patch("/{bridesmaid_id}", response_model=BridesmaidResponse)
async def update_bridesmaid(
    wedding_id: uuid.UUID,
    bridesmaid_id: uuid.UUID,
    data: BridesmaidUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    wedding: Annotated[Wedding, Depends(get_current_wedding)],
    db: AsyncSession = Depends(get_db),
) -> BridesmaidResponse:
    item = await bridesmaid_service.update_bridesmaid(db, wedding_id, bridesmaid_id, data)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bridesmaid not found")
    return item  # type: ignore[return-value]


@router.get("/{bridesmaid_id}", response_model=BridesmaidResponse)
async def get_bridesmaid(
    wedding_id: uuid.UUID,
    bridesmaid_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    wedding: Annotated[Wedding, Depends(get_current_wedding)],
    db: AsyncSession = Depends(get_db),
) -> BridesmaidResponse:
    item = await bridesmaid_service.get_bridesmaid(db, wedding_id, bridesmaid_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bridesmaid not found")
    return item  # type: ignore[return-value]
