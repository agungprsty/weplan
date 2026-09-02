# Kanikah - Wedding Planner - Backend

Backend API untuk platform Wedding Planner dibangun dengan FastAPI, SQLAlchemy 2.0 (async), dan PostgreSQL.

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
