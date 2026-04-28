import pytest
from httpx import AsyncClient
from tests.conftest import make_auth_headers


@pytest.mark.asyncio
async def test_lookup_by_email_found(client: AsyncClient, fake_service, fake_roles_service):
    await fake_service.create_profile(None, "user-1", "Ivan", "ivan@test.com")
    fake_roles_service.roles["admin"] = ["ADMIN"]

    response = await client.get("/api/v1/profile/lookup?email=ivan@test.com", headers=make_auth_headers("admin"))
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["user_id"] == "user-1"


@pytest.mark.asyncio
async def test_lookup_by_email_not_found(client: AsyncClient, fake_roles_service):
    fake_roles_service.roles["admin"] = ["ADMIN"]
    response = await client.get("/api/v1/profile/lookup?email=nobody@test.com")
    assert response.status_code == 200
    assert response.json() == []
