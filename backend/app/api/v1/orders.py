import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, get_current_wedding
from app.models.user import User
from app.models.wedding import Wedding
from app.schemas.order import OrderCreate, OrderResponse
from app.services import order as order_service
from app.services import plan as plan_service

router = APIRouter()


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    wedding_id: uuid.UUID,
    data: OrderCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    wedding: Annotated[Wedding, Depends(get_current_wedding)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> OrderResponse:
    plan = await plan_service.get_plan_by_id(db, data.plan_id)
    if plan is None or not plan.is_active:
        raise HTTPException(status_code=400, detail="Invalid or inactive plan")

    if plan.price == 0:
        raise HTTPException(status_code=400, detail="Cannot create order for free plan")

    pending_order = await order_service.get_pending_order_for_wedding(db, wedding_id)
    if pending_order is not None:
        raise HTTPException(status_code=400, detail="You already have a pending order")

    order = await order_service.create_order(db, wedding_id, data, plan.price)
    return order


@router.get("/", response_model=list[OrderResponse])
async def list_orders(
    wedding_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    wedding: Annotated[Wedding, Depends(get_current_wedding)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[OrderResponse]:
    orders = await order_service.list_orders(db, wedding_id)
    return orders


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    wedding_id: uuid.UUID,
    order_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    wedding: Annotated[Wedding, Depends(get_current_wedding)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> OrderResponse:
    order = await order_service.get_order(db, wedding_id, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
