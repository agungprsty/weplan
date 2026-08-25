---
name: fastapi-endpoint
description: Guidelines untuk membuat FastAPI endpoints dengan SQLAlchemy async dan Pydantic schemas
license: MIT
metadata:
  framework: fastapi
  language: python
---

## What I do
- Create FastAPI route handlers with proper async/await
- Implement SQLAlchemy 2.0 async database operations
- Create Pydantic v2 schemas for request/response
- Follow dependency injection patterns

## When to use me
Use this when creating or modifying API endpoints in the backend directory.

## Endpoint Structure

```python
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import get_db, get_current_user, get_current_wedding
from app.models.user import User
from app.models.wedding import Wedding
from app.schemas.guest import GuestCreate, GuestResponse, GuestList

router = APIRouter()

@router.get("/weddings/{wedding_id}/guests", response_model=list[GuestResponse])
async def list_guests(
    wedding_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    wedding: Wedding = Depends(get_current_wedding),
) -> list[GuestResponse]:
    """List all guests for a wedding."""
    # Implementation here
    pass
```

## Conventions
- Always use async/await for database operations
- Use `Depends()` for dependency injection
- Validate input with Pydantic schemas
- Return proper HTTP status codes
- Use UUID for all primary keys
- Filter by `wedding_id` for multi-tenancy

## Pydantic v2 Schema Pattern

```python
from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime

class GuestBase(BaseModel):
    name: str
    email: str | None = None
    category: str = "general"

class GuestCreate(GuestBase):
    pass

class GuestResponse(GuestBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    wedding_id: UUID
    rsvp_status: str
    created_at: datetime
```

## Error Handling
```python
from fastapi import HTTPException, status

raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Guest not found"
)
```
