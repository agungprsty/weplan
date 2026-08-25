import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_superadmin
from app.models.user import User
from app.schemas.order import OrderConfirm, OrderResponse
from app.services import order as order_service

router = APIRouter()


@router.patch("/{order_id}/confirm", response_model=OrderResponse)
async def confirm_order(
    order_id: uuid.UUID,
    data: OrderConfirm,
    current_user: Annotated[User, Depends(get_current_superadmin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> OrderResponse:
    order = await order_service.confirm_order(
        db,
        order_id,
        current_user.id,
        data.payment_method,
        data.notes,
    )
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
