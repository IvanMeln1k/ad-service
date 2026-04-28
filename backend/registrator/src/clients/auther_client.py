from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
import datetime

import httpx


@dataclass
class AuthTokens:
    access_token: str
    refresh_token: str
    refresh_token_expires_at: Optional[datetime.datetime] = None


class InvalidCredentialsError(Exception):
    pass


class AutherClient(ABC):
    @abstractmethod
    async def create_user(self, user_id: str, password: str) -> AuthTokens:
        pass

    @abstractmethod
    async def delete_user(self, user_id: str) -> None:
        pass

    @abstractmethod
    async def authenticate(self, user_id: str, password: str) -> AuthTokens:
        pass

    @abstractmethod
    async def delete_refresh_tokens(self, user_id: str, refresh_tokens: list[str]) -> int:
        pass


class HttpAutherClient(AutherClient):
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def create_user(self, user_id: str, password: str) -> AuthTokens:
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.post(
                "/users",
                params={"user_id": user_id, "password": password},
            )
            response.raise_for_status()
            data = response.json()
            return AuthTokens(
                access_token=data["access_token"],
                refresh_token=data["refresh_token"]["token"],
                refresh_token_expires_at=data["refresh_token"].get("expires_at"),
            )

    async def delete_user(self, user_id: str) -> None:
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.delete(f"/users/{user_id}")
            response.raise_for_status()

    async def authenticate(self, user_id: str, password: str) -> AuthTokens:
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.post(
                "/tokens",
                params={"user_id": user_id, "password": password},
            )
            if response.status_code == 401:
                raise InvalidCredentialsError("Invalid credentials")
            response.raise_for_status()
            data = response.json()
            return AuthTokens(
                access_token=data["access_token"],
                refresh_token=data["refresh_token"]["token"],
                refresh_token_expires_at=data["refresh_token"].get("expires_at"),
            )

    async def delete_refresh_tokens(self, user_id: str, refresh_tokens: list[str]) -> int:
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.delete(
                "/tokens",
                params={"user_id": user_id, "refresh_tokens": refresh_tokens},
            )
            response.raise_for_status()
            return response.json()["deleted_tokens"]
