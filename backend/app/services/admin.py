"""Admin services — stats, users, weddings, orders."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import (
    create_access_token,
    create_refresh_token,
    create_reset_token,
)
from app.models.order import Order
from app.models.plan import Plan
from app.models.user import User
from app.models.wedding import Wedding
from app.models.wedding_user import WeddingUser
from app.services.auth import generate_pair_code


async def get_admin_stats(db: AsyncSession) -> dict:
    now = datetime.now(UTC).replace(tzinfo=None)
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)

    total_users = await db.scalar(select(func.count()).select_from(User)) or 0
    active_users = (
        await db.scalar(
            select(func.count()).select_from(User).where(User.is_active.is_(True))
        )
        or 0
    )
    total_weddings = await db.scalar(select(func.count()).select_from(Wedding)) or 0
    pending_orders = (
        await db.scalar(
            select(func.count()).select_from(Order).where(Order.status == "pending")
        )
        or 0
    )
    confirmed_orders = (
        await db.scalar(
            select(func.count()).select_from(Order).where(Order.status == "confirmed")
        )
        or 0
    )
    cancelled_orders = (
        await db.scalar(
            select(func.count()).select_from(Order).where(Order.status == "cancelled")
        )
        or 0
    )
    total_revenue = (
        await db.scalar(
            select(func.coalesce(func.sum(Order.amount), 0)).where(
                Order.status == "confirmed"
            )
        )
        or 0
    )
    premium_weddings = (
        await db.scalar(
            select(func.count())
            .select_from(Wedding)
            .where(Wedding.plan_expires_at.is_not(None))
            .where(Wedding.plan_expires_at > now)
        )
        or 0
    )
    gratis_weddings = int(total_weddings) - int(premium_weddings)
    signup_7d = (
        await db.scalar(
            select(func.count()).select_from(User).where(User.created_at >= week_ago)
        )
        or 0
    )
    signup_30d = (
        await db.scalar(
            select(func.count()).select_from(User).where(User.created_at >= month_ago)
        )
        or 0
    )

    return {
        "total_users": int(total_users),
        "active_users": int(active_users),
        "total_weddings": int(total_weddings),
        "pending_orders": int(pending_orders),
        "confirmed_orders": int(confirmed_orders),
        "cancelled_orders": int(cancelled_orders),
        "total_revenue": int(total_revenue),
        "premium_weddings": int(premium_weddings),
        "gratis_weddings": int(gratis_weddings),
        "signup_last_7d": int(signup_7d),
        "signup_last_30d": int(signup_30d),
    }


async def list_users(
    db: AsyncSession,
    q: str | None,
    is_active: bool | None,
    is_superadmin: bool | None,
    provider: str | None,
    page: int,
    limit: int,
) -> tuple[list[User], int]:
    filters = []
    if q:
        like = f"%{q}%"
        filters.append(or_(User.email.ilike(like), User.full_name.ilike(like)))
    if is_active is not None:
        filters.append(User.is_active.is_(is_active))
    if is_superadmin is not None:
        filters.append(User.is_superadmin.is_(is_superadmin))
    if provider:
        filters.append(User.provider == provider)

    where_clause = and_(*filters) if filters else True

    total = (
        await db.scalar(select(func.count()).select_from(User).where(where_clause)) or 0
    )

    offset = (page - 1) * limit
    result = await db.execute(
        select(User)
        .where(where_clause)
        .order_by(User.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    users = list(result.scalars().all())

    # attach wedding_count for each user (single query)
    if users:
        ids = [u.id for u in users]
        counts = await db.execute(
            select(WeddingUser.user_id, func.count(WeddingUser.id))
            .where(WeddingUser.user_id.in_(ids))
            .group_by(WeddingUser.user_id)
        )
        count_map = {row[0]: row[1] for row in counts.all()}
        for u in users:
            # transient attribute for schema
            u.wedding_count = int(count_map.get(u.id, 0))
    else:
        for u in users:
            u.wedding_count = 0

    return users, int(total)


async def get_user_detail(db: AsyncSession, user_id: uuid.UUID) -> User | None:
    user = await db.get(User, user_id)
    if user is None:
        return None
    cnt = await db.scalar(
        select(func.count())
        .select_from(WeddingUser)
        .where(WeddingUser.user_id == user_id)
    )
    user.wedding_count = int(cnt or 0)
    return user


async def list_weddings(
    db: AsyncSession,
    q: str | None,
    plan_slug: str | None,
    expired: bool | None,
    page: int,
    limit: int,
) -> tuple[list[dict], int]:
    # Build base query with join plan for filter
    filters = []
    if q:
        like = f"%{q}%"
        filters.append(
            or_(
                Wedding.title.ilike(like),
                Wedding.pair_code.ilike(like),
                Wedding.partner1_name.ilike(like),
                Wedding.partner2_name.ilike(like),
            )
        )
    if plan_slug:
        # join plan slug
        sub = select(Plan.id).where(Plan.slug == plan_slug)
        # we will filter wedding.plan_id in subquery
        filters.append(Wedding.plan_id.in_(sub))
    now = datetime.now(UTC).replace(tzinfo=None)
    if expired is True:
        filters.append(
            or_(Wedding.plan_expires_at.is_(None), Wedding.plan_expires_at <= now)
        )
    elif expired is False:
        filters.append(Wedding.plan_expires_at > now)

    where_clause = and_(*filters) if filters else True

    total = (
        await db.scalar(select(func.count()).select_from(Wedding).where(where_clause))
        or 0
    )

    offset = (page - 1) * limit
    result = await db.execute(
        select(Wedding)
        .options(selectinload(Wedding.plan))
        .where(where_clause)
        .order_by(Wedding.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    weddings = list(result.scalars().all())

    # enrich with counts
    enriched: list[dict] = []
    for w in weddings:
        member_cnt = (
            await db.scalar(
                select(func.count())
                .select_from(WeddingUser)
                .where(WeddingUser.wedding_id == w.id)
            )
            or 0
        )
        # guest count
        from app.models.guest import Guest

        guest_cnt = (
            await db.scalar(
                select(func.count()).select_from(Guest).where(Guest.wedding_id == w.id)
            )
            or 0
        )
        enriched.append(
            {
                "wedding": w,
                "member_count": int(member_cnt),
                "guest_count": int(guest_cnt),
            }
        )
    return enriched, int(total)


async def get_wedding_detail(db: AsyncSession, wedding_id: uuid.UUID) -> dict | None:
    result = await db.execute(
        select(Wedding)
        .options(selectinload(Wedding.plan))
        .where(Wedding.id == wedding_id)
    )
    wedding = result.scalar_one_or_none()
    if wedding is None:
        return None

    # members
    m_result = await db.execute(
        select(WeddingUser, User)
        .join(User, WeddingUser.user_id == User.id)
        .where(WeddingUser.wedding_id == wedding_id)
    )
    members = []
    for wu, u in m_result.all():
        members.append(
            {
                "user_id": u.id,
                "email": u.email,
                "full_name": u.full_name,
                "role": wu.role,
                "provider": u.provider,
            }
        )
    # counts
    from app.models.guest import Guest
    from app.models.transaction import Transaction
    from app.models.vendor import Vendor

    guest_cnt = (
        await db.scalar(
            select(func.count())
            .select_from(Guest)
            .where(Guest.wedding_id == wedding_id)
        )
        or 0
    )
    vendor_cnt = (
        await db.scalar(
            select(func.count())
            .select_from(Vendor)
            .where(Vendor.wedding_id == wedding_id)
        )
        or 0
    )
    tx_cnt = (
        await db.scalar(
            select(func.count())
            .select_from(Transaction)
            .where(Transaction.wedding_id == wedding_id)
        )
        or 0
    )
    member_cnt = len(members)

    return {
        "wedding": wedding,
        "members": members,
        "member_count": member_cnt,
        "guest_count": int(guest_cnt),
        "vendor_count": int(vendor_cnt),
        "transaction_count": int(tx_cnt),
    }


async def extend_wedding(
    db: AsyncSession, wedding_id: uuid.UUID, days: int
) -> Wedding | None:
    wedding = await db.get(Wedding, wedding_id)
    if wedding is None:
        return None
    now = datetime.now(UTC).replace(tzinfo=None)
    base = (
        wedding.plan_expires_at
        if wedding.plan_expires_at and wedding.plan_expires_at > now
        else now
    )
    wedding.plan_expires_at = base + timedelta(days=days)
    await db.flush()
    await db.refresh(wedding)
    return wedding


async def regenerate_pair_code(
    db: AsyncSession, wedding_id: uuid.UUID
) -> Wedding | None:
    wedding = await db.get(Wedding, wedding_id)
    if wedding is None:
        return None
    # ensure uniqueness retry 5
    for _ in range(5):
        code = generate_pair_code()
        exists = await db.scalar(
            select(func.count()).select_from(Wedding).where(Wedding.pair_code == code)
        )
        if not exists:
            wedding.pair_code = code
            await db.flush()
            await db.refresh(wedding)
            return wedding
    # fallback
    wedding.pair_code = generate_pair_code()
    await db.flush()
    await db.refresh(wedding)
    return wedding


async def list_orders_global(
    db: AsyncSession,
    status: str | None,
    q: str | None,
    page: int,
    limit: int,
) -> tuple[list[dict], int]:
    filters = []
    if status:
        filters.append(Order.status == status)
    # join wedding for q search
    from app.models.wedding import Wedding as W

    # total count with join if needed
    if q:
        like = f"%{q}%"
        # filter where wedding title or pair_code like
        # need subquery for wedding ids matching q
        wedding_ids_sub = select(W.id).where(
            or_(W.title.ilike(like), W.pair_code.ilike(like))
        )
        # also match order id string? skip
        filters.append(Order.wedding_id.in_(wedding_ids_sub))

    where_clause = and_(*filters) if filters else True

    total = (
        await db.scalar(select(func.count()).select_from(Order).where(where_clause))
        or 0
    )

    offset = (page - 1) * limit
    # fetch with wedding and plan
    result = await db.execute(
        select(Order, W, Plan)
        .join(W, Order.wedding_id == W.id, isouter=True)
        .join(Plan, Order.plan_id == Plan.id, isouter=True)
        .where(where_clause)
        .order_by(Order.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    rows = result.all()
    enriched = []
    for order, wedding, plan in rows:
        enriched.append({"order": order, "wedding": wedding, "plan": plan})
    return enriched, int(total)


async def cancel_order(
    db: AsyncSession,
    order_id: uuid.UUID,
    reason: str | None,
) -> Order | None:
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if order is None:
        return None
    if order.status == "cancelled":
        return order
    order.status = "cancelled"
    if reason:
        # append reason to notes
        if order.notes:
            order.notes = f"{order.notes}\n[Cancelled] {reason}"
        else:
            order.notes = f"[Cancelled] {reason}"
    await db.flush()
    await db.refresh(order)
    return order


def generate_impersonate_tokens(target_user_id: uuid.UUID) -> dict:
    # 10 minutes access, 30 min refresh for impersonate session
    access = create_access_token(
        str(target_user_id), expires_delta=timedelta(minutes=10)
    )
    refresh = create_refresh_token(
        str(target_user_id), expires_delta=timedelta(minutes=30)
    )
    return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}


def generate_reset_link_for_user(
    user_id: uuid.UUID, frontend_url: str
) -> tuple[str, str]:
    token = create_reset_token(str(user_id))
    link = f"{frontend_url}/reset-password?token={token}"
    return token, link
