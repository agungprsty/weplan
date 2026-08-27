import uuid
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, get_current_wedding
from app.models.user import User
from app.models.wedding import Wedding
from app.schemas.savings_target import SavingsTargetResponse, SavingsTargetUpdate
from app.schemas.transaction import (
    TransactionCreate,
    TransactionResponse,
    TransactionUpdate,
)
from app.services import savings_target as savings_service
from app.services import transaction as txn_service

router = APIRouter()


def _is_premium(wedding: Wedding) -> bool:
    if wedding.plan_expires_at is None:
        return False
    now = datetime.now(UTC).replace(tzinfo=None)
    return wedding.plan_expires_at > now and wedding.plan_id is not None


# Savings Target singleton
@router.get("/savings-target", response_model=SavingsTargetResponse)
async def get_savings_target(
    wedding_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    wedding: Annotated[Wedding, Depends(get_current_wedding)],
    db: AsyncSession = Depends(get_db),
) -> SavingsTargetResponse:
    target = await savings_service.get_savings_target(db, wedding_id)
    total_masuk, total_keluar, current = await savings_service.compute_finance_stats(
        db, wedding_id
    )
    if target is None:
        # return empty default without persisting
        return SavingsTargetResponse(
            id=uuid.uuid4(),
            wedding_id=wedding_id,
            target_amount=0,
            deadline=None,
            created_at=datetime.now(UTC).replace(tzinfo=None),
            updated_at=datetime.now(UTC).replace(tzinfo=None),
            current_amount=current,
            total_masuk=total_masuk,
            total_keluar=total_keluar,
            progress_pct=0.0,
        )
    progress = 0.0
    if target.target_amount > 0:
        # progress based on current saldo (masuk - keluar) capped at 0-100+
        progress = round((current / target.target_amount) * 100, 2)
    return SavingsTargetResponse(
        id=target.id,
        wedding_id=target.wedding_id,
        target_amount=target.target_amount,
        deadline=target.deadline,
        created_at=target.created_at,
        updated_at=target.updated_at,
        current_amount=current,
        total_masuk=total_masuk,
        total_keluar=total_keluar,
        progress_pct=progress,
    )


@router.put("/savings-target", response_model=SavingsTargetResponse)
async def put_savings_target(
    wedding_id: uuid.UUID,
    data: SavingsTargetUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    wedding: Annotated[Wedding, Depends(get_current_wedding)],
    db: AsyncSession = Depends(get_db),
) -> SavingsTargetResponse:
    target = await savings_service.upsert_savings_target(db, wedding_id, data)
    total_masuk, total_keluar, current = await savings_service.compute_finance_stats(
        db, wedding_id
    )
    progress = 0.0
    if target.target_amount > 0:
        progress = round((current / target.target_amount) * 100, 2)
    return SavingsTargetResponse(
        id=target.id,
        wedding_id=target.wedding_id,
        target_amount=target.target_amount,
        deadline=target.deadline,
        created_at=target.created_at,
        updated_at=target.updated_at,
        current_amount=current,
        total_masuk=total_masuk,
        total_keluar=total_keluar,
        progress_pct=progress,
    )


# Transactions
@router.get("/transactions", response_model=list[TransactionResponse])
async def list_transactions(
    wedding_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    wedding: Annotated[Wedding, Depends(get_current_wedding)],
    db: AsyncSession = Depends(get_db),
) -> list[TransactionResponse]:
    return await txn_service.list_transactions(db, wedding_id)


@router.post(
    "/transactions",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_transaction(
    wedding_id: uuid.UUID,
    data: TransactionCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    wedding: Annotated[Wedding, Depends(get_current_wedding)],
    db: AsyncSession = Depends(get_db),
) -> TransactionResponse:
    if not _is_premium(wedding):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "PREMIUM_REQUIRED",
                "message": "Fitur Cashflow hanya untuk Premium 50k/6 bulan. Gratis hanya input Target Dana.",
            },
        )
    return await txn_service.create_transaction(db, wedding_id, data)


@router.patch("/transactions/{txn_id}", response_model=TransactionResponse)
async def update_transaction(
    wedding_id: uuid.UUID,
    txn_id: uuid.UUID,
    data: TransactionUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    wedding: Annotated[Wedding, Depends(get_current_wedding)],
    db: AsyncSession = Depends(get_db),
) -> TransactionResponse:
    if not _is_premium(wedding):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "PREMIUM_REQUIRED", "message": "Premium required"},
        )
    txn = await txn_service.update_transaction(db, wedding_id, txn_id, data)
    if txn is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Transaksi tidak ditemukan"
        )
    return txn


@router.delete("/transactions/{txn_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    wedding_id: uuid.UUID,
    txn_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    wedding: Annotated[Wedding, Depends(get_current_wedding)],
    db: AsyncSession = Depends(get_db),
) -> None:
    if not _is_premium(wedding):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "PREMIUM_REQUIRED", "message": "Premium required"},
        )
    ok = await txn_service.delete_transaction(db, wedding_id, txn_id)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Transaksi tidak ditemukan"
        )
