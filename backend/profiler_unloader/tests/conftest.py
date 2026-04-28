import pytest

from src.clients.profiler_client import ProfilerClient
from src.clients.notificator_client import NotificatorClient
from src.handler.registration_handler import RegistrationHandler


class FakeProfilerClient(ProfilerClient):
    def __init__(self):
        self.tokens: dict[str, str] = {}

    async def get_confirmation_token(self, user_id: str) -> str:
        return self.tokens.get(user_id, f"token-{user_id}")


class FakeNotificatorClient(NotificatorClient):
    def __init__(self):
        self.sent: list[dict] = []

    async def send_email(self, to: str, subject: str, body: str) -> None:
        self.sent.append({"to": to, "subject": subject, "body": body})


@pytest.fixture
def fake_profiler():
    return FakeProfilerClient()


@pytest.fixture
def fake_notificator():
    return FakeNotificatorClient()


@pytest.fixture
def handler(fake_profiler, fake_notificator):
    return RegistrationHandler(fake_profiler, fake_notificator)
