# Admin Panel Superadmin — WePlan (Kanikah)

> Opsi A: admin di dalam repo sama, prefix `/admin/*` dengan layout terpisah.
> Status: approved 2026-09-01. Superadmin awal: `weplansuper@gmail.com`.

## 1. Tujuan
Memberi superadmin kemampuan monitor semua user & workspace dan troubleshoot tanpa `psql` manual: search user/wedding/order, ban/reset password, impersonate read-only, konfirmasi/reject order manual, perpanjang paket, lihat activity log.

## 2. Keputusan yang Dikunci
- **Impersonate**: ya, butuh (short-lived view-as, 10 menit, audit, read-only)
- **Ban user + reset password**: ya (toggle `is_active`, generate reset link 15m)
- **Reject order**: ya (selain confirm, status `cancelled` dengan alasan)
- **Seed superadmin**: `weplansuper@gmail.com` / password env `ADMIN_INITIAL_PASSWORD` atau generate random log di console

## 3. Yang WAJIB Ada vs Tidak Perlu
### Wajib (P0/P1)
- **Dashboard** (`/admin`): KPI total users/weddings/MRR/pending orders/premium ratio, signup 7d.
- **Users** (`/admin/users`): list paginated search email/name, filter is_active/provider/superadmin, detail + weddings + stats + recent activities, aksi ban, reset-password, promote; global search.
- **Weddings** (`/admin/weddings`): list search title/pair_code/partner, filter plan/expired, detail members + counts (guests, checklists %, tx), activities paginated, aksi extend expiry & regenerate pair_code.
- **Orders** (`/admin/orders`): global list pending/confirmed/cancelled, filter/search, detail, confirm (existing) + cancel/reject, manual assign plan.
- **Plans** (`/admin/plans`): list + patch price/duration.
- **Support/Troubleshoot**: global search (email/pair_code/wedding_id/order_id), activity viewer per wedding, admin audit log (reuse `activities` atau tabel baru `admin_audit_logs`).
- **Keamanan**: semua `Depends(get_current_superadmin)` (`backend/app/core/deps.py:85`), frontend guard `middleware/admin.ts`, mask `hashed_password`.

### Tidak Perlu (MVP)
- Edit konten tenant (tamunya/checklistnya) — cukup viewer read-only.
- SQL console, bulk email blast, analytics builder, CMS landing, payment gateway otomasi, RBAC multi-role. Alasan: scope creep & risiko isolasi `wedding_id`.

## 4. Arsitektur
```
backend/app/
  schemas/admin.py
  services/admin.py (+ order reject)
  api/v1/admin/
    __init__.py  router aggregator prefix /admin
    stats.py, users.py, weddings.py, orders.py, plans.py, activities.py
  scripts/create_superadmin.py
frontend/app/
  layouts/admin.vue (sidebar admin, desktop-first)
  middleware/admin.ts
  composables/useAdminApi.ts
  stores/admin.ts (+ auth.is_superadmin)
  pages/admin/index.vue, users/index.vue, users/[id].vue, weddings/..., orders/..., plans.vue
  components/Admin/* (Search, StatCard, Table)
```

## 5. API Contract (semua Bearer superadmin)
```
GET    /api/v1/admin/stats
GET    /api/v1/admin/users?q=&is_active=&is_superadmin=&provider=&page=&limit=
GET    /api/v1/admin/users/{id}
PATCH  /api/v1/admin/users/{id}/status          {is_active}
POST   /api/v1/admin/users/{id}/reset-password   -> {reset_token, reset_link}
POST   /api/v1/admin/users/{id}/impersonate      -> {impersonate_token}
GET    /api/v1/admin/weddings?q=&plan=&expired=&page=&limit=
GET    /api/v1/admin/weddings/{id}
PATCH  /api/v1/admin/weddings/{id}/extend        {days: int}
POST   /api/v1/admin/weddings/{id}/regenerate-code
GET    /api/v1/admin/weddings/{id}/activities?page=&limit=
GET    /api/v1/admin/orders?status=&q=&page=&limit=
PATCH  /api/v1/admin/orders/{id}/confirm         {payment_method, notes}
PATCH  /api/v1/admin/orders/{id}/cancel          {reason}
GET    /api/v1/admin/plans
PATCH  /api/v1/admin/plans/{id}                  {price, max_guests, duration_months}
```

## 6. Phase Implementasi
### Phase 0 — Done (keputusan dikunci)
### Phase 1 — Backend Foundation (1.5 hari)
- schemas/admin.py (Paginated[T], AdminUser*, AdminWedding*, AdminOrder*, StatsResponse)
- services/admin.py (kpi, list users/weddings/orders dengan func.count)
- api/v1/admin/* + router.py prefix /admin (alias kompatibel /admin/orders/{id}/confirm lama)
- order reject: status cancelled, notes, audit
- seed weplansuper@gmail.com via script + alembic data

### Phase 2 — Frontend Shell (1 hari)
- layouts/admin.vue (sidebar Overview/Users/Weddings/Orders/Plans)
- middleware/admin.ts + patch stores/auth.ts (is_superadmin) + composables/useAdminApi.ts
- stores/admin.ts, shell pages admin/index + users + weddings + orders (tabel paginated)

### Phase 3 — Pages Lengkap (2 hari)
- detail drawers, extend/regenerate, confirm/cancel modal, plans edit, chart 7d signup

### Phase 4 — Troubleshoot Extras (0.5 hari)
- global search, impersonate banner, audit viewer

### Phase 5 — QA
- pytest tests/integration/test_admin.py (403/200, pagination)
- npm run build, guard check, seed check

## 7. Risiko & Guard
- Tidak bisa demote diri sendiri, tidak bisa ban diri sendiri.
- Mask password, rate-limit search, audit setiap admin action ke activities/admin_audit_logs.
- Query counts via subquery, avoid N+1.

## 8. File yang Disentuh Phase 1-2
- backend/app/schemas/admin.py (baru)
- backend/app/services/admin.py (baru)
- backend/app/api/v1/admin/* (refactor dari admin.py single file)
- backend/app/api/v1/router.py:26 (prefix)
- backend/app/schemas/user.py / auth.py (expose is_superadmin)
- backend/scripts/create_superadmin.py (baru)
- frontend/app/layouts/admin.vue, middleware/admin.ts, composables/useAdminApi.ts, stores/admin.ts, pages/admin/*
