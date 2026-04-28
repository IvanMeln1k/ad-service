from httpx import AsyncClient
from tests.conftest import AUTH_HEADERS


async def test_attributes_can_create_ad(client: AsyncClient, fake_auth):
    fake_auth.user.email_confirmed = True
    response = await client.get("/api/v1/attributes?attrs=can_create_ad", headers=AUTH_HEADERS)
    assert response.status_code == 200
    assert response.json() == {"can_create_ad": True}


async def test_attributes_cannot_create_ad(client: AsyncClient, fake_auth):
    fake_auth.user.email_confirmed = False
    response = await client.get("/api/v1/attributes?attrs=can_create_ad", headers=AUTH_HEADERS)
    assert response.status_code == 200
    assert response.json() == {"can_create_ad": False}


async def test_attributes_can_moderate(client: AsyncClient, fake_auth):
    fake_auth.user.roles = ["MODERATOR"]
    response = await client.get("/api/v1/attributes?attrs=can_moderate", headers=AUTH_HEADERS)
    assert response.status_code == 200
    assert response.json() == {"can_moderate": True}


async def test_attributes_multiple(client: AsyncClient, fake_auth):
    fake_auth.user.email_confirmed = True
    fake_auth.user.roles = []
    response = await client.get("/api/v1/attributes?attrs=can_create_ad,can_moderate", headers=AUTH_HEADERS)
    assert response.status_code == 200
    assert response.json() == {"can_create_ad": True, "can_moderate": False}


async def test_attributes_staff_cannot_create_ad(client: AsyncClient, fake_auth):
    fake_auth.user.email_confirmed = True
    fake_auth.user.roles = ["ADMIN"]
    response = await client.get("/api/v1/attributes?attrs=can_create_ad", headers=AUTH_HEADERS)
    assert response.status_code == 200
    assert response.json() == {"can_create_ad": False}


async def test_attributes_unknown_ignored(client: AsyncClient, fake_auth):
    response = await client.get("/api/v1/attributes?attrs=can_create_ad,nonexistent", headers=AUTH_HEADERS)
    assert response.status_code == 200
    assert "nonexistent" not in response.json()


async def test_attributes_no_auth(client: AsyncClient):
    response = await client.get("/api/v1/attributes?attrs=can_create_ad")
    assert response.status_code == 401
