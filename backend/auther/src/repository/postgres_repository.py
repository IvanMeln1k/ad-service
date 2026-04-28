import logging
from typing import Optional, List
import datetime

from sqlalchemy import select, delete, update, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from .repository import AuthRepository, AuthData, RefreshToken
from src.models.models import UserAuth, RefreshToken as RefreshTokenModel

logger = logging.getLogger(__name__)


class PostgresAuthRepository(AuthRepository):
    def __init__(self):
        pass

    async def create_user(self, session: AsyncSession, auth_data: AuthData) -> None:
        user_auth = UserAuth(uid=auth_data.uid, password_hash=auth_data.password_hash)
        session.add(user_auth)
        try:
            await session.flush()
        except IntegrityError:
            raise ValueError(f"User {auth_data.uid} already exists")

    async def get_user_auth_data(
        self, session: AsyncSession, uid: str
    ) -> Optional[AuthData]:
        stmt = select(UserAuth).where(UserAuth.uid == uid)
        result = await session.execute(stmt)
        user_auth = result.scalar_one_or_none()

        if user_auth:
            return AuthData(uid=user_auth.uid, password_hash=user_auth.password_hash)
        return None

    async def create_refresh_token(
        self, session: AsyncSession, refresh_token: RefreshToken
    ) -> None:
        token_model = RefreshTokenModel(
            token_hash=refresh_token.token_hash,
            uid=refresh_token.uid,
            expires_at=refresh_token.expires_at,
        )
        session.add(token_model)

    async def get_valid_refresh_token(
        self, session: AsyncSession, token_hash: str
    ) -> Optional[RefreshToken]:
        stmt = select(RefreshTokenModel).where(
            and_(
                RefreshTokenModel.token_hash == token_hash,
                or_(
                    RefreshTokenModel.expires_at.is_(None),
                    RefreshTokenModel.expires_at > datetime.datetime.utcnow(),
                ),
            )
        )
        result = await session.execute(stmt)
        token_model = result.scalar_one_or_none()

        if token_model:
            return RefreshToken(
                uid=token_model.uid,
                token_hash=token_model.token_hash,
                expires_at=token_model.expires_at,
            )
        return None

    async def delete_refresh_tokens(
        self,
        session: AsyncSession,
        uid: str,
        token_hashes: Optional[List[str]] = None,
        except_token_hash: Optional[str] = None,
    ) -> int:
        conditions = [RefreshTokenModel.uid == uid]

        if token_hashes:
            conditions.append(RefreshTokenModel.token_hash.in_(token_hashes))
        elif except_token_hash:
            conditions.append(RefreshTokenModel.token_hash != except_token_hash)

        stmt = delete(RefreshTokenModel).where(and_(*conditions))
        result = await session.execute(stmt)
        return result.rowcount or 0

    async def delete_user(self, session: AsyncSession, uid: str) -> bool:
        await self.delete_refresh_tokens(session, uid)
        stmt = delete(UserAuth).where(UserAuth.uid == uid)
        result = await session.execute(stmt)
        return (result.rowcount or 0) > 0

    async def update_user_password(
        self, session: AsyncSession, uid: str, new_password_hash: str
    ) -> None:
        stmt = (
            update(UserAuth)
            .where(UserAuth.uid == uid)
            .values(
                password_hash=new_password_hash, updated_at=datetime.datetime.utcnow()
            )
        )
        await session.execute(stmt)

    async def get_user_refresh_tokens_count(
        self, session: AsyncSession, uid: str
    ) -> int:
        stmt = select(RefreshTokenModel).where(RefreshTokenModel.uid == uid)
        result = await session.execute(stmt)
        return len(result.scalars().all())
