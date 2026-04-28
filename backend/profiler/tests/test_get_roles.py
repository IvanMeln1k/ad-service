import pytest
from httpx import AsyncClient
from tests.conftest import make_auth_headers


@pytest.mark.asyncio
async def test_get_roles_empty(client: AsyncClient, fake_roles_service):
    response = await client.get("/api/v1/profile/user-1/roles", headers=make_auth_headers("user-1"))
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_roles_with_roles(client: AsyncClient, fake_roles_service):
    fake_roles_service.roles["user-1"] = ["MODERATOR"]

    response = await client.get("/api/v1/profile/user-1/roles", headers=make_auth_headers("user-1"))
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["role"] == "MODERATOR"
    assert "assigned_at" in data[0]


@pytest.mark.asyncio
async def test_get_roles_for_other_user_forbidden(client: AsyncClient):
    response = await client.get("/api/v1/profile/user-2/roles", headers=make_auth_headers("user-1"))
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_manage_roles_admin_only(client: AsyncClient, fake_roles_service, fake_service):
    fake_roles_service.roles["admin"] = ["ADMIN"]
    await fake_service.create_profile(None, "user-2", "User Two", "u2@test.com")

    forbidden = await client.post(
        "/api/v1/profile/user-2/roles",
        json={"role": "MODERATOR"},
        headers=make_auth_headers("user-1"),
    )
    assert forbidden.status_code == 403

    granted = await client.post(
        "/api/v1/profile/user-2/roles",
        json={"role": "MODERATOR"},
        headers=make_auth_headers("admin"),
    )
    assert granted.status_code == 200
    assert any(r["role"] == "MODERATOR" for r in granted.json())
