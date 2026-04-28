import datetime

import pytest
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
import jwt

from src.repository.repository import ProfileData, ProfileLookupData, RoleData
from src.events.publisher import EventPublisher
from src.auth import AuthProvider, AuthUser
from src.services.services import (
    ProfileService,
    RolesService,
    EmailConfirmationService,
    ProfileNotFoundError,
    InvalidConfirmationTokenError,
)
from src.routers import (
    create_profile,
    list_profiles,
    lookup_profile,
    get_profile,
    update_profile,
    delete_profile,
    get_roles,
    manage_roles,
    email_confirmation_token,
    confirm_email,
)


class FakeEventPublisher(EventPublisher):
    def __init__(self):
        self.events: list[dict] = []

    async def publish(self, topic, key, value):
        self.events.append({"topic": topic, "key": key, "value": value})

    async def start(self):
        pass

    async def stop(self):
        pass


class FakeProfileService(ProfileService):
    def __init__(self):
        self.profiles: dict[str, ProfileData] = {}

    async def create_profile(self, session, user_id, name, email):
        self.profiles[user_id] = ProfileData(
            user_id=user_id,
            name=name,
            email=email,
            created_at=datetime.datetime(2026, 1, 1),
        )

    async def get_profile(self, session, user_id):
        if user_id not in self.profiles:
            raise ProfileNotFoundError(f"Profile {user_id} not found")
        return self.profiles[user_id]

    async def update_profile(self, session, user_id, name=None, city=None):
        if user_id not in self.profiles:
            raise ProfileNotFoundError(f"Profile {user_id} not found")
        p = self.profiles[user_id]
        if name is not None:
            p.name = name
        if city is not None:
            p.city = city
        return p

    async def delete_profile(self, session, user_id):
        if user_id not in self.profiles:
            raise ProfileNotFoundError(f"Profile {user_id} not found")
        del self.profiles[user_id]

    async def find_profiles_by_email(self, session, email):
        return [
            ProfileLookupData(user_id=p.user_id, name=p.name, avatar_url=p.avatar_url)
            for p in self.profiles.values()
            if p.email == email
        ]

    async def list_profiles(self, session, limit=20, offset=0):
        all_profiles = list(self.profiles.values())
        return all_profiles[offset : offset + limit]


class FakeRolesService(RolesService):
    def __init__(self):
        self.roles: dict[str, list[str]] = {}

    async def get_roles(self, session, user_id):
        return [
            RoleData(role=r, assigned_at=datetime.datetime(2026, 1, 1))
            for r in self.roles.get(user_id, [])
        ]

    async def assign_role(self, session, user_id, role):
        if user_id not in self.roles:
            self.roles[user_id] = []
        if role not in self.roles[user_id]:
            self.roles[user_id].append(role)
        return await self.get_roles(session, user_id)

    async def remove_role(self, session, user_id, role):
        if user_id in self.roles and role in self.roles[user_id]:
            self.roles[user_id].remove(role)
        return await self.get_roles(session, user_id)


class FakeAuthProvider(AuthProvider):
    def __init__(self):
        self.default_user_id = "user-1"

    async def authenticate(self, token: str) -> AuthUser:
        payload = jwt.decode(token, options={"verify_signature": False})
        return AuthUser(user_id=payload.get("user_id", self.default_user_id))


class FakeEmailConfirmationService(EmailConfirmationService):
    def __init__(self, profile_service: FakeProfileService):
        self.profile_service = profile_service
        self.tokens: dict[str, str] = {}

    async def create_email_confirmation_token(self, session, user_id):
        if user_id not in self.profile_service.profiles:
            raise ProfileNotFoundError(f"Profile {user_id} not found")
        token = f"token-{user_id}"
        self.tokens[token] = user_id
        return token

    async def confirm_email(self, session, token):
        if token not in self.tokens:
            raise InvalidConfirmationTokenError("Token not found")
        user_id = self.tokens[token]
        self.profile_service.profiles[user_id].email_confirmed = True


@pytest.fixture
def fake_service():
    return FakeProfileService()


@pytest.fixture
def fake_roles_service():
    return FakeRolesService()


@pytest.fixture
def fake_email_service(fake_service):
    return FakeEmailConfirmationService(fake_service)


@pytest.fixture
def fake_auth():
    return FakeAuthProvider()


@pytest.fixture
def app(fake_service, fake_roles_service, fake_email_service, fake_auth):
    test_app = FastAPI()
    test_app.state.profile_service = fake_service
    test_app.state.roles_service = fake_roles_service
    test_app.state.email_service = fake_email_service
    test_app.state.auth_provider = fake_auth
    test_app.state.session_factory = FakeSessionFactory()

    # Static paths first, then parameterized
    test_app.include_router(create_profile.router)
    test_app.include_router(list_profiles.router)
    test_app.include_router(lookup_profile.router)
    test_app.include_router(confirm_email.router)
    test_app.include_router(get_profile.router)
    test_app.include_router(update_profile.router)
    test_app.include_router(delete_profile.router)
    test_app.include_router(get_roles.router)
    test_app.include_router(manage_roles.router)
    test_app.include_router(email_confirmation_token.router)

    return test_app


class FakeSessionFactory:
    def __call__(self):
        return FakeSession()


class FakeSession:
    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass

    async def close(self):
        pass


@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


def make_auth_headers(user_id: str) -> dict[str, str]:
    token = jwt.encode({"user_id": user_id}, key="test-secret", algorithm="HS256")
    return {"Authorization": f"Bearer {token}"}
