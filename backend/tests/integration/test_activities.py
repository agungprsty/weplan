import pytest
from httpx import AsyncClient


async def register_and_login(
    client: AsyncClient, email: str = "act@example.com"
) -> str:
    await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "password123", "full_name": "Act User"},
    )
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "password123"},
    )
    return response.json()["access_token"]


async def create_wedding(client: AsyncClient, token: str) -> str:
    response = await client.post(
        "/api/v1/weddings/",
        json={"title": "Act Wedding", "partner1_name": "A", "partner2_name": "B"},
        headers={"Authorization": f"Bearer {token}"},
    )
    return response.json()["id"]


@pytest.mark.asyncio
async def test_activities_record_crud_and_status(client: AsyncClient):
    token = await register_and_login(client)
    wedding_id = await create_wedding(client, token)
    h = {"Authorization": f"Bearer {token}"}

    # checklist create -> status_changed -> deleted
    task = await client.post(
        f"/api/v1/weddings/{wedding_id}/checklists/",
        json={"title": "Booking venue", "category": "vendor"},
        headers=h,
    )
    assert task.status_code == 201
    task_id = task.json()["id"]

    await client.patch(
        f"/api/v1/weddings/{wedding_id}/checklists/{task_id}",
        json={"status": "done"},
        headers=h,
    )

    # guest create -> deleted
    guest = await client.post(
        f"/api/v1/weddings/{wedding_id}/guests/",
        json={"name": "Budi"},
        headers=h,
    )
    assert guest.status_code == 201
    guest_id = guest.json()["id"]
    await client.delete(f"/api/v1/weddings/{wedding_id}/guests/{guest_id}", headers=h)

    response = await client.get(
        f"/api/v1/weddings/{wedding_id}/activities/",
        headers=h,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["meta"]["total"] >= 4

    actions = [(a["action"], a["entity_type"], a["title"]) for a in body["data"]]
    assert ("created", "wedding", "Act Wedding") in actions
    assert ("created", "checklist", "Booking venue") in actions
    assert ("status_changed", "checklist", "Booking venue") in actions
    assert ("deleted", "guest", "Budi") in actions

    # newest first
    created_times = [a["created_at"] for a in body["data"]]
    assert created_times == sorted(created_times, reverse=True)

    # actor attribution
    status_row = next(a for a in body["data"] if a["action"] == "status_changed")
    assert status_row["actor_name"] == "Act User"
    assert status_row["meta"] == {"from": "todo", "to": "done"}


@pytest.mark.asyncio
async def test_activities_tenant_isolation(client: AsyncClient):
    token1 = await register_and_login(client, "iso1@example.com")
    token2 = await register_and_login(client, "iso2@example.com")
    w1 = await create_wedding(client, token1)
    w2 = await create_wedding(client, token2)

    await client.post(
        f"/api/v1/weddings/{w1}/guests/",
        json={"name": "OnlyW1"},
        headers={"Authorization": f"Bearer {token1}"},
    )

    response = await client.get(
        f"/api/v1/weddings/{w2}/activities/",
        headers={"Authorization": f"Bearer {token2}"},
    )
    assert response.status_code == 200
    titles = [a["title"] for a in response.json()["data"]]
    assert "OnlyW1" not in titles
    assert all(a["wedding_id"] == w2 for a in response.json()["data"])


@pytest.mark.asyncio
async def test_activities_entity_type_filter(client: AsyncClient):
    token = await register_and_login(client, "filt@example.com")
    wedding_id = await create_wedding(client, token)
    h = {"Authorization": f"Bearer {token}"}

    await client.post(
        f"/api/v1/weddings/{wedding_id}/guests/",
        json={"name": "F1"},
        headers=h,
    )
    await client.post(
        f"/api/v1/weddings/{wedding_id}/checklists/",
        json={"title": "T1", "category": "kua"},
        headers=h,
    )

    response = await client.get(
        f"/api/v1/weddings/{wedding_id}/activities/?entity_type=guest",
        headers=h,
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data and all(a["entity_type"] == "guest" for a in data)
