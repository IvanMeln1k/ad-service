import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_profile_success(client: AsyncClient, fake_service):
    await fake_service.create_profile(None, "user-1", "Ivan", "ivan@test.com")

    response = await client.get("/api/v1/profile/user-1")
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "user-1"
    assert data["name"] == "Ivan"
    assert data["email"] == "ivan@test.com"


@pytest.mark.asyncio
async def test_get_profile_not_found(client: AsyncClient):
    response = await client.get("/api/v1/profile/nonexistent")
    assert response.status_code == 404
