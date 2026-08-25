# Wedding Planner SaaS - Backend

Backend API untuk platform Wedding Planner SaaS dibangun dengan FastAPI, SQLAlchemy 2.0 (async), dan PostgreSQL.

## Tech Stack

- **Framework**: FastAPI (Python 3.11+)
- **ORM**: SQLAlchemy 2.0 (async)
- **Database**: PostgreSQL + asyncpg
- **Migrations**: Alembic
- **Auth**: JWT (PyJWT) + Argon2 password hashing (pwdlib)
- **Validation**: Pydantic v2
- **Testing**: pytest + pytest-asyncio + httpx

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup Environment

```bash
cp .env.example .env
# Edit .env dengan konfigurasi database Anda
```

### 3. Setup Database

```bash
# Create database
createdb wedding_planner

# Run migrations
alembic upgrade head
```

### 4. Run Development Server

```bash
uvicorn app.main:app --reload --port 8000
```

API documentation tersedia di: `http://localhost:8000/docs`

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app entry
│   ├── core/                # Core modules
│   │   ├── config.py        # Pydantic Settings
│   │   ├── database.py      # Async SQLAlchemy
│   │   ├── security.py      # JWT + Password hashing
│   │   └── deps.py          # FastAPI dependencies
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── api/v1/              # API routes
│   ├── services/            # Business logic
│   └── utils/               # Helpers
├── alembic/                 # Database migrations
├── tests/                   # Test files
├── alembic.ini
├── pyproject.toml
└── requirements.txt
```

## API Endpoints

### Auth
- `POST /api/v1/auth/register` - Register user baru
- `POST /api/v1/auth/login` - Login dan dapatkan JWT token
- `GET /api/v1/auth/me` - Dapatkan data user saat ini

### Weddings
- `POST /api/v1/weddings/` - Buat workspace wedding baru
- `POST /api/v1/weddings/pair` - Pair akun dengan kode unik
- `GET /api/v1/weddings/me` - Dapatkan data wedding user
- `PATCH /api/v1/weddings/{id}` - Update data wedding

### Guests
- `GET /api/v1/weddings/{id}/guests/` - List semua tamu
- `POST /api/v1/weddings/{id}/guests/` - Tambah tamu
- `GET /api/v1/weddings/{id}/guests/{id}` - Detail tamu
- `PATCH /api/v1/weddings/{id}/guests/{id}` - Update tamu/RSVP
- `DELETE /api/v1/weddings/{id}/guests/{id}` - Hapus tamu

### Checklists
- `GET /api/v1/weddings/{id}/checklists/` - List semua tugas
- `POST /api/v1/weddings/{id}/checklists/` - Buat tugas baru
- `GET /api/v1/weddings/{id}/checklists/{id}` - Detail tugas
- `PATCH /api/v1/weddings/{id}/checklists/{id}` - Update tugas
- `DELETE /api/v1/weddings/{id}/checklists/{id}` - Hapus tugas

## Development

### Code Style

```bash
# Format
ruff format .

# Lint
ruff check --fix .
```

### Testing

```bash
pytest -v
```

### Create Migration

```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```
