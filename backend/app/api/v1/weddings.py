import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, get_current_wedding
from app.core.limiter import limiter
from app.models.user import User
from app.models.wedding import Wedding
from app.models.wedding_user import WeddingUser
from app.schemas.wedding import (
    WeddingCreate,
    WeddingPairRequest,
    WeddingPreviewResponse,
    WeddingResponse,
    WeddingUpdate,
)
from app.services import wedding as wedding_service

router = APIRouter()


@router.post("/", response_model=WeddingResponse, status_code=status.HTTP_201_CREATED)
async def create_wedding(
    data: WeddingCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
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
    db: Annotated[AsyncSession, Depends(get_db)],
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
        ) from e
    return wedding  # type: ignore[return-value]


@router.get("/preview/{pair_code}", response_model=WeddingPreviewResponse)
@limiter.limit("20/minute")
async def preview_wedding(
    pair_code: str,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> WeddingPreviewResponse:
    """Public preview untuk invite link — tidak perlu auth, aman untuk share.
    Rate limit 20/min untuk cegah brute force."""
    code = pair_code.strip().upper()
    if not code or len(code) < 6 or len(code) > 8:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid pair code")
    result = await db.execute(select(Wedding).where(Wedding.pair_code == code))
    wedding = result.scalar_one_or_none()
    if wedding is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid pair code")
    cnt = await db.scalar(
        select(func.count()).select_from(WeddingUser).where(WeddingUser.wedding_id == wedding.id)
    )
    member_count = int(cnt or 0)
    return WeddingPreviewResponse(
        title=wedding.title,
        partner1_name=wedding.partner1_name,
        partner2_name=wedding.partner2_name,
        wedding_date=wedding.wedding_date,
        member_count=member_count,
        pair_code=wedding.pair_code,
        is_full=member_count >= 2,
    )


@router.get("/me", response_model=WeddingResponse | None)
async def get_my_wedding(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> WeddingResponse | None:
    wedding = await wedding_service.get_user_wedding(db, current_user)
    return wedding  # type: ignore[return-value]


@router.patch("/{wedding_id}", response_model=WeddingResponse)
async def update_wedding(
    wedding_id: uuid.UUID,
    data: WeddingUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    wedding: Annotated[Wedding, Depends(get_current_wedding)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> WeddingResponse:
    updated = await wedding_service.update_wedding(db, wedding, data, actor=current_user)
    return updated  # type: ignore[return-value]
