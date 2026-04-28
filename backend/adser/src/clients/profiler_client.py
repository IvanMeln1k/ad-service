from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

import httpx


@dataclass
class ProfileInfo:
    user_id: str
    name: str
    email: Optional[str] = None
    city: Optional[str] = None
    avatar_url: Optional[str] = None


class ProfilerClient(ABC):
    @abstractmethod
    async def get_profile(self, user_id: str) -> Optional[ProfileInfo]:
        pass


class HttpProfilerClient(ProfilerClient):
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def get_profile(self, user_id: str) -> Optional[ProfileInfo]:
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.get(f"/api/v1/profile/{user_id}")
            if response.status_code == 404:
                return None
            response.raise_for_status()
            data = response.json()
            return ProfileInfo(
                user_id=data["user_id"],
                name=data["name"],
                email=data.get("email"),
                city=data.get("city"),
                avatar_url=data.get("avatar_url"),
            )
