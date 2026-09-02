# Code Review Mendalam — WePlan (Kanikah) Wedding SaaS

> **Peran:** Senior Dev Reviewer | **Fokus:** Security, Performance, Maintainability, Best Practice FastAPI & Nuxt 3  
> **Tanggal:** 2 Sep 2026 | **Scope:** `backend/` (FastAPI + SQLAlchemy async) & `frontend/` (Nuxt 4.5 + Pinia)  
> **Reviewer:** muse-spark-1.2 (Automated Deep Scan)

---

## Daftar Isi

1. [Executive Summary & Skor](#1-executive-summary--skor)
2. [Yang Sudah Bagus](#2-yang-sudah-bagus-patut-dipertahankan)
3. [CRITICAL — Wajib Fix Sebelum Production](#3--critical--wajib-fix-sebelum-production)
4. [HIGH — Security & Correctness](#4--high--security--correctness)
5. [MEDIUM — Performance & Maintainability](#5--medium--performance--maintainability)
6. [Checklist Best Practice FastAPI & Nuxt](#6-checklist-best-practice)
7. [To-Do Prioritas](#7-to-do-prioritas)
8. [Catatan Mobile-First](#8-catatan-mobile-first)
9. [Lampiran — File yang Diperiksa](#9-lampiran--file-yang-diperiksa)

---

## 1. Executive Summary & Skor

| Area | Skor | Catatan |
| :--- | :---: | :--- |
| **Backend - Architecture** | 7.5/10 | Struktur `models/schemas/api/services/core` sudah rapi, DI FastAPI dipakai konsisten |
| **Backend - Security** | **4.0/10** | 🔴 Kritis: secret bocor di git, auth stateless tanpa revoke, CORS + localStorage XSS |
| **Backend - Performance** | 5.5/10 | NullPool mematikan pooling, N+1 masih ada, list tanpa pagination |
| **Backend - Maintainability** | 7.0/10 | Type hint + ruff bagus, tapi bisnis logic bocor ke router |
| **Frontend - Architecture** | 6.5/10 | Pinia + Optimistic UI sudah benar, tapi SSR/hydration & auth fragile |
| **Frontend - Security** | 4.5/10 | Token di `localStorage` + tidak ada CSRF/SEC headers |
| **Frontend - Performance** | 6.0/10 | Chunk split bagus, tapi `useApi()` di-init salah, 6 request parallel di dashboard tanpa debounce |
| **Frontend - Maintainability** | 5.5/10 | TS strict tidak aktif, tidak ada `eslint`, `useRoute` di composable client-only |

**Kesimpulan:** Functional MVP sudah solid, tapi **BELUM production-ready**. 2 temuan `CRITICAL` harus difix sebelum deploy.

---

## 2. Yang Sudah Bagus (Patut Dipertahankan)

### Backend

* `app/main.py` pakai `lifespan` + `await engine.dispose()` — best practice FastAPI async.
* `core/deps.py: get_current_wedding` isolasi multi-tenant `WeddingUser` → 403 jika bukan member, konsisten di semua `weddings/{id}/*`. Ini paling penting.
* `core/security.py` pakai `pwdlib[argon2]` (bukan bcrypt legacy) + `type: access/refresh/reset` di JWT claim — benar.
* `models/base.py` pakai `DeclarativeBase` SA 2.0 + `Mapped` + `utcnow()` naive UTC konsisten.
* `services/activity.py` central `log_activity` + `StrEnum` di `core/enums.py` — single source, bagus.
* `services/guest.py:list_guests` 2 query (guest + gift aggregate) lalu merge di Python, hindari N+1. Good.
* `ruff` config target 88, `E/W/F/I/B/C4/UP` aktif, `pyproject.toml` rapi. `ruff check` sisa 9x E501 saja.

### Frontend

* `stores/guest.ts` & `stores/checklist.ts` **Optimistic UI benar**: `crypto.randomUUID()` → `unshift` → `try { real } catch { rollback }`. Sesuai `AGENTS.md` pattern.
* `composables/useApi.ts` sudah `single-flight` refresh via `refreshing: Promise` + `_retry` guard + jangan retry `/auth/refresh`. Ini anti race-condition.
* `nuxt.config.ts` `manualChunks: chart/export/pinia` + `Cross-Origin-Opener-Policy` untuk Google GIS. Thoughtful.
* `middleware/auth.global.ts` `if (!to.matched.length) throw 404` tidak redirect ke login — best practice.
* `app/dashboard.vue` cek `isPremium` gating + `Promise.allSettled` single-flight `fetchedFor` — performa aware.
* `layouts/dashboard.vue` mobile-first: sidebar `w-[280px] → lg:w-[72px]` + backdrop blur + `isImpersonating ? top-9` — rapi.

---

## 3. 🔴 CRITICAL — Wajib Fix Sebelum Production

### C1. Secret Bocor di Git

**File:** `backend/.env` (ter-commit), `docker-compose.yml:29`, `frontend/.env`

```ini
JWT_SECRET_KEY="dev-secret-key-change-in-production"
GOOGLE_CLIENT_SECRET="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"
NUXT_PUBLIC_GOOGLE_CLIENT_ID=7488169...
```

* `.env` ada di git history, `docker-compose.yml` hardcode `dev-secret`. Siapapun `git log` bisa forge JWT.
* **Impact:** Full account takeover.
* **Fix:**
  1. `git rm --cached backend/.env frontend/.env` + tambah ke `.gitignore`
  2. Rotate `GOOGLE_CLIENT_SECRET` di console Google Cloud segera
  3. `backend/app/core/config.py` tambah validasi:
     ```python
     @field_validator("JWT_SECRET_KEY")
     def check_len(cls, v): 
         assert len(v) >= 32
         return v
     ```
  4. Production pakai `env_file` + Docker secrets / Vault, jangan hardcode di `compose`.

### C2. Token di `localStorage` + XSS = Full Hijack

**File:** `frontend/app/stores/auth.ts:37-39`, `composables/useApi.ts:10`

```ts
localStorage.setItem('kanikah_token', nextToken)
headers.set('Authorization', `Bearer ${auth.token}`)
```

* SPA simpan `access+refresh` di localStorage. Sekali ada XSS (misal `v-html` notes tamu), attacker curi token.
* `onResponseError` pakai `useRoute()` di dalam `onResponseError` (bisa dipanggil SSR) — fragile.
* **Best Practice Nuxt:** HttpOnly cookie `Secure + SameSite=Lax` via `useCookie()` + `nitro` `setCookie`. Jika mau tetap SPA, minimal tambah CSP + `sanitize` input, tapi cookie tetap rekomendasi.
* **Fix short-term:** Tambah `Content-Security-Policy` & `X-Frame-Options` di `nuxt.config: nitro.routeRules`, sanitize `guest.notes`.

### C3. CORS Misconfig + Kredensial

**File:** `backend/app/main.py:43-51`

```python
allow_headers=["*"], expose_headers=["*"], allow_credentials=True
allow_origin_regex = r"https?://(localhost|...|192.168...)(:\d+)?"
```

* `expose_headers=["*"]` invalid spec, `allow_headers=["*"]` + `allow_credentials=True` dilarang browser (harusnya explicit list: `Authorization, Content-Type`). Regex izinkan LAN IP any port = dev only, harus mati di prod.
* **Fix:** `expose_headers=["X-Total-Count"]`, `allow_headers=["Authorization","Content-Type"]`, matikan regex jika `ENV=production`.

---

## 4. 🟠 HIGH — Security & Correctness

| # | File | Temuan | Dampak | Fix |
|---|---|---|---|---|
| **H1** | `core/database.py:12` | `poolclass=NullPool` | Setiap request buat koneksi baru, bunuh performa Postgres (latency + max 100 conn). | Hapus `NullPool`, pakai `AsyncEngine` default `QueuePool(pool_size=10, max_overflow=20)`. `NullPool` hanya untuk `pytest`/`aiosqlite`. |
| **H2** | `core/database.py:25-33` | `get_db()` auto `commit()` di `yield` | Side-effect tersembunyi: semua `SELECT` pun commit, error `Integrity` rollback implicit sulit debug. Violate UoW. | Best practice FastAPI: `get_db` hanya yield, commit eksplisit di `service`/`router` atau middleware. Atau pakai `async with session.begin()`. |
| **H3** | `api/v1/auth.py:105-147` | `refresh` stateless tanpa revoke + `db.get` tiap refresh | Refresh token dicuri = valid 7 hari walau user ganti password. Tidak ada blacklist. | Tambah `token_jti` + simpan di Redis/DB + endpoint `logout`. Minimal: increment `user.token_version` saat `change_password`. |
| **H4** | `api/v1/finance.py:24-28` & `stores/finance.ts:41` | `_is_premium` cek `plan_expires_at > now` (naive vs UTC) & frontend cek `slug==='premium'` | Backend cek `plan_id is not None` saja → gratis yang punya `plan_expires_at` lama bisa lolos. Frontend drift. | Satukan: `is_premium = plan.slug=='premium' and expires > now(UTC)`. Buat `core/plan.py:get_active_plan()`. |
| **H5** | `api/v1/guests.py:17` & `services/checklist.py:113` | `GET /guests` & `/checklists` tanpa `limit/offset` | 5000 tamu = OOM JSON 10MB. | Tambah `Query(limit=50, le=100)` + `select().offset().limit()`. Wajib untuk multi-tenant. |
| **H6** | `api/v1/weddings.py:69-118` | Bisnis logic `setattr + flush + sync_savings_target` di router | Violate layering, sulit test. `member_count` di-attach via `setattr` typing liar. | Pindah ke `services/wedding.update_wedding()`. Router hanya `await service.update(...)`. |
| **H7** | `schemas/auth.py:21` & `services/auth.py:40` | `RegisterRequest` tanpa `Field(min_length=8)` + login tak cek `is_active` | Password `123` lolos Pydantic, user banned masih bisa login (deps cek, service tidak). | Tambah `password: str = Field(min_length=8, max_length=128)` + `if not user.is_active: raise 401` di `authenticate_user`. |
| **H8** | `services/analytics.py:170-211` | `all_txns = select(...).where(wedding_id)` lalu `defaultdict` di Python + buat 12 bulan dari `created_at` | Load 10k txn ke memory, N+1 kategori. | Agregasi di DB: `func.date_trunc('month', transaction_date)` + `group_by`. Jangan `select *` untuk analytics. |

---

## 5. 🟡 MEDIUM — Performance & Maintainability

### Backend

* **Missing Index:** `guests.wedding_id`, `checklists.wedding_id`, `transactions.wedding_id` sudah ada tapi `guests(category)`, `checklists(status,due_date)`, `vendors(due_date)` belum. Tambah `Index` di migration.
* **Error Response tidak konsisten:** `finance.py:155` return `{"code":...}` di dalam `detail` dict, tapi `deps.py` return string plain. Frontend `extractError` harus cover keduanya — fragile. Standarkan: `{"detail": {"code":..,"message":..}}` via custom `HTTPException` handler di `main.py`.
* **Missing Rate Limit:** `POST /auth/login`, `/forgot-password`, `/google` tanpa throttling → brute force / email enumeration (walaupun sudah `200` always, tetap bisa spam SMTP log). Pakai `slowapi` atau `fastapi-limiter`.
* **Validation longgar:** `schemas/wedding.py:WeddingUpdate` semua `Optional` tanpa `Field(max_length)`. `total_budget` `int` tanpa `ge=0`. `pair_code` tidak normalized `upper().strip()`.
* **Alembic:** `env.py:22-35` import `app.models.*` manual, kalau tambah model baru lupa import = `autogenerate` miss. Pakai `import app.models` saja (sudah ada `Base.metadata`).
* **Tests:** `tests/conftest.py:11` pakai `sqlite+aiosqlite:///./test.db` untuk Postgres + `echo=True` + file `test.db` di root (kotor). Beda dialek `BigInteger`, `ilike`, `Date`. Harus pakai `testcontainers/postgres` atau `asyncpg` mock.
* **Type Safety:** `app/api/v1/weddings.py:35` `return wedding  # type: ignore[return-value]` + `app/api/v1/admin.py` banyak `# type: ignore[arg-type]` — indikasi Pydantic `from_attributes` vs `member_count` transient tidak di-modelkan. Buat `WeddingResponseWithCount` atau `model_validate`.

### Frontend

* **Anti-pattern `useApi()` di top-level store:** `stores/guest.ts:24` `const api = useApi()` dieksekusi saat store di-import (SSR). Seharusnya `const api = useApi()` di **dalam** setiap function, atau pakai `() => useApi()`.
* **Auth Flash:** `middleware/auth.global.ts:5-7` `auth.restore()` cuma `import.meta.client` → SSR render `isAuthenticated=false` → hydration mismatch + redirect flicker. Pakai `useCookie('kanikah_token')` yang universal.
* **TypeScript tidak strict:** `tsconfig.json` extend `.nuxt/tsconfig.json` saja, tidak ada `strict:true`, tidak ada `eslint`. `stores/auth.ts:114` `as unknown as AuthUser` + `any` banyak.
* **ManualChunks fragile:** `nuxt.config:25` `id.includes('chart.js')` bisa salah match subpath. Lebih aman pakai `manualChunks: { chart: ['chart.js'] }` object.
* **Dashboard countdown:** `setInterval(() => Date.now(),1000)` tiap detik trigger re-render semua card + 4 `pad2` keyed div → jank di low-end HP. Pakai `useIntervalFn` + `computed` throttle 1s ok, tapi pertimbangkan `requestAnimationFrame` atau pause saat `document.hidden`.
* **Keamanan FE:** Tidak ada `sanitize` untuk `guest.notes`, `vendor.notes`, `activity.title` yang dirender via `{{ }}` (Vue auto-escape aman) tapi tetap perlu `DOMPurify` jika pakai `v-html`.
* **Duplikasi logic:** `isPremium` ada 3 tempat (`dashboard.vue:22`, `finance.ts:41`, `finance.py:24`) dengan rule beda. Buat `composables/usePremium.ts`.
* **Lainnya:** `dashboard.vue` `Welcome back, {{ auth.user?.name?.split(' ')[0] ?? 'Steven' }}` hardcode fallback `Steven` sisa template. `layouts/dashboard.vue` SVG inline besar — pindah ke `components/icons`.

---

## 6. Checklist Best Practice

### FastAPI — Sudah vs Belum

| Praktik | Status |
|---|---|
| `Annotated` + `Depends` untuk DI | ✅ Sudah |
| `AsyncSession` + `select()` SA 2.0 | ✅ Sudah |
| `Pydantic v2` `ConfigDict(from_attributes)` | ✅ Sudah |
| `HTTPBearer` + `verify_token` terpusat | ✅ Sudah (tapi tanpa `auto_error=False`) |
| `lifespan` + `engine.dispose` | ✅ Sudah |
| `StrEnum` central + `log_activity` | ✅ Sudah |
| **Pagination + `X-Total-Count`** | ❌ Belum |
| **Rate limiter + Request ID middleware** | ❌ Belum |
| **Global Exception Handler → format `detail.code`** | ❌ Belum |
| **BackgroundTasks / Celery untuk email reset** | ❌ Masih `print()` |
| **Field validator `constr` + `field_validator`** | ⚠️ Parsial |
| **Row-Level Isolation via `wedding_id` filter** | ✅ Sudah (deps konsisten) |

### Nuxt 3 — Sudah vs Belum

| Praktik | Status |
|---|---|
| `<script setup>` + Composition API | ✅ Sudah |
| Pinia + Optimistic Update | ✅ Sudah |
| `useRuntimeConfig().public.apiBase` | ✅ Sudah |
| `$fetch.create` + interceptor | ✅ Sudah |
| **SSR-safe `useCookie` (bukan localStorage)** | ❌ Belum |
| **`useFetch`/`useAsyncData` untuk SSR** | ❌ Semua pakai `$fetch` client-only |
| **Route middleware `auth.global` order + `navigateTo`** | ⚠️ Ada tapi blocking |
| **Auto-import `dirs: ['composables','stores']` explicit** | ✅ Sudah (bagus hindari `types` conflict) |
| **Vitest + @vue/test-utils** | ❌ Belum ada (`npm run test` tidak ada di `package.json`) |
| **ESLint + `vue-tsc` strict** | ❌ Belum (hanya `vue-tsc` devDep) |
| **Mobile-First layouts** | ✅ Sudah (sidebar responsive) |

---

## 7. To-Do Prioritas

### P0 — Minggu Ini (Wajib sebelum deploy)

- [ ] **[SECURITY] Rotate secret + gitignore `.env` + hapus history**
  - `git rm --cached backend/.env frontend/.env` + tambah `.gitignore`
  - Rotate `GOOGLE_CLIENT_SECRET` di Google Cloud Console
  - `backend/app/core/config.py` tambah validator `len(JWT_SECRET_KEY) >= 32`

- [ ] **[SECURITY] Ganti `localStorage` → `useCookie`**
  - Sementara + tambah CSP header di `nuxt.config.ts:nitro.routeRules`

- [ ] **[PERF] `core/database.py` hapus `NullPool`**
  ```python
  engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True)
  # NullPool hanya untuk test
  ```

- [ ] **[API] Tambah pagination di `guests/checklists/transactions/admin/*`**
  ```python
  @router.get("/", response_model=PaginatedGuestResponse)
  async def list_guests(..., page: int=Query(1, ge=1), limit: int=Query(20, le=100)):
      offset = (page-1)*limit
      # select().offset(offset).limit(limit)
  ```

### P1 — Sprint Depan

- [ ] **[ARCH] Pindah logic `weddings.py:PATCH` ke `services/wedding.py`**
- [ ] **[SEC] `slowapi` limiter `login 5/min`, `forgot 3/min`**
- [ ] **[FE] Refactor `stores/*`: `const api = useApi()` pindah ke dalam function**
- [ ] **[FE] `useCookie` + `auth.restore` universal (hapus `import.meta.client` guard)**
- [ ] **[DB] Migration indeks `CREATE INDEX ON guests(wedding_id, category)` dst.**
- [ ] **[VALIDATION] `schemas/auth.py` tambah `Field(min_length=8)` + cek `is_active`**
- [ ] **[SEC] Satukan `is_premium` logic BE/FE**

### P2 — Nice to Have

- [ ] Tambah `tests/integration/test_finance_premium` & ganti `conftest` ke `postgres` container
- [ ] `main.py` exception handler → `{detail:{code,message}}` konsisten
- [ ] `schemas/*.py` tambah `Field` validator lengkap (password, budget, phone)
- [ ] Aktifkan `eslint` + `typescript strict` di `nuxt.config`
- [ ] Ganti `print("[kanikah] Reset link")` dengan `BackgroundTasks` + SMTP
- [ ] `services/analytics.py` agregasi bulanan di DB via `date_trunc`

---

## 8. Catatan Mobile-First

Layout dashboard sudah mobile-first:
* Sidebar `w-[280px] → lg:w-[72px]` + backdrop blur + `lg:hidden` toggle — benar.
* Grid `col-span-12 xl:col-span-4` + `grid-cols-12 gap-4` — responsive.

**Perbaikan:**
* Tabel `Tugas Terbaru` di `dashboard.vue:555` masih `overflow-x-auto` — tambahkan versi card `v-if="isMobile"` sesuai skill `mobile-first` (tabel → card list di <640px).
* Form `guests.vue` / `vendors.vue` perlu cek: input `type="tel"` + `autocomplete` + `inputmode` untuk HP.

---

## 9. Lampiran — File yang Diperiksa

**Backend (32 files):**
`app/main.py`, `core/config.py`, `core/security.py`, `core/database.py`, `core/deps.py`, `core/enums.py`, `models/base.py`, `models/user.py`, `models/wedding.py`, `models/guest.py`, `models/checklist.py`, `models/wedding_user.py`, `models/vendor.py`, `models/transaction.py`, `api/v1/router.py`, `api/v1/auth.py`, `api/v1/guests.py`, `api/v1/weddings.py`, `api/v1/checklists.py`, `api/v1/admin.py`, `api/v1/finance.py`, `api/v1/analytics.py`, `services/auth.py`, `services/guest.py`, `services/wedding.py`, `services/checklist.py`, `services/transaction.py`, `services/analytics.py`, `schemas/auth.py`, `schemas/guest.py`, `schemas/wedding.py`, `schemas/checklist.py`, `schemas/transaction.py`

**Frontend (15 files):**
`nuxt.config.ts`, `tsconfig.json`, `package.json`, `app/composables/useApi.ts`, `app/composables/useAdminApi.ts`, `app/stores/auth.ts`, `app/stores/wedding.ts`, `app/stores/guest.ts`, `app/stores/checklist.ts`, `app/stores/finance.ts`, `app/middleware/auth.global.ts`, `app/layouts/dashboard.vue`, `app/pages/dashboard.vue`

**Hasil `ruff check`:** 9x E501 (line too long) — minor, sudah difilter di `pyproject.toml`.

---

## Penutup

> Skor rata-rata 5.8/10 — MVP layak demo, belum layak production. Fokus P0 dulu (secret + pooling + pagination + cookie). Setelah P0 beres, skor bisa naik ke 7.5/10 dan siap hardening P1.

**Next step yang disarankan:** Saya bisa buatkan PR fix untuk P0 (3 file) langsung: `database.py` + `pagination` + `.gitignore` + `CORS`. Mau dilanjutkan?

---
*Generated: 2026-09-02 | Tool: muse-spark-1.2 | Reviewer mode: Security, Performance, Maintainability*
