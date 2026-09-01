"""Schemas for admin panel."""

from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class PaginationMeta(BaseModel):
    total: int
    page: int
    limit: int
    pages: int


class SignupDailyItem(BaseModel):
    date: str
    count: int


class AdminStatsResponse(BaseModel):
    total_users: int
    active_users: int
    total_weddings: int
    pending_orders: int
    confirmed_orders: int
    cancelled_orders: int
    total_revenue: int
    premium_weddings: int
    gratis_weddings: int
    signup_last_7d: int
    signup_last_30d: int
    signup_daily: list[SignupDailyItem] = Field(default_factory=list)


class AdminUserItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    full_name: str
    is_active: bool
    is_superadmin: bool
    provider: str
    avatar_url: str | None = None
    email_verified: bool
    created_at: datetime
    updated_at: datetime
    wedding_count: int = 0


class AdminUserListResponse(BaseModel):
    data: list[AdminUserItem]
    meta: PaginationMeta


class AdminUserDetailResponse(AdminUserItem):
    weddings: list[AdminWeddingBrief] = Field(default_factory=list)


class AdminWeddingBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    pair_code: str
    partner1_name: str
    partner2_name: str
    plan_expires_at: datetime | None = None
    created_at: datetime


class AdminWeddingItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    wedding_date: date | None = None
    partner1_name: str
    partner2_name: str
    total_budget: int | None = None
    pair_code: str
    plan_id: uuid.UUID | None = None
    plan_name: str | None = None
    plan_slug: str | None = None
    plan_expires_at: datetime | None = None
    member_count: int = 0
    guest_count: int = 0
    created_at: datetime
    updated_at: datetime


class AdminWeddingListResponse(BaseModel):
    data: list[AdminWeddingItem]
    meta: PaginationMeta


class AdminWeddingMember(BaseModel):
    user_id: uuid.UUID
    email: str
    full_name: str
    role: str
    provider: str


class AdminWeddingDetailResponse(AdminWeddingItem):
    members: list[AdminWeddingMember] = Field(default_factory=list)
    guest_count: int = 0
    vendor_count: int = 0
    transaction_count: int = 0


class UserStatusUpdate(BaseModel):
    is_active: bool


class WeddingExtendRequest(BaseModel):
    days: int = Field(ge=1, le=3650, description="Days to extend, 1-3650")


class OrderCancelRequest(BaseModel):
    reason: str | None = Field(default=None, max_length=500)


class PlanCreateRequest(BaseModel):
    name: str = Field(max_length=100)
    slug: str = Field(max_length=50, pattern=r"^[a-z0-9-]+$")
    price: int = Field(ge=0)
    max_guests: int = Field(ge=1)
    duration_months: int = Field(ge=0)
    is_active: bool = True


class PlanUpdateRequest(BaseModel):
    name: str | None = Field(default=None, max_length=100)
    price: int | None = Field(default=None, ge=0)
    max_guests: int | None = Field(default=None, ge=1)
    duration_months: int | None = Field(default=None, ge=0)
    is_active: bool | None = None


class ImpersonateResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    target_user_id: uuid.UUID
    expires_in_minutes: int = 10


class ResetPasswordLinkResponse(BaseModel):
    reset_token: str
    reset_link: str
    expires_in_minutes: int = 15


class AdminOrderItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    wedding_id: uuid.UUID
    wedding_title: str | None = None
    plan_id: uuid.UUID
    plan_name: str | None = None
    status: str
    amount: int
    payment_method: str | None = None
    notes: str | None = None
    confirmed_by: uuid.UUID | None = None
    confirmed_at: datetime | None = None
    expires_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class AdminOrderListResponse(BaseModel):
    data: list[AdminOrderItem]
    meta: PaginationMeta


class AdminPlanItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    price: int
    max_guests: int
    duration_months: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ActivityItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    wedding_id: uuid.UUID
    actor_user_id: uuid.UUID | None = None
    action: str
    entity_type: str
    entity_id: uuid.UUID | None = None
    title: str
    meta_data: dict | None = Field(default=None, alias="meta")
    created_at: datetime


class ActivityListResponse(BaseModel):
    data: list[ActivityItem]
    meta: PaginationMeta
