import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_update_profile_success(client: AsyncClient, fake_service):
    await fake_service.create_profile(None, "user-1", "Ivan", "ivan@test.com")

    response = await client.patch(
        "/api/v1/profile/user-1",
        json={"name": "Ivan Updated", "city": "Moscow"},
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
    )
    assert response.status_code == 404
