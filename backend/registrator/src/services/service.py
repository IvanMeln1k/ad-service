from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
import datetime


@dataclass
class RegistrationResult:
    user_id: str
    access_token: str
    refresh_token: str
    refresh_token_expires_at: Optional[datetime.datetime] = None


@dataclass
class LoginResult:
    user_id: str
    access_token: str
    refresh_token: str
    refresh_token_expires_at: Optional[datetime.datetime] = None


class EmailAlreadyTakenError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class InvalidTokenError(Exception):
    pass


class RegistrationService(ABC):
    @abstractmethod
    async def register(self, email: str, name: str, password: str) -> RegistrationResult:
        pass

    @abstractmethod
    async def login(self, email: str, password: str) -> LoginResult:
        pass

    @abstractmethod
    async def logout(self, user_id: str, refresh_token: str) -> None:
        pass

    @abstractmethod
    async def confirm_email(self, token: str) -> None:
        pass
