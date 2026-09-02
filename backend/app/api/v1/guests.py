import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, get_current_wedding
from app.models.user import User
from app.models.wedding import Wedding
from app.schemas.guest import GuestCreate, GuestResponse, GuestUpdate
from app.schemas.pagination import pages_calc
from app.services import guest as guest_service

router = APIRouter()


@router.get("/")
async def list_guests(
    wedding_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    wedding: Annotated[Wedding, Depends(get_current_wedding)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    guests, total = await guest_service.list_guests(db, wedding_id, page=page, limit=limit)
    # Support both paginated object (new) and legacy array for backward compat when client omits pagination detection
    # Always return paginated shape; frontend unwraps via data/meta check. Tests updated accordingly.
    return {
        "data": guests,
        "meta": {"total": total, "page": page, "limit": limit, "pages": pages_calc(total, limit)},
    }


@router.post("/", response_model=GuestResponse, status_code=status.HTTP_201_CREATED)
async def create_guest(
    wedding_id: uuid.UUID,
    data: GuestCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    wedding: Annotated[Wedding, Depends(get_current_wedding)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> GuestResponse:
    return await guest_service.create_guest(db, wedding_id, data, actor=current_user)


@router.patch("/{guest_id}", response_model=GuestResponse)
async def update_guest(
    wedding_id: uuid.UUID,
    guest_id: uuid.UUID,
    data: GuestUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    wedding: Annotated[Wedding, Depends(get_current_wedding)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> GuestResponse:
    guest = await guest_service.update_guest(
        db, wedding_id, guest_id, data, actor=current_user
    )
    if guest is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Guest not found",
        )
    return guest


@router.get("/{guest_id}", response_model=GuestResponse)
async def get_guest(
    wedding_id: uuid.UUID,
    guest_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    wedding: Annotated[Wedding, Depends(get_current_wedding)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> GuestResponse:
    guest = await guest_service.get_guest(db, wedding_id, guest_id)
    if guest is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Guest not found",
        )
    return guest


@router.delete("/{guest_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_guest(
    wedding_id: uuid.UUID,
    guest_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    wedding: Annotated[Wedding, Depends(get_current_wedding)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    ok = await guest_service.delete_guest(db, wedding_id, guest_id, actor=current_user)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Guest not found",
        )
