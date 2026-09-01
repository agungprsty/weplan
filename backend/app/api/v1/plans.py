import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.plan import PlanResponse
from app.services import plan as plan_service

router = APIRouter()


@router.get("/", response_model=list[PlanResponse])
async def list_plans(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[PlanResponse]:
    plans = await plan_service.list_active_plans(db)
    return plans


@router.get("/{plan_id}", response_model=PlanResponse)
async def get_plan(
    plan_id: uuid.UUID, db: Annotated[AsyncSession, Depends(get_db)]
) -> PlanResponse:
    plan = await plan_service.get_plan_by_id(db, plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan
