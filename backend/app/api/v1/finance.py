import uuid
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
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


# Savings Target singleton — sinkron otomatis dari wedding.total_budget & wedding_date
@router.get("/savings-target", response_model=SavingsTargetResponse)
async def get_savings_target(
    wedding_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    wedding: Annotated[Wedding, Depends(get_current_wedding)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SavingsTargetResponse:
    target = await savings_service.get_savings_target(db, wedding_id)
    # Lazy-sync: jika target belum ada atau beda dengan wedding, sinkronkan
    desired_amount = wedding.total_budget or 0
    desired_deadline = wedding.wedding_date
    if target is None:
        if desired_amount or desired_deadline:
            from app.services.wedding import sync_savings_target

            await sync_savings_target(db, wedding)
            target = await savings_service.get_savings_target(db, wedding_id)
    elif target.target_amount != desired_amount or target.deadline != desired_deadline:
        from app.services.wedding import sync_savings_target

        await sync_savings_target(db, wedding)
        target = await savings_service.get_savings_target(db, wedding_id)

    total_masuk, total_keluar, current = await savings_service.compute_finance_stats(
        db, wedding_id
    )
    if target is None:
        # wedding tanpa budget/date → return default virtual (tidak persist)
        return SavingsTargetResponse(
            id=uuid.uuid4(),
            wedding_id=wedding_id,
            target_amount=desired_amount,
            deadline=desired_deadline,
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
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SavingsTargetResponse:
    # Sinkron balik ke wedding agar single source of truth terjaga
    # (frontend baru tidak memanggil PUT lagi; PUT dipertahankan untuk kompatibilitas)
    update_dict = data.model_dump(exclude_unset=True)
    if "target_amount" in update_dict:
        wedding.total_budget = update_dict["target_amount"]
    if "deadline" in update_dict:
        wedding.wedding_date = update_dict["deadline"]
    await db.flush()
    target = await savings_service.upsert_savings_target(
        db, wedding_id, data, actor=current_user
    )
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
@router.get("/transactions")
async def list_transactions(
    wedding_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    wedding: Annotated[Wedding, Depends(get_current_wedding)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    from app.schemas.pagination import pages_calc

    items, total = await txn_service.list_transactions(db, wedding_id, page=page, limit=limit)
    return {"data": items, "meta": {"total": total, "page": page, "limit": limit, "pages": pages_calc(total, limit)}}


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
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TransactionResponse:
    if not _is_premium(wedding):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "PREMIUM_REQUIRED",
                "message": "Fitur Cashflow hanya untuk Premium 50k/6 bulan. Gratis hanya input Target Dana.",  # noqa: E501
            },
        )
    return await txn_service.create_transaction(
        db, wedding_id, data, actor=current_user
    )


@router.patch("/transactions/{txn_id}", response_model=TransactionResponse)
async def update_transaction(
    wedding_id: uuid.UUID,
    txn_id: uuid.UUID,
    data: TransactionUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    wedding: Annotated[Wedding, Depends(get_current_wedding)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TransactionResponse:
    if not _is_premium(wedding):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "PREMIUM_REQUIRED", "message": "Premium required"},
        )
    txn = await txn_service.update_transaction(
        db, wedding_id, txn_id, data, actor=current_user
    )
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
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    if not _is_premium(wedding):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "PREMIUM_REQUIRED", "message": "Premium required"},
        )
    ok = await txn_service.delete_transaction(
        db, wedding_id, txn_id, actor=current_user
    )
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Transaksi tidak ditemukan"
        )
