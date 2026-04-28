from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from fastapi import Request, HTTPException
import httpx


@dataclass
class AuthUser:
    user_id: str
    roles: list[str]
    email_confirmed: bool = False


class AuthProvider(ABC):
    @abstractmethod
    async def authenticate(self, token: str) -> AuthUser:
        pass


class HttpAuthProvider(AuthProvider):
    def __init__(self, auther_url: str, profiler_url: str):
        self.auther_url = auther_url
        self.profiler_url = profiler_url

    async def authenticate(self, token: str) -> AuthUser:
        import jwt
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            user_id = payload["user_id"]
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid token")

        email_confirmed = False
        roles = []

        async with httpx.AsyncClient(base_url=self.profiler_url) as client:
            auth_headers = {"Authorization": f"Bearer {token}"}
            profile_resp = await client.get(f"/api/v1/profile/{user_id}", headers=auth_headers)
            if profile_resp.status_code == 200:
                email_confirmed = profile_resp.json().get("email_confirmed", False)

            roles_resp = await client.get(f"/api/v1/profile/{user_id}/roles", headers=auth_headers)
            if roles_resp.status_code == 200:
                roles = [r["role"] for r in roles_resp.json()]

        return AuthUser(user_id=user_id, roles=roles, email_confirmed=email_confirmed)


async def get_current_user(request: Request) -> AuthUser:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authorization header")
    token = auth_header[7:]
    provider: AuthProvider = request.app.state.auth_provider
    return await provider.authenticate(token)


async def get_optional_user(request: Request) -> Optional[AuthUser]:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    token = auth_header[7:]
    provider: AuthProvider = request.app.state.auth_provider
    try:
        return await provider.authenticate(token)
    except HTTPException:
        return None
