from src.sender.sender import EmailSender
from src.services.service import NotificationService, SendError


class NotificationServiceImpl(NotificationService):
    def __init__(self, sender: EmailSender):
        self.sender = sender

    async def send_email(self, to: str, subject: str, body: str) -> None:
        try:
            await self.sender.send(to, subject, body)
        except Exception as e:
            raise SendError(f"Failed to send email to {to}: {e}") from e
