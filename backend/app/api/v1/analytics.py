import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, get_current_wedding
from app.models.user import User
from app.models.wedding import Wedding
from app.schemas.analytics import (
    ChecklistAnalyticsResponse,
    FinanceAnalyticsResponse,
    GuestAnalyticsResponse,
)
from app.services.analytics import (
    get_checklist_analytics,
    get_finance_analytics,
    get_guest_analytics,
)

router = APIRouter()


@router.get("/analytics/finance", response_model=FinanceAnalyticsResponse)
async def finance_analytics(
    wedding_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    wedding: Annotated[Wedding, Depends(get_current_wedding)],
    db: AsyncSession = Depends(get_db),
) -> FinanceAnalyticsResponse:
    return await get_finance_analytics(db, wedding)


@router.get("/analytics/guests", response_model=GuestAnalyticsResponse)
async def guest_analytics(
    wedding_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    wedding: Annotated[Wedding, Depends(get_current_wedding)],
    db: AsyncSession = Depends(get_db),
) -> GuestAnalyticsResponse:
    return await get_guest_analytics(db, wedding)


@router.get("/analytics/checklists", response_model=ChecklistAnalyticsResponse)
async def checklist_analytics(
    wedding_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    wedding: Annotated[Wedding, Depends(get_current_wedding)],
    db: AsyncSession = Depends(get_db),
) -> ChecklistAnalyticsResponse:
    return await get_checklist_analytics(db, wedding)
