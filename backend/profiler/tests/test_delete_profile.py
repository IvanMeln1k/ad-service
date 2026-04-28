import pytest
from httpx import AsyncClient
from tests.conftest import make_auth_headers


@pytest.mark.asyncio
async def test_delete_profile_success(client: AsyncClient, fake_service):
    await fake_service.create_profile(None, "user-1", "Ivan", "ivan@test.com")

    response = await client.delete("/api/v1/profile/user-1", headers=make_auth_headers("user-1"))
    assert response.status_code == 204
    assert "user-1" not in fake_service.profiles


@pytest.mark.asyncio
async def test_delete_profile_not_found(client: AsyncClient):
    response = await client.delete("/api/v1/profile/nonexistent", headers=make_auth_headers("nonexistent"))
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_profile_forbidden_for_other_user(client: AsyncClient, fake_service):
    await fake_service.create_profile(None, "user-2", "Ivan", "ivan@test.com")
    response = await client.delete("/api/v1/profile/user-2", headers=make_auth_headers("user-1"))
    assert response.status_code == 403
