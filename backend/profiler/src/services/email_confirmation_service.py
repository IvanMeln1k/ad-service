import datetime
import secrets

from sqlalchemy.ext.asyncio import AsyncSession

from src.config import config
from src.repository.repository import ProfileRepository, EmailConfirmationTokenData
from src.services.services import (
    EmailConfirmationService,
    ProfileNotFoundError,
    EmailAlreadyConfirmedError,
    InvalidConfirmationTokenError,
    ExpiredConfirmationTokenError,
)


class EmailConfirmationServiceImpl(EmailConfirmationService):
    def __init__(self, repository: ProfileRepository):
        self.repository = repository

    async def create_email_confirmation_token(
        self, session: AsyncSession, user_id: str
    ) -> str:
        existing = await self.repository.get_profile(session, user_id)
        if existing is None:
            raise ProfileNotFoundError(f"Profile {user_id} not found")

        token = secrets.token_urlsafe(32)
        expires_at = datetime.datetime.utcnow() + datetime.timedelta(
            seconds=config.EMAIL_CONFIRMATION_TTL
        )

        token_data = EmailConfirmationTokenData(
            token=token,
            user_id=user_id,
            expires_at=expires_at,
        )
        await self.repository.create_email_confirmation_token(session, token_data)
        await session.commit()

        return token

    async def confirm_email(self, session: AsyncSession, token: str) -> None:
        token_data = await self.repository.get_email_confirmation_token(session, token)
        if token_data is None:
            raise InvalidConfirmationTokenError("Token not found")

        if token_data.expires_at < datetime.datetime.utcnow():
            raise ExpiredConfirmationTokenError("Token expired")

        profile = await self.repository.get_profile(session, token_data.user_id)
        if profile is None:
            raise InvalidConfirmationTokenError("Profile not found for token")

        already_confirmed = await self.repository.is_email_confirmed(
            session, profile.email
        )
        if already_confirmed:
            raise EmailAlreadyConfirmedError(
                f"Email {profile.email} already confirmed by another user"
            )

        await self.repository.confirm_email(session, token_data.user_id)
        await session.commit()
