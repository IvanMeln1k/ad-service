import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_profiles_empty(client: AsyncClient):
    response = await client.get("/api/v1/profile")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_list_profiles_with_data(client: AsyncClient, fake_service):
    await fake_service.create_profile(None, "user-1", "Ivan", "ivan@test.com")
    await fake_service.create_profile(None, "user-2", "Oleg", "oleg@test.com")

    response = await client.get("/api/v1/profile")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_list_profiles_pagination(client: AsyncClient, fake_service):
    await fake_service.create_profile(None, "user-1", "Ivan", "ivan@test.com")
    await fake_service.create_profile(None, "user-2", "Oleg", "oleg@test.com")

    response = await client.get("/api/v1/profile?limit=1&offset=0")
    assert response.status_code == 200
    assert len(response.json()) == 1
