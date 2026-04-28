import datetime

import pytest
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport

from src.clients.auther_client import AutherClient, AuthTokens, InvalidCredentialsError
from src.clients.profiler_client import ProfilerClient, EmailAlreadyTakenError
from src.services.registration_service import RegistrationServiceImpl
from src.routers import register, login, logout, confirm_email


class FakeAutherClient(AutherClient):
    def __init__(self):
        self.users: dict[str, str] = {}
        self.deleted_tokens: list[dict] = []

    async def create_user(self, user_id: str, password: str) -> AuthTokens:
        self.users[user_id] = password
        return AuthTokens(
            access_token=f"access-{user_id}",
            refresh_token=f"refresh-{user_id}",
            refresh_token_expires_at=datetime.datetime(2026, 2, 1),
        )

    async def delete_user(self, user_id: str) -> None:
        self.users.pop(user_id, None)

    async def authenticate(self, user_id: str, password: str) -> AuthTokens:
        if user_id not in self.users or self.users[user_id] != password:
            raise InvalidCredentialsError("Invalid credentials")
        return AuthTokens(
            access_token=f"access-{user_id}",
            refresh_token=f"refresh-{user_id}",
            refresh_token_expires_at=datetime.datetime(2026, 2, 1),
        )

    async def delete_refresh_tokens(self, user_id: str, refresh_tokens: list[str]) -> int:
        self.deleted_tokens.append({"user_id": user_id, "tokens": refresh_tokens})
        return len(refresh_tokens)


class FakeProfilerClient(ProfilerClient):
    def __init__(self):
        self.profiles: dict[str, dict] = {}
        self.taken_emails: set[str] = set()
        self.confirmed_tokens: list[str] = []

    async def create_profile(self, user_id: str, name: str, email: str) -> None:
        if email in self.taken_emails:
            raise EmailAlreadyTakenError(f"Email {email} already taken")
        self.profiles[user_id] = {"name": name, "email": email}

    async def delete_profile(self, user_id: str) -> None:
        self.profiles.pop(user_id, None)

    async def lookup_by_email(self, email: str) -> list[dict]:
        return [
            {"user_id": uid, "name": p["name"]}
            for uid, p in self.profiles.items()
            if p["email"] == email
        ]

    async def confirm_email(self, token: str) -> None:
        if token == "invalid-token":
            raise ValueError("Invalid token")
        self.confirmed_tokens.append(token)


@pytest.fixture
def fake_auther():
    return FakeAutherClient()


@pytest.fixture
def fake_profiler():
    return FakeProfilerClient()


@pytest.fixture
def app(fake_auther, fake_profiler):
    test_app = FastAPI()
    test_app.state.registration_service = RegistrationServiceImpl(
        auther_client=fake_auther,
        profiler_client=fake_profiler,
    )
    test_app.include_router(register.router)
    test_app.include_router(login.router)
    test_app.include_router(logout.router)
    test_app.include_router(confirm_email.router)
    return test_app


@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
