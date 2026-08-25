# Plan & Order System

Sistem manajemen paket langganan dan pemesanan dengan pembayaran manual untuk MVP.

## Data Models

### Plan Model (`app/models/plan.py`)

```python
class Plan(Base):
    __tablename__ = "plans"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100))
    slug: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    price: Mapped[int] = mapped_column(BigInteger, default=0)
    max_guests: Mapped[int] = mapped_column(Integer, default=50)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow)
```

### Order Model (`app/models/order.py`)

```python
class Order(Base):
    __tablename__ = "orders"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    wedding_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("weddings.id", ondelete="CASCADE"))
    plan_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("plans.id", ondelete="CASCADE"))
    status: Mapped[str] = mapped_column(String(20), default="pending")
    amount: Mapped[int] = mapped_column(BigInteger)
    payment_method: Mapped[str | None] = mapped_column(String(50), nullable=True)
    proof_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    confirmed_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow)
```

### Wedding Model Update

```python
# Tambahkan di wedding.py
plan_id: Mapped[uuid.UUID | None] = mapped_column(
    ForeignKey("plans.id", ondelete="SET NULL"), nullable=True
)
plan: Mapped["Plan | None"] = relationship()
```

### User Model Update

```python
# Tambahkan di user.py
is_superadmin: Mapped[bool] = mapped_column(Boolean, default=False)
```

## API Endpoints

### Plans (Public)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/plans/` | List semua plan aktif |
| GET | `/api/v1/plans/{plan_id}` | Detail plan |

### Orders (Wedding-scoped)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/weddings/{wedding_id}/orders/` | Buat order baru |
| GET | `/api/v1/weddings/{wedding_id}/orders/` | List order history |
| GET | `/api/v1/weddings/{wedding_id}/orders/{order_id}` | Detail order |

### Admin (Superadmin only)

| Method | Path | Description |
|--------|------|-------------|
| PATCH | `/api/v1/admin/orders/{order_id}/confirm` | Konfirmasi pembayaran |

## Business Rules

### Free Plan Flow
- Wedding baru otomatis mendapat Paket Dasar (Gratis)
- Tidak perlu membuat Order record
- `wedding.plan_id` = NULL atau referensi ke plan "basic"

### Premium Plan Flow
1. User pilih plan premium dari dashboard
2. Buat Order dengan status "pending"
3. User upload bukti bayar (proof_url)
4. Admin konfirmasi via PATCH /admin/orders/{id}/confirm
5. Order status berubah ke "confirmed"
6. `wedding.plan_id` diupdate ke plan premium

### Validation Rules
- Tidak bisa buat order untuk free plan (price == 0)
- Tidak bisa buat order jika sudah ada pending order
- Hanya superadmin yang bisa konfirmasi order
- Plan harus aktif (is_active == true) untuk bisa dipesan

## Dependencies

### get_current_superadmin (`app/core/deps.py`)

```python
async def get_current_superadmin(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if not current_user.is_superadmin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user
```

## Seed Data

```python
# plans table initial data
Plan(
    name="Paket Dasar",
    slug="basic",
    price=0,
    max_guests=50,
    is_active=True,
)
Plan(
    name="Paket Lengkap",
    slug="premium",
    price=149000,
    max_guests=999999,
    is_active=True,
)
```

## Dashboard Widget

Widget "Plan Aktif" di dashboard.html menampilkan:
- Nama plan saat ini
- Badge "Gratis" atau "Premium"
- Info batas tamu
- Tombol upgrade (jika masih free)

```html
<!-- Plan Status Widget -->
<div class="bg-white rounded-2xl shadow-sm border border-slate-100 p-6">
    <div class="flex justify-between items-center">
        <div class="flex items-center gap-4">
            <div class="w-12 h-12 bg-gradient-to-br from-rose-400 to-rose-600 rounded-xl flex items-center justify-center">
                <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"></path>
                </svg>
            </div>
            <div>
                <p class="text-slate-500 text-sm font-medium">Plan Aktif</p>
                <h3 class="text-xl font-bold text-slate-800">Paket Dasar <span class="text-slate-400 font-normal text-sm">(Gratis)</span></h3>
            </div>
        </div>
        <button class="bg-rose-600 text-white px-5 py-2.5 rounded-full font-medium text-sm shadow-md shadow-rose-600/20 hover:bg-rose-700 hover:-translate-y-0.5 transition-all">
            Upgrade ke Premium
        </button>
    </div>
</div>
```

## Migration

```bash
alembic revision --autogenerate -m "add plans and orders tables"
alembic upgrade head
```
