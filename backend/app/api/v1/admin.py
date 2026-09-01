import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.deps import get_current_superadmin
from app.models.plan import Plan
from app.models.user import User
from app.models.wedding import Wedding
from app.schemas.admin import (
    ActivityListResponse,
    AdminOrderListResponse,
    AdminPlanItem,
    AdminStatsResponse,
    AdminUserDetailResponse,
    AdminUserListResponse,
    AdminWeddingDetailResponse,
    AdminWeddingListResponse,
    ImpersonateResponse,
    OrderCancelRequest,
    PlanUpdateRequest,
    ResetPasswordLinkResponse,
    UserStatusUpdate,
    WeddingExtendRequest,
)
from app.schemas.order import OrderConfirm, OrderResponse
from app.schemas.plan import PlanResponse
from app.services import admin as admin_service
from app.services import order as order_service

router = APIRouter()


def _pages(total: int, limit: int) -> int:
    return (total + limit - 1) // limit if limit else 0


# ---- Stats ----
@router.get("/stats", response_model=AdminStatsResponse)
async def get_stats(
    current_user: Annotated[User, Depends(get_current_superadmin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AdminStatsResponse:
    data = await admin_service.get_admin_stats(db)
    return AdminStatsResponse(**data)


# ---- Users ----
@router.get("/users", response_model=AdminUserListResponse)
async def list_users(
    current_user: Annotated[User, Depends(get_current_superadmin)],
    db: Annotated[AsyncSession, Depends(get_db)],
    q: str | None = Query(default=None, max_length=100),
    is_active: bool | None = None,
    is_superadmin: bool | None = None,
    provider: str | None = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
) -> AdminUserListResponse:
    users, total = await admin_service.list_users(
        db, q, is_active, is_superadmin, provider, page, limit
    )
    # Build items
    from app.schemas.admin import AdminUserItem

    data = []
    for u in users:
        data.append(
            AdminUserItem(
                id=u.id,
                email=u.email,
                full_name=u.full_name,
                is_active=u.is_active,
                is_superadmin=u.is_superadmin,
                provider=u.provider,
                avatar_url=u.avatar_url,
                email_verified=u.email_verified,
                created_at=u.created_at,
                updated_at=u.updated_at,
                wedding_count=getattr(u, "wedding_count", 0),
            )
        )
    return AdminUserListResponse(
        data=data,
        meta={
            "total": total,
            "page": page,
            "limit": limit,
            "pages": _pages(total, limit),
        },
    )


@router.get("/users/{user_id}", response_model=AdminUserDetailResponse)
async def get_user_detail(
    user_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_superadmin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AdminUserDetailResponse:
    user = await admin_service.get_user_detail(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    # fetch weddings brief
    from app.models.wedding import Wedding
    from app.models.wedding_user import WeddingUser

    result = await db.execute(
        select(Wedding)
        .join(WeddingUser, WeddingUser.wedding_id == Wedding.id)
        .where(WeddingUser.user_id == user_id)
        .order_by(Wedding.created_at.desc())
    )
    weddings = result.scalars().all()
    briefs = [
        {
            "id": w.id,
            "title": w.title,
            "pair_code": w.pair_code,
            "partner1_name": w.partner1_name,
            "partner2_name": w.partner2_name,
            "plan_expires_at": w.plan_expires_at,
            "created_at": w.created_at,
        }
        for w in weddings
    ]
    return AdminUserDetailResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        is_superadmin=user.is_superadmin,
        provider=user.provider,
        avatar_url=user.avatar_url,
        email_verified=user.email_verified,
        created_at=user.created_at,
        updated_at=user.updated_at,
        wedding_count=getattr(user, "wedding_count", 0),
        weddings=briefs,  # type: ignore[arg-type]
    )


@router.patch("/users/{user_id}/status", response_model=AdminUserDetailResponse)
async def update_user_status(
    user_id: uuid.UUID,
    data: UserStatusUpdate,
    current_user: Annotated[User, Depends(get_current_superadmin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AdminUserDetailResponse:
    if user_id == current_user.id and not data.is_active:
        raise HTTPException(
            status_code=400, detail="Tidak bisa menonaktifkan akun sendiri"
        )
    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = data.is_active
    await db.flush()
    await db.refresh(user)
    # audit
    # log to wedding if user has wedding, else skip
    # we log as system activity via first wedding if exists
    from app.models.wedding_user import WeddingUser
    from app.services.activity import log_activity

    wu = await db.scalar(
        select(WeddingUser).where(WeddingUser.user_id == user_id).limit(1)
    )
    if wu is not None:
        await log_activity(
            db,
            wu.wedding_id,
            current_user,
            "status_changed",
            "wedding",
            user_id,
            f"User {user.email} {'activated' if data.is_active else 'banned'} by admin",
            meta={"target_user": str(user_id), "is_active": data.is_active},
        )
    return await get_user_detail(user_id, current_user, db)  # type: ignore[return-value]


@router.post(
    "/users/{user_id}/reset-password", response_model=ResetPasswordLinkResponse
)
async def admin_reset_password(
    user_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_superadmin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ResetPasswordLinkResponse:
    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    token, link = admin_service.generate_reset_link_for_user(
        user.id, settings.FRONTEND_URL
    )
    return ResetPasswordLinkResponse(
        reset_token=token,
        reset_link=link,
        expires_in_minutes=settings.PASSWORD_RESET_EXPIRE_MINUTES,
    )


@router.post("/users/{user_id}/impersonate", response_model=ImpersonateResponse)
async def impersonate_user(
    user_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_superadmin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ImpersonateResponse:
    if user_id == current_user.id:
        raise HTTPException(
            status_code=400, detail="Tidak perlu impersonate diri sendiri"
        )
    target = await db.get(User, user_id)
    if target is None:
        raise HTTPException(status_code=404, detail="User not found")
    if not target.is_active:
        raise HTTPException(status_code=400, detail="User tidak aktif")
    tokens = admin_service.generate_impersonate_tokens(target.id)
    # audit
    from app.models.wedding_user import WeddingUser

    wu = await db.scalar(
        select(WeddingUser).where(WeddingUser.user_id == target.id).limit(1)
    )
    if wu is not None:
        from app.services.activity import log_activity

        await log_activity(
            db,
            wu.wedding_id,
            current_user,
            "updated",
            "wedding",
            target.id,
            f"Admin impersonate {target.email}",
            meta={"impersonated_user": str(target.id), "admin": str(current_user.id)},
        )
    return ImpersonateResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type="bearer",
        target_user_id=target.id,
        expires_in_minutes=10,
    )


# ---- Weddings ----
@router.get("/weddings", response_model=AdminWeddingListResponse)
async def list_weddings(
    current_user: Annotated[User, Depends(get_current_superadmin)],
    db: Annotated[AsyncSession, Depends(get_db)],
    q: str | None = Query(default=None, max_length=100),
    plan: str | None = Query(default=None, description="plan slug filter"),
    expired: bool | None = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
) -> AdminWeddingListResponse:
    enriched, total = await admin_service.list_weddings(
        db, q, plan, expired, page, limit
    )
    data = []
    for item in enriched:
        w = item["wedding"]
        data.append(
            {
                "id": w.id,
                "title": w.title,
                "wedding_date": w.wedding_date,
                "partner1_name": w.partner1_name,
                "partner2_name": w.partner2_name,
                "total_budget": w.total_budget,
                "pair_code": w.pair_code,
                "plan_id": w.plan_id,
                "plan_name": w.plan.name if w.plan else None,
                "plan_slug": w.plan.slug if w.plan else None,
                "plan_expires_at": w.plan_expires_at,
                "member_count": item["member_count"],
                "guest_count": item["guest_count"],
                "created_at": w.created_at,
                "updated_at": w.updated_at,
            }
        )
    return AdminWeddingListResponse(  # type: ignore[arg-type]
        data=data,
        meta={
            "total": total,
            "page": page,
            "limit": limit,
            "pages": _pages(total, limit),
        },
    )


@router.get("/weddings/{wedding_id}", response_model=AdminWeddingDetailResponse)
async def get_wedding_detail(
    wedding_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_superadmin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AdminWeddingDetailResponse:
    detail = await admin_service.get_wedding_detail(db, wedding_id)
    if detail is None:
        raise HTTPException(status_code=404, detail="Wedding not found")
    w = detail["wedding"]
    return AdminWeddingDetailResponse(
        id=w.id,
        title=w.title,
        wedding_date=w.wedding_date,
        partner1_name=w.partner1_name,
        partner2_name=w.partner2_name,
        total_budget=w.total_budget,
        pair_code=w.pair_code,
        plan_id=w.plan_id,
        plan_name=w.plan.name if w.plan else None,
        plan_slug=w.plan.slug if w.plan else None,
        plan_expires_at=w.plan_expires_at,
        member_count=detail["member_count"],
        guest_count=detail["guest_count"],
        created_at=w.created_at,
        updated_at=w.updated_at,
        members=detail["members"],  # type: ignore[arg-type]
        vendor_count=detail["vendor_count"],
        transaction_count=detail["transaction_count"],
    )


@router.patch(
    "/weddings/{wedding_id}/extend", response_model=AdminWeddingDetailResponse
)
async def extend_wedding(
    wedding_id: uuid.UUID,
    data: WeddingExtendRequest,
    current_user: Annotated[User, Depends(get_current_superadmin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AdminWeddingDetailResponse:
    wedding = await admin_service.extend_wedding(db, wedding_id, data.days)
    if wedding is None:
        raise HTTPException(status_code=404, detail="Wedding not found")
    from app.services.activity import log_activity

    await log_activity(
        db,
        wedding.id,
        current_user,
        "status_changed",
        "wedding",
        wedding.id,
        f"Admin extend {data.days} hari",
        meta={"days": data.days, "new_expires": str(wedding.plan_expires_at)},
    )
    return await get_wedding_detail(wedding_id, current_user, db)  # type: ignore[return-value]


@router.post(
    "/weddings/{wedding_id}/regenerate-code", response_model=AdminWeddingDetailResponse
)
async def regenerate_code(
    wedding_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_superadmin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AdminWeddingDetailResponse:
    wedding = await admin_service.regenerate_pair_code(db, wedding_id)
    if wedding is None:
        raise HTTPException(status_code=404, detail="Wedding not found")
    from app.services.activity import log_activity

    await log_activity(
        db,
        wedding.id,
        current_user,
        "updated",
        "wedding",
        wedding.id,
        f"Admin regenerate pair_code {wedding.pair_code}",
        meta={"pair_code": wedding.pair_code},
    )
    return await get_wedding_detail(wedding_id, current_user, db)  # type: ignore[return-value]


@router.get("/weddings/{wedding_id}/activities", response_model=ActivityListResponse)
async def list_wedding_activities(
    wedding_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_superadmin)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
) -> ActivityListResponse:
    # verify wedding exists
    wedding = await db.get(Wedding, wedding_id)
    if wedding is None:
        raise HTTPException(status_code=404, detail="Wedding not found")
    from app.models.activity import Activity

    total = (
        await db.scalar(
            select(func.count())
            .select_from(Activity)
            .where(Activity.wedding_id == wedding_id)
        )
        or 0
    )
    offset = (page - 1) * limit
    result = await db.execute(
        select(Activity)
        .where(Activity.wedding_id == wedding_id)
        .order_by(Activity.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    items = list(result.scalars().all())
    # map meta_data -> meta for schema
    data = []
    for a in items:
        data.append(
            {
                "id": a.id,
                "wedding_id": a.wedding_id,
                "actor_user_id": a.actor_user_id,
                "action": a.action,
                "entity_type": a.entity_type,
                "entity_id": a.entity_id,
                "title": a.title,
                "meta": a.meta_data,
                "created_at": a.created_at,
            }
        )
    return ActivityListResponse(  # type: ignore[arg-type]
        data=data,
        meta={
            "total": int(total),
            "page": page,
            "limit": limit,
            "pages": _pages(int(total), limit),
        },
    )


# ---- Orders (global) ----
@router.get("/orders", response_model=AdminOrderListResponse)
async def list_orders_global(
    current_user: Annotated[User, Depends(get_current_superadmin)],
    db: Annotated[AsyncSession, Depends(get_db)],
    status: str | None = Query(default=None, description="pending/confirmed/cancelled"),
    q: str | None = Query(default=None, max_length=100),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
) -> AdminOrderListResponse:
    enriched, total = await admin_service.list_orders_global(db, status, q, page, limit)
    data = []
    for item in enriched:
        o = item["order"]
        w = item["wedding"]
        p = item["plan"]
        data.append(
            {
                "id": o.id,
                "wedding_id": o.wedding_id,
                "wedding_title": w.title if w else None,
                "plan_id": o.plan_id,
                "plan_name": p.name if p else None,
                "status": o.status,
                "amount": o.amount,
                "payment_method": o.payment_method,
                "notes": o.notes,
                "confirmed_by": o.confirmed_by,
                "confirmed_at": o.confirmed_at,
                "expires_at": o.expires_at,
                "created_at": o.created_at,
                "updated_at": o.updated_at,
            }
        )
    return AdminOrderListResponse(  # type: ignore[arg-type]
        data=data,
        meta={
            "total": total,
            "page": page,
            "limit": limit,
            "pages": _pages(total, limit),
        },
    )


@router.patch("/orders/{order_id}/confirm", response_model=OrderResponse)
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
    from app.services.activity import log_activity

    await log_activity(
        db,
        order.wedding_id,
        current_user,
        "status_changed",
        "order",
        order.id,
        f"Order Premium Rp {order.amount:,}",
        meta={"from": "pending", "to": "confirmed"},
    )
    return order


@router.patch("/orders/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order(
    order_id: uuid.UUID,
    data: OrderCancelRequest,
    current_user: Annotated[User, Depends(get_current_superadmin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> OrderResponse:
    order = await admin_service.cancel_order(db, order_id, data.reason)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    from app.services.activity import log_activity

    await log_activity(
        db,
        order.wedding_id,
        current_user,
        "status_changed",
        "order",
        order.id,
        f"Order cancelled Rp {order.amount:,}",
        meta={"from": "pending", "to": "cancelled", "reason": data.reason},
    )
    return order  # type: ignore[return-value]


# ---- Plans ----
@router.get("/plans", response_model=list[AdminPlanItem])
async def list_plans_admin(
    current_user: Annotated[User, Depends(get_current_superadmin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[AdminPlanItem]:
    result = await db.execute(select(Plan).order_by(Plan.price.asc()))
    plans = list(result.scalars().all())
    return plans  # type: ignore[return-value]


@router.patch("/plans/{plan_id}", response_model=PlanResponse)
async def update_plan(
    plan_id: uuid.UUID,
    data: PlanUpdateRequest,
    current_user: Annotated[User, Depends(get_current_superadmin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PlanResponse:
    plan = await db.get(Plan, plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="Plan not found")
    update = data.model_dump(exclude_unset=True)
    for k, v in update.items():
        setattr(plan, k, v)
    await db.flush()
    await db.refresh(plan)
    return plan  # type: ignore[return-value]


# ---- Backwards compat: keep old path PATCH /admin/orders/{id}/confirm ----
# The new path is /admin/orders/{id}/confirm as above.
# When router prefix is /admin, old clients calling /admin/orders/{id}/confirm still work.
# No extra alias needed.
