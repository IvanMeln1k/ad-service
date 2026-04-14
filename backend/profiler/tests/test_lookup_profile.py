import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_lookup_by_email_found(client: AsyncClient, fake_service):
    await fake_service.create_profile(None, "user-1", "Ivan", "ivan@test.com")

    response = await client.get("/api/v1/profile/lookup?email=ivan@test.com")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["user_id"] == "user-1"


@pytest.mark.asyncio
async def test_lookup_by_email_not_found(client: AsyncClient):
    response = await client.get("/api/v1/profile/lookup?email=nobody@test.com")
    assert response.status_code == 200
    assert response.json() == []
