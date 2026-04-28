import pytest

from src.handler.registration_handler import RegistrationHandler


async def test_handle_user_registered(handler: RegistrationHandler, fake_profiler, fake_notificator):
    fake_profiler.tokens["user-1"] = "confirm-token-abc"

    event = {
        "event": "user.registered",
        "user_id": "user-1",
        "email": "ivan@test.com",
        "name": "Ivan",
    }

    await handler.handle(event)

    assert len(fake_notificator.sent) == 1
    email = fake_notificator.sent[0]
    assert email["to"] == "ivan@test.com"
    assert email["subject"] == "Подтверждение email"
    assert "confirm-token-abc" in email["body"]
    assert "Ivan" in email["body"]


async def test_handle_unknown_event(handler: RegistrationHandler, fake_notificator):
    event = {
        "event": "unknown.event",
        "user_id": "user-1",
    }

    await handler.handle(event)

    assert len(fake_notificator.sent) == 0


async def test_handle_multiple_registrations(handler: RegistrationHandler, fake_notificator):
    for i in range(3):
        event = {
            "event": "user.registered",
            "user_id": f"user-{i}",
            "email": f"user{i}@test.com",
            "name": f"User {i}",
        }
        await handler.handle(event)

    assert len(fake_notificator.sent) == 3
    assert fake_notificator.sent[0]["to"] == "user0@test.com"
    assert fake_notificator.sent[2]["to"] == "user2@test.com"
