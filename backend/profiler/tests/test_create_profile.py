import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_profile_success(client: AsyncClient, fake_service):
    response = await client.post(
        "/api/v1/profile",
        json={"user_id": "user-1", "name": "Ivan", "email": "ivan@test.com"},
    )
    assert response.status_code == 201
    assert response.json()["user_id"] == "user-1"
    assert "user-1" in fake_service.profiles


@pytest.mark.asyncio
async def test_create_profile_missing_fields(client: AsyncClient):
    response = await client.post(
        "/api/v1/profile",
        json={"user_id": "user-1"},
    )
    assert response.status_code == 422
