import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_confirm_email_success(client: AsyncClient, fake_service, fake_email_service):
    await fake_service.create_profile(None, "user-1", "Ivan", "ivan@test.com")
    token = await fake_email_service.create_email_confirmation_token(None, "user-1")

    response = await client.post(
        "/api/v1/email-confirmation",
        json={"token": token},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "confirmed"
    assert fake_service.profiles["user-1"].email_confirmed is True


@pytest.mark.asyncio
async def test_confirm_email_invalid_token(client: AsyncClient):
    response = await client.post(
        "/api/v1/email-confirmation",
        json={"token": "invalid-token"},
    )
    assert response.status_code == 400
