# Wedding Planner SaaS

Platform SaaS multi-tenant untuk kolaborasi real-time pasangan dalam merencanakan pernikahan. Mengelola anggaran, daftar tamu, dan tugas persiapan.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Nuxt.js 3 (Vue 3 + TypeScript) |
| State Management | Pinia |
| Styling | TailwindCSS |
| Backend | FastAPI (Python 3.11+) |
| ORM | SQLAlchemy (async) |
| Migrations | Alembic |
| Database | PostgreSQL |
| Authentication | JWT |

## Features (MVP)

- **Authentication & Workspace** - Registrasi, login, dan shared workspace via pairing code
- **Checklist & Task Management** - Daftar tugas pernikahan dengan status dan assignee
- **Guest Management** - CRUD tamu dengan kategori dan RSVP tracking
- **Budgeting** - Target anggaran dan alokasi dana per kategori

## Prerequisites

- Node.js 18+ (untuk frontend)
- Python 3.11+ (untuk backend)
- PostgreSQL 14+
- pip atau poetry (Python package manager)
- npm atau pnpm (Node package manager)

## Installation

### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your database credentials

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --port 8000
```

API documentation available at: `http://localhost:8000/docs`

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Setup environment variables
cp .env.example .env.local
# Edit .env.local with your API URL

# Start development server
npm run dev
```

Frontend available at: `http://localhost:3000`

## Project Structure

```
kanikah/
├── frontend/                 # Nuxt.js application
│   ├── app/
│   │   ├── pages/           # File-based routing
│   │   ├── components/      # Vue components
│   │   ├── composables/     # Composable functions
│   │   ├── stores/          # Pinia stores
│   │   └── layouts/         # Layout components
│   ├── nuxt.config.ts
│   └── package.json
├── backend/                  # FastAPI application
│   ├── app/
│   │   ├── api/             # API routes
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── services/        # Business logic
│   │   └── core/            # Config & security
│   ├── alembic/             # Database migrations
│   └── requirements.txt
├── AGENTS.md                 # AI agent rules
├── opencode.json             # OpenCode configuration
└── plan.json                 # Project plan
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token

### Workspace
- `POST /api/weddings` - Create wedding workspace
- `POST /api/weddings/pair` - Pair account with unique code
- `GET /api/weddings/me` - Get user's wedding details

### Guests
- `GET /api/weddings/{id}/guests` - List guests
- `POST /api/weddings/{id}/guests` - Add guest
- `PATCH /api/weddings/{id}/guests/{id}` - Update guest/RSVP

### Checklists
- `GET /api/weddings/{id}/checklists` - List tasks
- `PATCH /api/weddings/{id}/checklists/{id}` - Update task status/assignee

## Development

### Code Style

**Backend (Python)**
- Follow PEP 8
- Use type hints
- Format with Ruff: `ruff format .`
- Lint with Ruff: `ruff check --fix .`

**Frontend (TypeScript)**
- Use Composition API with `<script setup>`
- Format with Prettier
- Lint with ESLint

### Testing

**Backend**
```bash
cd backend
pytest -v
```

**Frontend**
```bash
cd frontend
npm run test
```

## Database Schema

- **users** - User credentials and profile
- **weddings** - Wedding event metadata
- **wedding_users** - User-wedding relationship with roles
- **guests** - Guest list with RSVP status
- **checklists** - Task management with assignments

All tenant tables include `wedding_id` for multi-tenancy (Row-Level Isolation).

## License

Private - All rights reserved.
