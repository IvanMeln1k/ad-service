from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from fastapi import HTTPException, Request


@dataclass
class AuthUser:
    user_id: str


class AuthProvider(ABC):
    @abstractmethod
    async def authenticate(self, token: str) -> AuthUser:
        pass


class JwtAuthProvider(AuthProvider):
    async def authenticate(self, token: str) -> AuthUser:
        import jwt

        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            user_id = payload["user_id"]
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid token")
        return AuthUser(user_id=user_id)


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
