import pytest
from httpx import AsyncClient


async def test_register_success(client: AsyncClient, fake_auther, fake_profiler):
    response = await client.post(
        "/api/v1/register",
        json={"email": "ivan@test.com", "name": "Ivan", "password": "pass123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert "user_id" in data
    assert "access_token" in data
    assert "refresh_token" in data

    user_id = data["user_id"]
    assert user_id in fake_auther.users
    assert user_id in fake_profiler.profiles
    assert fake_profiler.profiles[user_id]["email"] == "ivan@test.com"


async def test_register_email_already_taken(client: AsyncClient, fake_auther, fake_profiler):
    fake_profiler.taken_emails.add("taken@test.com")

    response = await client.post(
        "/api/v1/register",
        json={"email": "taken@test.com", "name": "Ivan", "password": "pass123"},
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "Email already taken"

    # Compensation: auther user should be deleted
    assert len(fake_auther.users) == 0


async def test_register_invalid_email(client: AsyncClient):
    response = await client.post(
        "/api/v1/register",
        json={"email": "not-an-email", "name": "Ivan", "password": "pass123"},
    )
    assert response.status_code == 422


async def test_register_missing_fields(client: AsyncClient):
    response = await client.post(
        "/api/v1/register",
        json={"email": "ivan@test.com"},
    )
    assert response.status_code == 422


# --- Login ---


async def test_login_success(client: AsyncClient, fake_auther, fake_profiler):
    # First register
    await client.post(
        "/api/v1/register",
        json={"email": "ivan@test.com", "name": "Ivan", "password": "pass123"},
    )

    # Then login
    response = await client.post(
        "/api/v1/login",
        json={"email": "ivan@test.com", "password": "pass123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "user_id" in data
    assert "access_token" in data
    assert "refresh_token" in data


async def test_login_wrong_password(client: AsyncClient, fake_auther, fake_profiler):
    await client.post(
        "/api/v1/register",
        json={"email": "ivan@test.com", "name": "Ivan", "password": "pass123"},
    )

    response = await client.post(
        "/api/v1/login",
        json={"email": "ivan@test.com", "password": "wrong"},
    )
    assert response.status_code == 401


async def test_login_unknown_email(client: AsyncClient):
    response = await client.post(
        "/api/v1/login",
        json={"email": "unknown@test.com", "password": "pass123"},
    )
    assert response.status_code == 401


# --- Logout ---


async def test_logout_success(client: AsyncClient, fake_auther, fake_profiler):
    reg = await client.post(
        "/api/v1/register",
        json={"email": "ivan@test.com", "name": "Ivan", "password": "pass123"},
    )
    data = reg.json()

    response = await client.post(
        "/api/v1/logout",
        json={
            "user_id": data["user_id"],
            "refresh_token": data["refresh_token"]["token"],
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert len(fake_auther.deleted_tokens) == 1


# --- Confirm Email ---


async def test_confirm_email_success(client: AsyncClient, fake_profiler):
    response = await client.post(
        "/api/v1/confirm-email",
        json={"token": "valid-token-123"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "confirmed"
    assert "valid-token-123" in fake_profiler.confirmed_tokens


async def test_confirm_email_invalid_token(client: AsyncClient):
    response = await client.post(
        "/api/v1/confirm-email",
        json={"token": "invalid-token"},
    )
    assert response.status_code == 400
