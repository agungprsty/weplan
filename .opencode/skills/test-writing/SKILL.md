---
name: test-writing
description: Guidelines untuk testing dengan pytest (backend) dan Vitest (frontend)
license: MIT
metadata:
  backend: pytest
  frontend: vitest
---

## What I do
- Write unit tests for Python backend with pytest
- Write component tests for Vue frontend with Vitest
- Create test fixtures and factories
- Mock external dependencies

## When to use me
Use this when writing or modifying tests in the project.

## Backend Testing (pytest)

### File Structure
```
backend/tests/
├── unit/
│   ├── test_models.py
│   ├── test_schemas.py
│   └── test_services.py
├── integration/
│   ├── test_auth.py
│   ├── test_guests.py
│   └── test_checklists.py
├── conftest.py
└── factories.py
```

### Test Pattern
```python
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_create_guest(client: AsyncClient, auth_headers: dict):
    """Test creating a new guest."""
    response = await client.post(
        "/api/weddings/test-id/guests",
        json={"name": "John Doe", "email": "john@example.com"},
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "John Doe"
```

### Fixtures (conftest.py)
```python
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer test-token"}
```

## Frontend Testing (Vitest)

### Component Test
```typescript
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import GuestCard from './GuestCard.vue'

describe('GuestCard', () => {
  it('renders guest name', () => {
    const wrapper = mount(GuestCard, {
      props: { name: 'John Doe', rsvpStatus: 'attending' }
    })
    expect(wrapper.text()).toContain('John Doe')
  })
})
```

### Composable Test
```typescript
import { describe, it, expect, vi } from 'vitest'
import { useGuests } from './useGuests'

vi.mock('$fetch', () => ({
  default: vi.fn()
}))

describe('useGuests', () => {
  it('fetches guests on mount', async () => {
    const { guests } = useGuests('wedding-id')
    await nextTick()
    expect(guests.value).toBeDefined()
  })
})
```

## Conventions
- Test files: `test_<module>.py` (backend), `*.spec.ts` (frontend)
- One test file per module/component
- Use descriptive test names that explain the scenario
- Group related tests with `describe` blocks
- Mock external services, not internal logic
- Test both success and error paths
