from abc import ABC, abstractmethod
import datetime
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession


class AuthData:
    def __init__(self, uid: str, password_hash: str):
        self.uid = uid
        self.password_hash = password_hash


class RefreshToken:
    def __init__(
        self, uid: str, token_hash: str, expires_at: Optional[datetime.datetime] = None
    ):
        self.uid = uid
        self.token_hash = token_hash
        self.expires_at = expires_at


class AuthRepository(ABC):
    @abstractmethod
    def create_user(self, session: AsyncSession, auth_data: AuthData) -> None:
        """Create a new user with authentication data"""
        raise NotImplementedError()

    @abstractmethod
    def get_user_auth_data(self, session: AsyncSession, uid: str) -> Optional[AuthData]:
        """Get user authentication data by user ID"""
        raise NotImplementedError()

    @abstractmethod
    def create_refresh_token(
        self, session: AsyncSession, refresh_token: RefreshToken
    ) -> None:
        """Create a new refresh token"""
        raise NotImplementedError()

    @abstractmethod
    def get_valid_refresh_token(
        self, session: AsyncSession, token_hash: str
    ) -> Optional[RefreshToken]:
        """Get valid refresh token by hash (checking expiration)"""
        raise NotImplementedError()

    @abstractmethod
    def delete_refresh_tokens(
        self,
        session: AsyncSession,
        uid: str,
        token_hashes: Optional[List[str]] = None,
        except_token_hash: Optional[str] = None,
    ) -> int:
        """
        Delete refresh tokens with flexible filtering

        Args:
            session: Database session
            uid: User ID
            token_hashes: List of specific token hashes to delete (if provided)
            except_token_hash: Delete all tokens except this one (if provided)

        Returns:
            Number of tokens deleted
        """
        raise NotImplementedError()

    @abstractmethod
    def delete_user(self, session: AsyncSession, uid: str) -> bool:
        """Delete user and all their refresh tokens"""
        raise NotImplementedError()

    @abstractmethod
    def update_user_password(
        self, session: AsyncSession, uid: str, new_password_hash: str
    ) -> None:
        """Update user password hash"""
        raise NotImplementedError()
