import pytest
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport

from src.services.service import NotificationService
from src.routers import send_email


class FakeEmailSender:
    def __init__(self):
        self.sent: list[dict] = []

    async def send(self, to: str, subject: str, body: str) -> None:
        self.sent.append({"to": to, "subject": subject, "body": body})


class FakeNotificationService(NotificationService):
    def __init__(self):
        self.sent: list[dict] = []

    async def send_email(self, to: str, subject: str, body: str) -> None:
        self.sent.append({"to": to, "subject": subject, "body": body})


@pytest.fixture
def fake_service():
    return FakeNotificationService()


@pytest.fixture
def app(fake_service):
    test_app = FastAPI()
    test_app.state.notification_service = fake_service
    test_app.include_router(send_email.router)
    return test_app


@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
