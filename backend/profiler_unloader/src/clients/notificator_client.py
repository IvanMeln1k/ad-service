from abc import ABC, abstractmethod

import httpx


class NotificatorClient(ABC):
    @abstractmethod
    async def send_email(self, to: str, subject: str, body: str) -> None:
        pass


class HttpNotificatorClient(NotificatorClient):
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def send_email(self, to: str, subject: str, body: str) -> None:
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.post(
                "/api/v1/notifications/email",
                json={"to": to, "subject": subject, "body": body},
            )
            response.raise_for_status()
