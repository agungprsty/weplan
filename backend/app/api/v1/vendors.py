import uuid
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, get_current_wedding
from app.models.user import User
from app.models.wedding import Wedding
from app.schemas.vendor import VendorCreate, VendorResponse, VendorUpdate
from app.services import vendor as vendor_service

router = APIRouter()


def _is_premium(wedding: Wedding) -> bool:
    if wedding.plan_expires_at is None:
        return False
    # naive UTC comparison
    now = datetime.now(UTC).replace(tzinfo=None)
    return wedding.plan_expires_at > now and wedding.plan_id is not None


@router.get("/", response_model=list[VendorResponse])
async def list_vendors(
    wedding_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    wedding: Annotated[Wedding, Depends(get_current_wedding)],
    db: AsyncSession = Depends(get_db),
) -> list[VendorResponse]:
    return await vendor_service.list_vendors(db, wedding_id)


@router.post("/", response_model=VendorResponse, status_code=status.HTTP_201_CREATED)
async def create_vendor(
    wedding_id: uuid.UUID,
    data: VendorCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    wedding: Annotated[Wedding, Depends(get_current_wedding)],
    db: AsyncSession = Depends(get_db),
) -> VendorResponse:
    if not _is_premium(wedding):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "PREMIUM_REQUIRED",
                "message": "Fitur Vendor hanya untuk Paket Premium 50k/6 bulan. Silakan upgrade.",
            },
        )
    return await vendor_service.create_vendor(db, wedding_id, data)


@router.patch("/{vendor_id}", response_model=VendorResponse)
async def update_vendor(
    wedding_id: uuid.UUID,
    vendor_id: uuid.UUID,
    data: VendorUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    wedding: Annotated[Wedding, Depends(get_current_wedding)],
    db: AsyncSession = Depends(get_db),
) -> VendorResponse:
    vendor = await vendor_service.update_vendor(db, wedding_id, vendor_id, data)
    if vendor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")
    return vendor


@router.get("/{vendor_id}", response_model=VendorResponse)
async def get_vendor(
    wedding_id: uuid.UUID,
    vendor_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    wedding: Annotated[Wedding, Depends(get_current_wedding)],
    db: AsyncSession = Depends(get_db),
) -> VendorResponse:
    vendor = await vendor_service.get_vendor(db, wedding_id, vendor_id)
    if vendor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")
    return vendor


@router.delete("/{vendor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vendor(
    wedding_id: uuid.UUID,
    vendor_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    wedding: Annotated[Wedding, Depends(get_current_wedding)],
    db: AsyncSession = Depends(get_db),
) -> None:
    ok = await vendor_service.delete_vendor(db, wedding_id, vendor_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")
