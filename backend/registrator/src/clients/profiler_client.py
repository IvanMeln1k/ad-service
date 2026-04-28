from abc import ABC, abstractmethod

import httpx


class EmailAlreadyTakenError(Exception):
    pass


class ProfilerClient(ABC):
    @abstractmethod
    async def create_profile(self, user_id: str, name: str, email: str) -> None:
        pass

    @abstractmethod
    async def delete_profile(self, user_id: str) -> None:
        pass

    @abstractmethod
    async def lookup_by_email(self, email: str) -> list[dict]:
        pass

    @abstractmethod
    async def confirm_email(self, token: str) -> None:
        pass


class HttpProfilerClient(ProfilerClient):
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def create_profile(self, user_id: str, name: str, email: str) -> None:
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.post(
                "/api/v1/profile",
                json={"user_id": user_id, "name": name, "email": email},
            )
            if response.status_code == 409:
                raise EmailAlreadyTakenError(f"Email {email} already taken")
            response.raise_for_status()

    async def delete_profile(self, user_id: str) -> None:
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.delete(f"/api/v1/profile/{user_id}")
            response.raise_for_status()

    async def lookup_by_email(self, email: str) -> list[dict]:
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.get(
                "/api/v1/profile/lookup",
                params={"email": email},
            )
            response.raise_for_status()
            return response.json()

    async def confirm_email(self, token: str) -> None:
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.post(
                "/api/v1/email-confirmation",
                json={"token": token},
            )
            if response.status_code == 400:
                detail = response.json().get("detail", "")
                raise ValueError(detail)
            if response.status_code == 409:
                raise EmailAlreadyTakenError("Email already confirmed")
            response.raise_for_status()
