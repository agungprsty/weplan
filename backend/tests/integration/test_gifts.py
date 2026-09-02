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


async def create_guest(
    client: AsyncClient, token: str, wedding_id: str, name: str
) -> str:
    response = await client.post(
        f"/api/v1/weddings/{wedding_id}/guests/",
        json={"name": name},
        headers={"Authorization": f"Bearer {token}"},
    )
    return response.json()["id"]


@pytest.mark.asyncio
async def test_create_gift(client: AsyncClient):
    token = await register_and_login(client)
    wedding_id = await create_wedding(client, token)
    guest_id = await create_guest(client, token, wedding_id, "Budi Santoso")
    response = await client.post(
        f"/api/v1/weddings/{wedding_id}/gifts/",
        json={"guest_id": guest_id, "type": "uang", "amount": 500000},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["type"] == "uang"
    assert data["amount"] == 500000
    assert data["guest_name"] == "Budi Santoso"


@pytest.mark.asyncio
async def test_list_gifts_and_guest_summary(client: AsyncClient):
    token = await register_and_login(client)
    wedding_id = await create_wedding(client, token)
    guest_id = await create_guest(client, token, wedding_id, "Guest 1")
    other_id = await create_guest(client, token, wedding_id, "Guest 2")
    await client.post(
        f"/api/v1/weddings/{wedding_id}/gifts/",
        json={"guest_id": guest_id, "type": "uang", "amount": 100000},
        headers={"Authorization": f"Bearer {token}"},
    )
    await client.post(
        f"/api/v1/weddings/{wedding_id}/gifts/",
        json={"guest_id": guest_id, "type": "kado", "description": "Piring"},
        headers={"Authorization": f"Bearer {token}"},
    )
    await client.post(
        f"/api/v1/weddings/{wedding_id}/gifts/",
        json={"guest_id": other_id, "type": "uang", "amount": 250000},
        headers={"Authorization": f"Bearer {token}"},
    )

    gifts = await client.get(
        f"/api/v1/weddings/{wedding_id}/gifts/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert gifts.status_code == 200
    assert len(gifts.json()) == 3

    guests = await client.get(
        f"/api/v1/weddings/{wedding_id}/guests/",
        headers={"Authorization": f"Bearer {token}"},
    )
    guests_data = guests.json()
    # support paginated {data, meta} and legacy list
    if isinstance(guests_data, dict) and "data" in guests_data:
        guests_data = guests_data["data"]
    summary = {g["name"]: g for g in guests_data}
    assert summary["Guest 1"]["gift_count"] == 2
    assert summary["Guest 1"]["gift_total"] == 100000
    assert summary["Guest 2"]["gift_count"] == 1
    assert summary["Guest 2"]["gift_total"] == 250000


@pytest.mark.asyncio
async def test_update_and_delete_gift(client: AsyncClient):
    token = await register_and_login(client)
    wedding_id = await create_wedding(client, token)
    guest_id = await create_guest(client, token, wedding_id, "Guest 1")
    created = await client.post(
        f"/api/v1/weddings/{wedding_id}/gifts/",
        json={"guest_id": guest_id, "type": "kado"},
        headers={"Authorization": f"Bearer {token}"},
    )
    gift_id = created.json()["id"]

    updated = await client.patch(
        f"/api/v1/weddings/{wedding_id}/gifts/{gift_id}",
        json={"type": "uang", "amount": 75000},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert updated.status_code == 200
    assert updated.json()["type"] == "uang"
    assert updated.json()["amount"] == 75000

    deleted = await client.delete(
        f"/api/v1/weddings/{wedding_id}/gifts/{gift_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert deleted.status_code == 204
    gone = await client.get(
        f"/api/v1/weddings/{wedding_id}/gifts/{gift_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert gone.status_code == 404


@pytest.mark.asyncio
async def test_gifts_tenant_isolation(client: AsyncClient):
    token_a = await register_and_login(client)
    wedding_a = await create_wedding(client, token_a)
    guest_a = await create_guest(client, token_a, wedding_a, "Guest A")
    created = await client.post(
        f"/api/v1/weddings/{wedding_a}/gifts/",
        json={"guest_id": guest_a, "type": "uang", "amount": 1000},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    gift_id = created.json()["id"]

    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "other@example.com",
            "password": "password123",
            "full_name": "Other User",
        },
    )
    login_b = await client.post(
        "/api/v1/auth/login",
        json={"email": "other@example.com", "password": "password123"},
    )
    token_b = login_b.json()["access_token"]
    wedding_b = await create_wedding(client, token_b)

    listed = await client.get(
        f"/api/v1/weddings/{wedding_b}/gifts/",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert listed.status_code == 200
    assert listed.json() == []

    fetched = await client.get(
        f"/api/v1/weddings/{wedding_b}/gifts/{gift_id}",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert fetched.status_code == 404
