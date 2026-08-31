"""Analytics aggregators (read-only)."""

from collections import defaultdict
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.checklist import Checklist
from app.models.guest import Guest
from app.models.kua_document import KuaDocument
from app.models.mahar_item import MaharItem
from app.models.transaction import Transaction
from app.models.vendor import Vendor
from app.models.wedding import Wedding
from app.schemas.analytics import (
    AssigneeBreakdown,
    CategoryBreakdown,
    ChecklistAnalyticsResponse,
    ChecklistStatusBreakdown,
    FinanceAnalyticsResponse,
    FinanceKPI,
    GuestAnalyticsResponse,
    KuaProgress,
    MaharVariance,
    MonthlyCashflow,
    RsvpBreakdown,
    SideBreakdown,
    VendorStatusBreakdown,
)


def _pct(part: int, total: int) -> float:
    if total == 0:
        return 0.0
    return round(part / total * 100, 2)


async def get_finance_analytics(
    db: AsyncSession, wedding: Wedding
) -> FinanceAnalyticsResponse:
    wedding_id = wedding.id

    # KPI totals
    masuk_res = await db.execute(
        select(func.coalesce(func.sum(Transaction.amount), 0)).where(
            Transaction.wedding_id == wedding_id, Transaction.type == "masuk"
        )
    )
    keluar_res = await db.execute(
        select(func.coalesce(func.sum(Transaction.amount), 0)).where(
            Transaction.wedding_id == wedding_id, Transaction.type == "keluar"
        )
    )
    total_masuk: int = int(masuk_res.scalar() or 0)
    total_keluar: int = int(keluar_res.scalar() or 0)
    saldo = total_masuk - total_keluar

    target_amount = wedding.total_budget or 0
    progress_pct = round(saldo / target_amount * 100, 2) if target_amount > 0 else 0.0

    # avg keluar per month & burn rate: need earliest transaction date
    first_txn_res = await db.execute(
        select(func.min(Transaction.transaction_date)).where(
            Transaction.wedding_id == wedding_id
        )
    )
    first_date = first_txn_res.scalar()
    avg_keluar_per_month = 0.0
    burn_rate_per_day = 0.0
    forecast_days = None
    if first_date and total_keluar > 0:
        # use created window vs now
        days_span = (date.today() - first_date).days + 1
        days_span = max(days_span, 1)
        months_span = max(days_span / 30.44, 1)
        avg_keluar_per_month = round(total_keluar / months_span, 2)
        burn_rate_per_day = round(total_keluar / days_span, 2)
        if burn_rate_per_day > 0 and saldo > 0:
            forecast_days = int(saldo // burn_rate_per_day)
        elif saldo <= 0:
            forecast_days = 0

    days_until = None
    if wedding.wedding_date:
        diff = (wedding.wedding_date - date.today()).days
        days_until = diff if diff > 0 else 0

    # by_category (keluar per category) — group query
    cat_rows = await db.execute(
        select(Transaction.category, func.sum(Transaction.amount))
        .where(Transaction.wedding_id == wedding_id, Transaction.type == "keluar")
        .group_by(Transaction.category)
    )
    cat_list: list[CategoryBreakdown] = []
    for cat, amt in cat_rows.all():
        amt_i = int(amt or 0)
        cat_list.append(
            CategoryBreakdown(
                category=cat or "lainnya",
                amount=amt_i,
                pct=round(amt_i / total_keluar * 100, 2) if total_keluar else 0.0,
            )
        )
    cat_list.sort(key=lambda x: x.amount or 0, reverse=True)

    # vendor by status
    vendor_rows = await db.execute(
        select(
            Vendor.status,
            func.count(Vendor.id),
            func.coalesce(func.sum(Vendor.total_amount), 0),
        )
        .where(Vendor.wedding_id == wedding_id)
        .group_by(Vendor.status)
    )
    vendor_by_status = [
        VendorStatusBreakdown(status=s, count=int(c), amount=int(a or 0))
        for s, c, a in vendor_rows.all()
    ]
    # Ensure 3 buckets present
    present = {v.status for v in vendor_by_status}
    for s in ("belum_bayar", "dp", "lunas"):
        if s not in present:
            vendor_by_status.append(VendorStatusBreakdown(status=s, count=0, amount=0))
    vendor_by_status.sort(key=lambda x: x.status)

    overdue_res = await db.execute(
        select(func.count(Vendor.id)).where(
            Vendor.wedding_id == wedding_id,
            Vendor.due_date.isnot(None),
            Vendor.due_date < date.today(),
            Vendor.status != "lunas",
        )
    )
    overdue = int(overdue_res.scalar() or 0)

    # mahar variance per type
    mahar_rows = await db.execute(
        select(
            MaharItem.type,
            func.count(MaharItem.id),
            func.coalesce(func.sum(MaharItem.estimated_cost), 0),
            func.coalesce(func.sum(MaharItem.actual_cost), 0),
        )
        .where(MaharItem.wedding_id == wedding_id)
        .group_by(MaharItem.type)
    )
    mahar_variance = []
    for t, c, est, act in mahar_rows.all():
        est_i, act_i = int(est or 0), int(act or 0)
        mahar_variance.append(
            MaharVariance(
                type=t,
                count=int(c),
                estimated=est_i,
                actual=act_i,
                variance=act_i - est_i,
            )
        )

    # monthly cashflow: last 12 months inclusive by transaction_date
    # if wedding has created_at use it else 12 months window ending today
    # strategy: aggregate all transactions by YYYY-MM
    all_txns = await db.execute(
        select(
            Transaction.type, Transaction.amount, Transaction.transaction_date
        ).where(Transaction.wedding_id == wedding_id)
    )
    bucket: dict[str, dict[str, int]] = defaultdict(lambda: {"masuk": 0, "keluar": 0})
    for typ, amt, d in all_txns.all():
        if d is None:
            continue
        key = d.strftime("%Y-%m")
        bucket[key][typ] = bucket[key].get(typ, 0) + int(amt)

    # Build continuous 12-month keys from wedding.created_at month or today-11
    if wedding.created_at:
        start = wedding.created_at.date().replace(day=1)
    else:
        today_first = date.today().replace(day=1)
        # go back 11 months
        year = today_first.year
        month = today_first.month - 11
        while month <= 0:
            month += 12
            year -= 1
        start = date(year, month, 1)

    # generate 12 month keys forward from start
    month_keys: list[str] = []
    y, m = start.year, start.month
    for _ in range(12):
        month_keys.append(f"{y:04d}-{m:02d}")
        m += 1
        if m > 12:
            m = 1
            y += 1

    monthly: list[MonthlyCashflow] = []
    running_saldo = 0  # not cumulative across all history — per-month saldo
    for k in month_keys:
        vals = bucket.get(k, {"masuk": 0, "keluar": 0})
        masuk = vals.get("masuk", 0)
        keluar = vals.get("keluar", 0)
        running_saldo = (
            masuk - keluar
        )  # per-month saldo; if muốn cumulative use running sum
        monthly.append(
            MonthlyCashflow(month=k, masuk=masuk, keluar=keluar, saldo=running_saldo)
        )

    kpi = FinanceKPI(
        total_masuk=total_masuk,
        total_keluar=total_keluar,
        saldo=saldo,
        target_amount=target_amount,
        progress_pct=progress_pct,
        avg_keluar_per_month=avg_keluar_per_month,
        burn_rate_per_day=burn_rate_per_day,
        forecast_days_remaining=forecast_days,
        days_until_wedding=days_until,
    )
    return FinanceAnalyticsResponse(
        kpi=kpi,
        by_category=cat_list,
        vendor_by_status=vendor_by_status,
        vendor_overdue_count=overdue,
        mahar_variance=mahar_variance,
        monthly=monthly,
    )


async def get_guest_analytics(
    db: AsyncSession, wedding: Wedding
) -> GuestAnalyticsResponse:
    wedding_id = wedding.id
    total_res = await db.execute(
        select(func.count(Guest.id)).where(Guest.wedding_id == wedding_id)
    )
    total = int(total_res.scalar() or 0)

    # by rsvp
    rsvp_rows = await db.execute(
        select(Guest.rsvp_status, func.count(Guest.id))
        .where(Guest.wedding_id == wedding_id)
        .group_by(Guest.rsvp_status)
    )
    rsvp_map = {r: int(c) for r, c in rsvp_rows.all()}
    by_rsvp = [
        RsvpBreakdown(
            status=s, count=rsvp_map.get(s, 0), pct=_pct(rsvp_map.get(s, 0), total)
        )
        for s in ("pending", "attending", "declined")
    ]

    side_rows = await db.execute(
        select(Guest.side, func.count(Guest.id))
        .where(Guest.wedding_id == wedding_id)
        .group_by(Guest.side)
    )
    side_map = {r: int(c) for r, c in side_rows.all()}
    by_side = [
        SideBreakdown(
            side=s, count=side_map.get(s, 0), pct=_pct(side_map.get(s, 0), total)
        )
        for s in ("bride", "groom", "both")
    ]

    cat_rows = await db.execute(
        select(Guest.category, func.count(Guest.id))
        .where(Guest.wedding_id == wedding_id)
        .group_by(Guest.category)
    )
    by_category = [
        CategoryBreakdown(
            category=cat or "general", count=int(c), pct=_pct(int(c), total)
        )
        for cat, c in cat_rows.all()
    ]
    by_category.sort(key=lambda x: x.count or 0, reverse=True)

    max_guests = None
    if wedding.plan and hasattr(wedding.plan, "max_guests"):
        max_guests = wedding.plan.max_guests

    return GuestAnalyticsResponse(
        total=total,
        max_guests=max_guests,
        headcount_pax=total,
        by_rsvp=by_rsvp,
        by_side=by_side,
        by_category=by_category,
    )


async def get_checklist_analytics(
    db: AsyncSession, wedding: Wedding
) -> ChecklistAnalyticsResponse:
    wedding_id = wedding.id
    total_res = await db.execute(
        select(func.count(Checklist.id)).where(Checklist.wedding_id == wedding_id)
    )
    total = int(total_res.scalar() or 0)

    # by status
    status_rows = await db.execute(
        select(Checklist.status, func.count(Checklist.id))
        .where(Checklist.wedding_id == wedding_id)
        .group_by(Checklist.status)
    )
    status_map = {r: int(c) for r, c in status_rows.all()}
    by_status = [
        ChecklistStatusBreakdown(
            status=s, count=status_map.get(s, 0), pct=_pct(status_map.get(s, 0), total)
        )
        for s in ("todo", "in_progress", "done")
    ]
    # normalize: include any other status values that exist (e.g., legacy)
    for k, v in status_map.items():
        if k not in ("todo", "in_progress", "done"):
            by_status.append(
                ChecklistStatusBreakdown(status=k, count=v, pct=_pct(v, total))
            )

    progress_pct = _pct(status_map.get("done", 0), total)

    cat_rows = await db.execute(
        select(Checklist.category, func.count(Checklist.id))
        .where(Checklist.wedding_id == wedding_id)
        .group_by(Checklist.category)
    )
    by_category = [
        CategoryBreakdown(
            category=cat or "lainnya", count=int(c), pct=_pct(int(c), total)
        )
        for cat, c in cat_rows.all()
    ]
    by_category.sort(key=lambda x: x.count or 0, reverse=True)

    # by assignee: group by assignee_id (null vs uuid)
    assignee_rows = await db.execute(
        select(Checklist.assignee_id, func.count(Checklist.id))
        .where(Checklist.wedding_id == wedding_id)
        .group_by(Checklist.assignee_id)
    )
    # We'll produce both/unassigned aggregate; frontend can label
    assignee_map: dict[str, int] = {}
    for aid, c in assignee_rows.all():
        key = "unassigned" if aid is None else str(aid)
        assignee_map[key] = int(c)
    # generic breakdown by assignee_id
    by_assignee = [
        AssigneeBreakdown(assignee=k, count=v, pct=_pct(v, total))
        for k, v in assignee_map.items()
    ]
    # If no distribution, provide both placeholder 0
    if not by_assignee and total == 0:
        by_assignee = []

    overdue_res = await db.execute(
        select(func.count(Checklist.id)).where(
            Checklist.wedding_id == wedding_id,
            Checklist.due_date.isnot(None),
            Checklist.due_date < date.today(),
            Checklist.status != "done",
        )
    )
    overdue = int(overdue_res.scalar() or 0)

    # KUA progress
    kua_total_res = await db.execute(
        select(func.count(KuaDocument.id)).where(KuaDocument.wedding_id == wedding_id)
    )
    kua_total = int(kua_total_res.scalar() or 0)
    kua_done_res = await db.execute(
        select(func.count(KuaDocument.id)).where(
            KuaDocument.wedding_id == wedding_id,
            KuaDocument.status.in_(["selesai", "diverifikasi", "sudah"]),
        )
    )
    kua_done = int(kua_done_res.scalar() or 0)
    kua = KuaProgress(total=kua_total, done=kua_done, pct=_pct(kua_done, kua_total))

    return ChecklistAnalyticsResponse(
        total=total,
        progress_pct=progress_pct,
        by_status=by_status,
        by_category=by_category,
        by_assignee=by_assignee,
        overdue_count=overdue,
        kua=kua,
    )
