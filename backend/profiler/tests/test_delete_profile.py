import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_delete_profile_success(client: AsyncClient, fake_service):
    await fake_service.create_profile(None, "user-1", "Ivan", "ivan@test.com")

    response = await client.delete("/api/v1/profile/user-1")
    assert response.status_code == 204
    assert "user-1" not in fake_service.profiles


@pytest.mark.asyncio
async def test_delete_profile_not_found(client: AsyncClient):
    response = await client.delete("/api/v1/profile/nonexistent")
    assert response.status_code == 404
