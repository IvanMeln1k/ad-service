import pytest
from httpx import AsyncClient
from tests.conftest import make_auth_headers


@pytest.mark.asyncio
async def test_update_profile_success(client: AsyncClient, fake_service):
    await fake_service.create_profile(None, "user-1", "Ivan", "ivan@test.com")

    response = await client.patch(
        "/api/v1/profile/user-1",
        json={"name": "Ivan Updated", "city": "Moscow"},
        headers=make_auth_headers("user-1"),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Ivan Updated"
    assert data["city"] == "Moscow"


@pytest.mark.asyncio
async def test_update_profile_not_found(client: AsyncClient):
    response = await client.patch(
        "/api/v1/profile/nonexistent",
        json={"name": "Test"},
        headers=make_auth_headers("nonexistent"),
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_profile_forbidden_for_other_user(client: AsyncClient, fake_service):
    await fake_service.create_profile(None, "user-2", "Ivan", "ivan@test.com")
    response = await client.patch(
        "/api/v1/profile/user-2",
        json={"name": "Changed"},
        headers=make_auth_headers("user-1"),
    )
    assert response.status_code == 403
