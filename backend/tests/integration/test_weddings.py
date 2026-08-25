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
        data={"username": "test@example.com", "password": "password123"},
    )
    return response.json()["access_token"]


@pytest.mark.asyncio
async def test_create_wedding(client: AsyncClient):
    token = await register_and_login(client)
    response = await client.post(
        "/api/v1/weddings/",
        json={
            "title": "Wedding of Agung & Fani",
            "partner1_name": "Agung",
            "partner2_name": "Fani",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Wedding of Agung & Fani"
    assert "pair_code" in data


@pytest.mark.asyncio
async def test_get_my_wedding(client: AsyncClient):
    token = await register_and_login(client)
    await client.post(
        "/api/v1/weddings/",
        json={
            "title": "Wedding of Agung & Fani",
            "partner1_name": "Agung",
            "partner2_name": "Fani",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    response = await client.get(
        "/api/v1/weddings/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Wedding of Agung & Fani"
