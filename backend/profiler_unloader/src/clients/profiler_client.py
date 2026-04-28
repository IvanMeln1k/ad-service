from abc import ABC, abstractmethod

import httpx


class ProfilerClient(ABC):
    @abstractmethod
    async def get_confirmation_token(self, user_id: str) -> str:
        pass


class HttpProfilerClient(ProfilerClient):
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def get_confirmation_token(self, user_id: str) -> str:
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.get(
                f"/api/v1/profile/{user_id}/email-confirmation-token"
            )
            response.raise_for_status()
            return response.json()["token"]
