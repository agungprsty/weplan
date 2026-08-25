---
name: database-migration
description: Workflow untuk membuat dan mengelola Alembic database migrations dengan SQLAlchemy
license: MIT
metadata:
  tool: alembic
  orm: sqlalchemy
---

## What I do
- Generate Alembic migrations from SQLAlchemy models
- Create reversible migrations
- Handle data migrations safely
- Follow migration naming conventions

## When to use me
Use this when creating, modifying, or troubleshooting database migrations.

## Migration Workflow

### 1. Generate Migration
```bash
cd backend
alembic revision --autogenerate -m "descriptive message"
```

### 2. Review Generated Migration
Always review the auto-generated migration file:
- Check column types are correct
- Verify foreign key relationships
- Ensure indexes are appropriate
- Check for data loss scenarios

### 3. Apply Migration
```bash
# Apply all pending migrations
alembic upgrade head

# Apply specific migration
alembic upgrade <revision>

# Rollback one step
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision>
```

## Model Convention

```python
import uuid
from datetime import datetime
from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class Guest(Base):
    __tablename__ = "guests"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4
    )
    wedding_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("weddings.id", ondelete="CASCADE")
    )
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    rsvp_status: Mapped[str] = mapped_column(String(20), default="pending")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationships
    wedding: Mapped["Wedding"] = relationship(back_populates="guests")
```

## Naming Conventions
- Migration files: `<revision>_<description>.py`
- Descriptions: use underscores, be specific
  - ✅ `add_guest_rsvp_status`
  - ✅ `create_wedding_users_table`
  - ❌ `update_table`
  - ❌ `changes`

## Safety Rules
- NEVER delete columns without checking for data loss
- ALWAYS add nullable columns first, then backfill
- Use `batch_alter_table` for SQLite compatibility
- Test both upgrade and downgrade paths
