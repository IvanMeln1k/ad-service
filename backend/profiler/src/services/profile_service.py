from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.config import config
from src.events.publisher import EventPublisher
from src.repository.repository import ProfileRepository, ProfileData, ProfileLookupData
from src.services.services import ProfileService, ProfileNotFoundError, EmailAlreadyConfirmedError


class ProfileServiceImpl(ProfileService):
    def __init__(self, repository: ProfileRepository, publisher: EventPublisher):
        self.repository = repository
        self.publisher = publisher

    async def create_profile(
        self, session: AsyncSession, user_id: str, name: str, email: str
    ) -> None:
        if await self.repository.is_email_confirmed(session, email):
            raise EmailAlreadyConfirmedError(f"Email {email} is already confirmed by another user")

        await self.repository.create_profile(session, user_id, name, email)
        await session.commit()

        await self.publisher.publish(
            topic=config.KAFKA_TOPIC_REGISTRATIONS,
            key=user_id,
            value={
                "event": "user.registered",
                "user_id": user_id,
                "email": email,
                "name": name,
            },
        )

    async def get_profile(
        self, session: AsyncSession, user_id: str
    ) -> ProfileData:
        profile = await self.repository.get_profile(session, user_id)
        if profile is None:
            raise ProfileNotFoundError(f"Profile {user_id} not found")
        return profile

    async def update_profile(
        self,
        session: AsyncSession,
        user_id: str,
        name: Optional[str] = None,
        city: Optional[str] = None,
    ) -> ProfileData:
        existing = await self.repository.get_profile(session, user_id)
        if existing is None:
            raise ProfileNotFoundError(f"Profile {user_id} not found")

        await self.repository.update_profile(session, user_id, name=name, city=city)
        await session.commit()

        return await self.repository.get_profile(session, user_id)

    async def delete_profile(self, session: AsyncSession, user_id: str) -> None:
        deleted = await self.repository.delete_profile(session, user_id)
        await session.commit()
        if not deleted:
            raise ProfileNotFoundError(f"Profile {user_id} not found")

    async def find_profiles_by_email(
        self, session: AsyncSession, email: str
    ) -> list[ProfileLookupData]:
        return await self.repository.find_profiles_by_email(session, email)

    async def list_profiles(
        self, session: AsyncSession, limit: int = 20, offset: int = 0
    ) -> list[ProfileData]:
        return await self.repository.list_profiles(session, limit, offset)
