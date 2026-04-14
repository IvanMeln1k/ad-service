import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_token_success(client: AsyncClient, fake_service):
    await fake_service.create_profile(None, "user-1", "Ivan", "ivan@test.com")

    response = await client.get("/api/v1/profile/user-1/email-confirmation-token")
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert data["token"] == "token-user-1"


@pytest.mark.asyncio
async def test_get_token_profile_not_found(client: AsyncClient):
    response = await client.get("/api/v1/profile/nonexistent/email-confirmation-token")
    assert response.status_code == 404
