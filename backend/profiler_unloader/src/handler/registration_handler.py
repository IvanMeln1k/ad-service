import logging

from src.clients.profiler_client import ProfilerClient
from src.clients.notificator_client import NotificatorClient
from src.config import config

logger = logging.getLogger(__name__)


class RegistrationHandler:
    def __init__(
        self,
        profiler_client: ProfilerClient,
        notificator_client: NotificatorClient,
    ):
        self.profiler_client = profiler_client
        self.notificator_client = notificator_client

    async def handle(self, event: dict) -> None:
        event_type = event.get("event")
        if event_type != "user.registered":
            logger.warning("Unknown event type: %s", event_type)
            return

        user_id = event["user_id"]
        email = event["email"]
        name = event["name"]

        logger.info("Processing registration for user %s (%s)", user_id, email)

        token = await self.profiler_client.get_confirmation_token(user_id)

        subject = "Подтверждение email"
        body = (
            f"<h1>Здравствуйте, {name}!</h1>"
            f"<p>Для подтверждения email перейдите по ссылке:</p>"
            f"<p><a href=\"{config.FRONTEND_URL}/confirm-email?token={token}\">"
            f"Подтвердить email</a></p>"
        )

        await self.notificator_client.send_email(email, subject, body)
        logger.info("Confirmation email sent to %s", email)
