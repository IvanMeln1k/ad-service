import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_roles_empty(client: AsyncClient, fake_roles_service):
    response = await client.get("/api/v1/profile/user-1/roles")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_roles_with_roles(client: AsyncClient, fake_roles_service):
    fake_roles_service.roles["user-1"] = ["MODERATOR"]

    response = await client.get("/api/v1/profile/user-1/roles")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["role"] == "MODERATOR"
    assert "assigned_at" in data[0]
