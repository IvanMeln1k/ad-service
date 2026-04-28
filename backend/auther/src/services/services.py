from abc import ABC, abstractmethod
import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel


class TokenInfo(BaseModel):
    token: str
    expires_at: Optional[datetime.datetime] = None


class Tokens(BaseModel):
    access_token: str
    refresh_token: TokenInfo


class UserAlreadyExistsError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class InvalidRefreshTokenError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class AuthService(ABC):
    @abstractmethod
    def create_user(self, session: AsyncSession, user_id: str, password: str) -> Tokens:
        """Create a new user and return access/refresh tokens"""
        raise NotImplementedError()

    @abstractmethod
    def authenticate_user(
        self, session: AsyncSession, user_id: str, password: str
    ) -> Tokens:
        """Authenticate user with password and return tokens"""
        raise NotImplementedError()

    @abstractmethod
    def refresh_tokens(self, session: AsyncSession, refresh_token: str) -> Tokens:
        """Refresh access token using refresh token"""
        raise NotImplementedError()

    @abstractmethod
    def delete_refresh_tokens(
        self,
        session: AsyncSession,
        user_id: str,
        refresh_tokens: Optional[list[str]] = None,
        except_token: Optional[str] = None,
    ) -> int:
        """
        Delete refresh tokens with flexible filtering

        Args:
            session: Database session
            user_id: User ID
            refresh_tokens: List of specific refresh tokens to delete
            except_token: Delete all tokens except this one

        Returns:
            Number of tokens deleted
        """
        raise NotImplementedError()

    @abstractmethod
    def delete_user(self, session: AsyncSession, user_id: str) -> None:
        """Delete user and all their tokens"""
        raise NotImplementedError()

    @abstractmethod
    def change_password(
        self, session: AsyncSession, user_id: str, old_password: str, new_password: str
    ) -> Tokens:
        """Change user password and return new tokens"""
        raise NotImplementedError()
