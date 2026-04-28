from abc import ABC, abstractmethod


class SendError(Exception):
    pass


class NotificationService(ABC):
    @abstractmethod
    async def send_email(self, to: str, subject: str, body: str) -> None:
        pass
