import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_send_email_success(client: AsyncClient, fake_service):
    response = await client.post(
        "/api/v1/notifications/email",
        json={
            "to": "user@example.com",
            "subject": "Test Subject",
            "body": "<p>Hello</p>",
        },
    )
    assert response.status_code == 200
    assert response.json() == {"status": "sent"}
    assert len(fake_service.sent) == 1
    assert fake_service.sent[0]["to"] == "user@example.com"
    assert fake_service.sent[0]["subject"] == "Test Subject"
    assert fake_service.sent[0]["body"] == "<p>Hello</p>"


@pytest.mark.asyncio
async def test_send_email_invalid_email(client: AsyncClient):
    response = await client.post(
        "/api/v1/notifications/email",
        json={
            "to": "not-an-email",
            "subject": "Test",
            "body": "Hello",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_send_email_missing_subject(client: AsyncClient):
    response = await client.post(
        "/api/v1/notifications/email",
        json={
            "to": "user@example.com",
            "body": "Hello",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_send_email_missing_body(client: AsyncClient):
    response = await client.post(
        "/api/v1/notifications/email",
        json={
            "to": "user@example.com",
            "subject": "Test",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_send_email_empty_json(client: AsyncClient):
    response = await client.post(
        "/api/v1/notifications/email",
        json={},
    )
    assert response.status_code == 422
