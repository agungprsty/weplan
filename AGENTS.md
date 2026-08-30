# Wedding Planner SaaS - Project Rules

## Project Overview

Platform SaaS multi-tenant untuk kolaborasi real-time pasangan dalam merencanakan pernikahan. Mengelola anggaran, daftar tamu, dan tugas persiapan.

**Target**: MVP dengan fitur Authentication, Workspace Pairing, Checklist/Task Management, Guest Management, dan Budgeting.

## Architecture

```
frontend/          # Nuxt.js 3 (Vue 3 + TypeScript)
backend/           # FastAPI (Python 3.11+)
```

- **Frontend**: Nuxt.js 3, Pinia (state), TailwindCSS, Optimistic UI
- **Backend**: FastAPI, SQLAlchemy (async), Alembic (migrations), JWT auth
- **Database**: PostgreSQL dengan Row-Level Isolation via `wedding_id`

## Development Commands

### Backend

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"

# Run development server
uvicorn app.main:app --reload --port 8000

# Run tests
pytest -v

# Format code
ruff format .
ruff check --fix .
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Run tests
npm run test

# Lint
npm run lint

# Format
npm run format
```

## Project Structure

### Backend (`backend/`)

```
backend/
├── app/
│   ├── main.py              # FastAPI app entry
│   ├── config.py            # Settings (pydantic-settings)
│   ├── database.py          # SQLAlchemy async engine & session
│   ├── models/              # SQLAlchemy ORM models
│   │   ├── user.py
│   │   ├── wedding.py
│   │   ├── guest.py
│   │   └── checklist.py
│   ├── schemas/             # Pydantic request/response schemas
│   │   ├── auth.py
│   │   ├── wedding.py
│   │   ├── guest.py
│   │   └── checklist.py
│   ├── api/                 # API route handlers
│   │   ├── auth.py
│   │   ├── weddings.py
│   │   ├── guests.py
│   │   └── checklists.py
│   ├── core/                # Security, dependencies, utils
│   │   ├── security.py      # JWT token creation/verification
│   │   ├── deps.py          # FastAPI dependencies
│   │   └── config.py
│   └── services/            # Business logic layer
│       ├── auth.py
│       ├── wedding.py
│       └── guest.py
├── alembic/                 # Database migrations
├── tests/                   # Pytest test files
├── alembic.ini
├── pyproject.toml
└── requirements.txt
```

### Frontend (`frontend/`)

```
frontend/
├── app/                     # Nuxt pages (app directory mode)
│   ├── pages/               # File-based routing
│   ├── layouts/             # Layout components
│   ├── components/          # Vue components
│   ├── composables/         # Composable functions (useFetch wrappers)
│   ├── stores/              # Pinia stores
│   ├── middleware/           # Route middleware
│   └── plugins/             # Nuxt plugins
├── public/                  # Static assets
├── nuxt.config.ts
├── tailwind.config.ts
├── package.json
└── tsconfig.json
```

## Coding Conventions

### Python (Backend)

- Follow PEP 8 style guide
- Use type hints on all function signatures
- Use async/await for all database operations
- Import order: stdlib → third-party → local (use `ruff` to enforce)
- Maximum line length: 88 characters (Black/Ruff default)
- Use docstrings for public functions and classes
- snake_case for functions, variables, and modules
- PascalCase for classes and models

### TypeScript (Frontend)

- Use Composition API with `<script setup>` syntax
- Use TypeScript strict mode
- Prefer `ref()` over `reactive()` for state
- Use `useFetch` / `useAsyncData` for server data
- PascalCase for components and composables
- camelCase for variables and functions
- kebab-case for template components

## Database Conventions

### Multi-Tenancy

- All tenant-scoped tables MUST have `wedding_id` column
- Always filter queries by `wedding_id` using dependency injection
- Never expose data from other weddings

### Models

- Use `UUID` for primary keys (via `uuid.uuid4`)
- Include `created_at` and `updated_at` timestamps
- Use `Mapped` type annotations (SQLAlchemy 2.0 style)
- Foreign keys must have `ondelete` behavior specified

### Migrations

- Always generate migrations with `alembic revision --autogenerate`
- Migration messages must be descriptive (e.g., "add guest rsvp status")
- Never edit auto-generated migrations manually
- Test migrations both up and down before committing

## API Conventions

### RESTful Patterns

```
GET    /api/resource              # List
POST   /api/resource              # Create
GET    /api/resource/{id}         # Read
PATCH  /api/resource/{id}         # Update
DELETE /api/resource/{id}         # Delete
```

### Response Format

```json
{
  "data": { ... },
  "meta": { "total": 100 }
}
```

### Error Response

```json
{
  "detail": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input",
    "errors": [...]
  }
}
```

### Authentication

- JWT tokens via `Authorization: Bearer <token>` header
- Use `Depends(get_current_user)` for protected routes
- Use `Depends(get_current_wedding)` for wedding-scoped routes

## Security Rules

- NEVER commit secrets, API keys, or passwords
- NEVER log sensitive data (passwords, tokens, personal info)
- Always validate input with Pydantic schemas
- Use parameterized queries (SQLAlchemy handles this)
- Hash passwords with `bcrypt` via `passlib`
- JWT tokens must have expiration (default: 7 days)

## Git Conventions

- Branch naming: `feature/description`, `fix/description`, `chore/description`
- Commit messages: imperative mood, lowercase, max 72 chars
  - ✅ `add guest rsvp endpoint`
  - ✅ `fix pagination offset calculation`
  - ❌ `Added guest rsvp endpoint`
  - ❌ `Fix pagination`
- Always run linter before committing
- Create PR for any non-trivial changes

## Testing

### Backend (pytest)

- Unit tests in `tests/unit/`
- Integration tests in `tests/integration/`
- Use `pytest-asyncio` for async tests
- Use `factory_boy` for test data generation
- Test files named `test_<module>.py`

### Frontend (Vitest)

- Component tests alongside components
- Use `@vue/test-utils` for mounting
- Mock API calls with `vitest.mock`
- Test composables separately

## Common Patterns

### FastAPI Dependency Injection

```python
async def get_current_wedding(
    wedding_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Wedding:
    # Verify user has access to this wedding
    ...
```

### Pinia Store with Optimistic Update

```typescript
export const useGuestStore = defineStore('guests', () => {
  const guests = ref<Guest[]>([])

  async function addGuest(data: CreateGuestInput) {
    // Optimistic: add immediately
    const optimistic = { ...data, id: crypto.randomUUID() }
    guests.value.push(optimistic)

    try {
      const real = await $fetch(`/api/guests`, { method: 'POST', body: data })
      // Replace optimistic with real data
      const idx = guests.value.findIndex(g => g.id === optimistic.id)
      guests.value[idx] = real
    } catch {
      // Rollback on error
      guests.value = guests.value.filter(g => g.id !== optimistic.id)
    }
  }
})
```
