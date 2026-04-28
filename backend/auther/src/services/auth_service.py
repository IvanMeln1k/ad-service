import logging
import secrets
import hashlib
import jwt
from typing import Optional
import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from .services import (
    AuthService,
    Tokens,
    TokenInfo,
    UserAlreadyExistsError,
    UserNotFoundError,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
)
from ..repository.repository import AuthRepository, AuthData, RefreshToken

logger = logging.getLogger(__name__)


class AuthenticationService(AuthService):
    def __init__(
        self,
        repository: AuthRepository,
        jwt_secret: str,
        access_token_ttl: int = 3600,  # 1 hour
        refresh_token_ttl: int = 86400 * 30,  # 30 days
    ):
        self.repository = repository
        self.jwt_secret = jwt_secret
        self.access_token_ttl = access_token_ttl
        self.refresh_token_ttl = refresh_token_ttl

    def _hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def _generate_token_hash(self, token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()

    def _generate_access_token(self, user_id: str) -> str:
        payload = {
            "user_id": user_id,
            "exp": datetime.datetime.utcnow()
            + datetime.timedelta(seconds=self.access_token_ttl),
            "iat": datetime.datetime.utcnow(),
        }
        return jwt.encode(payload, self.jwt_secret, algorithm="HS256")

    def _generate_refresh_token(self) -> str:
        return secrets.token_urlsafe(64)

    def _calculate_expires_at(
        self, ttl: Optional[int] = None
    ) -> Optional[datetime.datetime]:
        if ttl is None:
            return None
        return datetime.datetime.utcnow() + datetime.timedelta(seconds=ttl)

    async def create_user(
        self, session: AsyncSession, user_id: str, password: str
    ) -> Tokens:
        password_hash = self._hash_password(password)
        auth_data = AuthData(uid=user_id, password_hash=password_hash)

        refresh_token = self._generate_refresh_token()
        refresh_token_hash = self._generate_token_hash(refresh_token)
        expires_at = self._calculate_expires_at(self.refresh_token_ttl)

        refresh_token_data = RefreshToken(
            uid=user_id, token_hash=refresh_token_hash, expires_at=expires_at
        )

        try:
            await self.repository.create_user(session, auth_data)
            await self.repository.create_refresh_token(session, refresh_token_data)
            await session.commit()
        except ValueError as e:
            await session.rollback()
            raise UserAlreadyExistsError(f"User {user_id} already exists") from e
        except Exception:
            await session.rollback()
            raise

        access_token = self._generate_access_token(user_id)
        return Tokens(
            access_token=access_token,
            refresh_token=TokenInfo(
                token=refresh_token,
                expires_at=expires_at
            )
        )

    async def authenticate_user(
        self, session: AsyncSession, user_id: str, password: str
    ) -> Tokens:
        auth_data = await self.repository.get_user_auth_data(session, user_id)
        if not auth_data:
            raise InvalidCredentialsError("Invalid user ID or password")

        password_hash = self._hash_password(password)
        if auth_data.password_hash != password_hash:
            raise InvalidCredentialsError("Invalid user ID or password")

        refresh_token = self._generate_refresh_token()
        refresh_token_hash = self._generate_token_hash(refresh_token)
        expires_at = self._calculate_expires_at(self.refresh_token_ttl)

        refresh_token_data = RefreshToken(
            uid=user_id, token_hash=refresh_token_hash, expires_at=expires_at
        )

        try:
            await self.repository.create_refresh_token(session, refresh_token_data)
            await session.commit()
        except Exception:
            await session.rollback()
            raise

        access_token = self._generate_access_token(user_id)
        return Tokens(
            access_token=access_token,
            refresh_token=TokenInfo(
                token=refresh_token,
                expires_at=expires_at
            )
        )

    async def refresh_tokens(self, session: AsyncSession, refresh_token: str) -> Tokens:
        refresh_token_hash = self._generate_token_hash(refresh_token)
        token_data = await self.repository.get_valid_refresh_token(
            session, refresh_token_hash
        )

        if not token_data:
            raise InvalidRefreshTokenError("Invalid or expired refresh token")

        new_refresh_token = self._generate_refresh_token()
        new_refresh_token_hash = self._generate_token_hash(new_refresh_token)
        expires_at = self._calculate_expires_at(self.refresh_token_ttl)

        new_refresh_token_data = RefreshToken(
            uid=token_data.uid, token_hash=new_refresh_token_hash, expires_at=expires_at
        )

        try:
            await self.repository.create_refresh_token(session, new_refresh_token_data)
            await self.repository.delete_refresh_tokens(
                session, token_data.uid, except_token_hash=new_refresh_token_hash
            )
            await session.commit()
        except Exception:
            await session.rollback()
            raise

        access_token = self._generate_access_token(token_data.uid)
        return Tokens(
            access_token=access_token,
            refresh_token=TokenInfo(
                token=new_refresh_token,
                expires_at=expires_at
            )
        )

    async def delete_refresh_tokens(
        self,
        session: AsyncSession,
        user_id: str,
        refresh_tokens: Optional[list[str]] = None,
        except_token: Optional[str] = None,
    ) -> int:
        token_hashes = None
        if refresh_tokens:
            token_hashes = [
                self._generate_token_hash(token) for token in refresh_tokens
            ]

        except_token_hash = None
        if except_token:
            except_token_hash = self._generate_token_hash(except_token)

        try:
            result = await self.repository.delete_refresh_tokens(
                session, user_id, token_hashes, except_token_hash
            )
            await session.commit()
            return result
        except Exception:
            await session.rollback()
            raise

    async def delete_user(self, session: AsyncSession, user_id: str) -> None:
        try:
            deleted = await self.repository.delete_user(session, user_id)
            if not deleted:
                raise UserNotFoundError(f"User {user_id} not found")
            await session.commit()
        except UserNotFoundError:
            raise
        except Exception:
            await session.rollback()
            raise

    async def change_password(
        self, session: AsyncSession, user_id: str, old_password: str, new_password: str
    ) -> Tokens:
        auth_data = await self.repository.get_user_auth_data(session, user_id)
        if not auth_data:
            raise InvalidCredentialsError("Invalid user ID or password")

        old_password_hash = self._hash_password(old_password)
        if auth_data.password_hash != old_password_hash:
            raise InvalidCredentialsError("Invalid user ID or password")

        new_password_hash = self._hash_password(new_password)

        refresh_token = self._generate_refresh_token()
        refresh_token_hash = self._generate_token_hash(refresh_token)
        expires_at = self._calculate_expires_at(self.refresh_token_ttl)

        refresh_token_data = RefreshToken(
            uid=user_id, token_hash=refresh_token_hash, expires_at=expires_at
        )

        try:
            await self.repository.update_user_password(
                session, user_id, new_password_hash
            )
            await self.repository.delete_refresh_tokens(session, user_id)
            await self.repository.create_refresh_token(session, refresh_token_data)
            await session.commit()
        except Exception:
            await session.rollback()
            raise

        access_token = self._generate_access_token(user_id)
        return Tokens(
            access_token=access_token,
            refresh_token=TokenInfo(
                token=refresh_token,
                expires_at=expires_at
            )
        )
