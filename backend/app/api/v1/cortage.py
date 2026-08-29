import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, get_current_wedding
from app.models.user import User
from app.models.wedding import Wedding
from app.schemas.cortage import CortageResponse, CortageUpdate
from app.services import cortage as cortage_service

router = APIRouter()


@router.get("/", response_model=list[CortageResponse])
async def list_cortage(
    wedding_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    wedding: Annotated[Wedding, Depends(get_current_wedding)],
    db: AsyncSession = Depends(get_db),
) -> list[CortageResponse]:
    return await cortage_service.list_cortage(db, wedding_id)  # type: ignore[return-value]


@router.patch("/{cortage_id}", response_model=CortageResponse)
async def update_cortage(
    wedding_id: uuid.UUID,
    cortage_id: uuid.UUID,
    data: CortageUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    wedding: Annotated[Wedding, Depends(get_current_wedding)],
    db: AsyncSession = Depends(get_db),
) -> CortageResponse:
    item = await cortage_service.update_cortage(db, wedding_id, cortage_id, data)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pengiring not found")
    return item  # type: ignore[return-value]


@router.get("/{cortage_id}", response_model=CortageResponse)
async def get_cortage(
    wedding_id: uuid.UUID,
    cortage_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    wedding: Annotated[Wedding, Depends(get_current_wedding)],
    db: AsyncSession = Depends(get_db),
) -> CortageResponse:
    item = await cortage_service.get_cortage(db, wedding_id, cortage_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pengiring not found")
    return item  # type: ignore[return-value]
