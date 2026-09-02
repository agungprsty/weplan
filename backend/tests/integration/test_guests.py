import pytest
from httpx import AsyncClient


async def register_and_login(client: AsyncClient) -> str:
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "password123",
            "full_name": "Test User",
        },
    )
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "password123"},
    )
    return response.json()["access_token"]


async def create_wedding(client: AsyncClient, token: str) -> str:
    response = await client.post(
        "/api/v1/weddings/",
        json={
            "title": "Wedding of Agung & Fani",
            "partner1_name": "Agung",
            "partner2_name": "Fani",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    return response.json()["id"]


@pytest.mark.asyncio
async def test_create_guest(client: AsyncClient):
    token = await register_and_login(client)
    wedding_id = await create_wedding(client, token)
    response = await client.post(
        f"/api/v1/weddings/{wedding_id}/guests/",
        json={
            "name": "Budi Santoso",
            "email": "budi@example.com",
            "category": "family",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Budi Santoso"
    assert data["rsvp_status"] == "pending"


@pytest.mark.asyncio
async def test_list_guests(client: AsyncClient):
    token = await register_and_login(client)
    wedding_id = await create_wedding(client, token)
    await client.post(
        f"/api/v1/weddings/{wedding_id}/guests/",
        json={"name": "Guest 1"},
        headers={"Authorization": f"Bearer {token}"},
    )
    await client.post(
        f"/api/v1/weddings/{wedding_id}/guests/",
        json={"name": "Guest 2"},
        headers={"Authorization": f"Bearer {token}"},
    )
    response = await client.get(
        f"/api/v1/weddings/{wedding_id}/guests/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    if isinstance(data, dict) and "data" in data:
        data = data["data"]
    assert len(data) == 2


@pytest.mark.asyncio
async def test_update_guest_rsvp(client: AsyncClient):
    token = await register_and_login(client)
    wedding_id = await create_wedding(client, token)
    create_response = await client.post(
        f"/api/v1/weddings/{wedding_id}/guests/",
        json={"name": "Guest 1"},
        headers={"Authorization": f"Bearer {token}"},
    )
    guest_id = create_response.json()["id"]
    response = await client.patch(
        f"/api/v1/weddings/{wedding_id}/guests/{guest_id}",
        json={"rsvp_status": "attending"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["rsvp_status"] == "attending"
