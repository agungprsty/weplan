"""Pydantic schemas for analytics / laporan endpoints."""

from pydantic import BaseModel


class CategoryBreakdown(BaseModel):
    category: str
    count: int | None = None
    amount: int | None = None
    pct: float | None = None


class MonthlyCashflow(BaseModel):
    month: str  # YYYY-MM
    masuk: int
    keluar: int
    saldo: int


class FinanceKPI(BaseModel):
    total_masuk: int
    total_keluar: int
    saldo: int
    target_amount: int
    progress_pct: float
    avg_keluar_per_month: float
    burn_rate_per_day: float
    forecast_days_remaining: int | None  # None jika tidak ada pengeluaran
    days_until_wedding: int | None


class VendorStatusBreakdown(BaseModel):
    status: str  # belum_bayar / dp / lunas
    count: int
    amount: int


class MaharVariance(BaseModel):
    type: str  # mahar / seserahan_cpp / seserahan_cpw / hantaran
    count: int
    estimated: int
    actual: int
    variance: int  # actual - estimated


class FinanceAnalyticsResponse(BaseModel):
    kpi: FinanceKPI
    by_category: list[CategoryBreakdown]  # pengeluaran (keluar) per category
    vendor_by_status: list[VendorStatusBreakdown]
    vendor_overdue_count: int
    mahar_variance: list[MaharVariance]
    monthly: list[MonthlyCashflow]


class RsvpBreakdown(BaseModel):
    status: str  # pending / attending / declined
    count: int
    pct: float


class SideBreakdown(BaseModel):
    side: str  # bride / groom / both
    count: int
    pct: float


class GuestAnalyticsResponse(BaseModel):
    total: int
    max_guests: int | None
    headcount_pax: int  # approximated as total guests (pax not stored, use total)
    by_rsvp: list[RsvpBreakdown]
    by_side: list[SideBreakdown]
    by_category: list[CategoryBreakdown]


class ChecklistStatusBreakdown(BaseModel):
    status: str  # todo / in_progress / done
    count: int
    pct: float


class AssigneeBreakdown(BaseModel):
    assignee: str  # pria / wanita / both / unassigned
    count: int
    pct: float


class KuaProgress(BaseModel):
    total: int
    done: int  # status selesai / diverifikasi
    pct: float


class ChecklistAnalyticsResponse(BaseModel):
    total: int
    progress_pct: float
    by_status: list[ChecklistStatusBreakdown]
    by_category: list[CategoryBreakdown]
    by_assignee: list[AssigneeBreakdown]
    overdue_count: int
    kua: KuaProgress
