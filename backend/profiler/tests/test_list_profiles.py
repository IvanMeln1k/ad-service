import pytest
from httpx import AsyncClient
from tests.conftest import make_auth_headers


@pytest.mark.asyncio
async def test_list_profiles_empty(client: AsyncClient, fake_roles_service):
    fake_roles_service.roles["admin"] = ["ADMIN"]
    response = await client.get("/api/v1/profile", headers=make_auth_headers("admin"))
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_list_profiles_with_data(client: AsyncClient, fake_service, fake_roles_service):
    await fake_service.create_profile(None, "user-1", "Ivan", "ivan@test.com")
    await fake_service.create_profile(None, "user-2", "Oleg", "oleg@test.com")
    fake_roles_service.roles["admin"] = ["ADMIN"]

    response = await client.get("/api/v1/profile", headers=make_auth_headers("admin"))
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_list_profiles_pagination(client: AsyncClient, fake_service, fake_roles_service):
    await fake_service.create_profile(None, "user-1", "Ivan", "ivan@test.com")
    await fake_service.create_profile(None, "user-2", "Oleg", "oleg@test.com")
    fake_roles_service.roles["admin"] = ["ADMIN"]

    response = await client.get("/api/v1/profile?limit=1&offset=0", headers=make_auth_headers("admin"))
    assert response.status_code == 200
    assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_list_profiles_forbidden_for_regular_user(client: AsyncClient):
    response = await client.get("/api/v1/profile", headers=make_auth_headers("user-1"))
    assert response.status_code == 403
