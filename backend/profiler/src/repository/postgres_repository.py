import datetime
from typing import Optional

from sqlalchemy import select, delete, update, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.models import (
    Profile,
    ProfileRole,
    Role,
    ProfileAvatar,
    UserEmail,
    EmailConfirmationToken,
)
from src.repository.repository import (
    ProfileRepository,
    ProfileData,
    ProfileLookupData,
    RoleData,
    EmailConfirmationTokenData,
)


class PostgresProfileRepository(ProfileRepository):
    async def create_profile(
        self, session: AsyncSession, user_id: str, name: str, email: str
    ) -> None:
        profile = Profile(user_id=user_id, name=name)
        session.add(profile)
        await session.flush()

        user_email = UserEmail(user_id=user_id, email=email)
        session.add(user_email)
        await session.flush()

    async def get_profile(
        self, session: AsyncSession, user_id: str
    ) -> Optional[ProfileData]:
        stmt = select(Profile).where(Profile.user_id == user_id)
        result = await session.execute(stmt)
        profile = result.scalar_one_or_none()
        if profile is None:
            return None

        email_stmt = select(UserEmail).where(UserEmail.user_id == user_id)
        email_result = await session.execute(email_stmt)
        user_email = email_result.scalar_one_or_none()

        avatar_stmt = (
            select(ProfileAvatar)
            .where(ProfileAvatar.user_id == user_id)
            .order_by(ProfileAvatar.uploaded_at.desc())
            .limit(1)
        )
        avatar_result = await session.execute(avatar_stmt)
        avatar = avatar_result.scalar_one_or_none()

        roles_stmt = select(ProfileRole).where(ProfileRole.user_id == user_id)
        roles_result = await session.execute(roles_stmt)
        roles = [
            RoleData(role=r.role.value, assigned_at=r.assigned_at)
            for r in roles_result.scalars().all()
        ]

        return ProfileData(
            user_id=profile.user_id,
            name=profile.name,
            email=user_email.email if user_email else "",
            city=profile.city,
            avatar_url=avatar.s3_key if avatar else None,
            email_confirmed=user_email.confirmed_at is not None if user_email else False,
            roles=roles,
            created_at=profile.created_at,
        )

    async def update_profile(
        self,
        session: AsyncSession,
        user_id: str,
        name: Optional[str] = None,
        city: Optional[str] = None,
    ) -> None:
        values = {}
        if name is not None:
            values["name"] = name
        if city is not None:
            values["city"] = city
        if not values:
            return

        stmt = update(Profile).where(Profile.user_id == user_id).values(**values)
        await session.execute(stmt)
        await session.flush()

    async def delete_profile(self, session: AsyncSession, user_id: str) -> bool:
        stmt = delete(Profile).where(Profile.user_id == user_id)
        result = await session.execute(stmt)
        await session.flush()
        return result.rowcount > 0

    async def find_profiles_by_email(
        self, session: AsyncSession, email: str
    ) -> list[ProfileLookupData]:
        stmt = (
            select(Profile.user_id, Profile.name, ProfileAvatar.s3_key)
            .join(UserEmail, Profile.user_id == UserEmail.user_id)
            .outerjoin(
                ProfileAvatar,
                and_(
                    Profile.user_id == ProfileAvatar.user_id,
                    ProfileAvatar.id == (
                        select(ProfileAvatar.id)
                        .where(ProfileAvatar.user_id == Profile.user_id)
                        .order_by(ProfileAvatar.uploaded_at.desc())
                        .limit(1)
                        .correlate(Profile)
                        .scalar_subquery()
                    ),
                ),
            )
            .where(UserEmail.email == email)
        )
        result = await session.execute(stmt)
        rows = result.all()

        return [
            ProfileLookupData(
                user_id=row[0],
                name=row[1],
                avatar_url=row[2],
            )
            for row in rows
        ]

    async def get_roles(self, session: AsyncSession, user_id: str) -> list[RoleData]:
        stmt = select(ProfileRole).where(ProfileRole.user_id == user_id)
        result = await session.execute(stmt)
        return [
            RoleData(role=r.role.value, assigned_at=r.assigned_at)
            for r in result.scalars().all()
        ]

    async def assign_role(self, session: AsyncSession, user_id: str, role: str) -> None:
        profile = await self.get_profile(session, user_id)
        if profile is None:
            raise ValueError("Profile not found")

        existing_stmt = select(ProfileRole).where(
            and_(ProfileRole.user_id == user_id, ProfileRole.role == Role(role))
        )
        existing = (await session.execute(existing_stmt)).scalar_one_or_none()
        if existing is not None:
            return

        role_row = ProfileRole(user_id=user_id, role=Role(role))
        session.add(role_row)
        await session.flush()

    async def remove_role(self, session: AsyncSession, user_id: str, role: str) -> bool:
        stmt = delete(ProfileRole).where(
            and_(ProfileRole.user_id == user_id, ProfileRole.role == Role(role))
        )
        result = await session.execute(stmt)
        await session.flush()
        return (result.rowcount or 0) > 0

    async def create_email_confirmation_token(
        self, session: AsyncSession, token_data: EmailConfirmationTokenData
    ) -> None:
        token = EmailConfirmationToken(
            user_id=token_data.user_id,
            token=token_data.token,
            expires_at=token_data.expires_at,
        )
        session.add(token)
        await session.flush()

    async def get_email_confirmation_token(
        self, session: AsyncSession, token: str
    ) -> Optional[EmailConfirmationTokenData]:
        stmt = select(EmailConfirmationToken).where(
            EmailConfirmationToken.token == token
        )
        result = await session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            return None

        return EmailConfirmationTokenData(
            token=row.token,
            user_id=row.user_id,
            expires_at=row.expires_at,
        )

    async def confirm_email(self, session: AsyncSession, user_id: str) -> None:
        stmt = (
            update(UserEmail)
            .where(UserEmail.user_id == user_id)
            .values(confirmed_at=datetime.datetime.utcnow())
        )
        await session.execute(stmt)
        await session.flush()

    async def is_email_confirmed(
        self, session: AsyncSession, email: str
    ) -> bool:
        stmt = select(UserEmail).where(
            and_(
                UserEmail.email == email,
                UserEmail.confirmed_at.is_not(None),
            )
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def list_profiles(
        self, session: AsyncSession, limit: int = 20, offset: int = 0
    ) -> list[ProfileData]:
        stmt = select(Profile).order_by(Profile.created_at.desc()).limit(limit).offset(offset)
        result = await session.execute(stmt)
        profiles = result.scalars().all()

        profile_data_list = []
        for profile in profiles:
            data = await self.get_profile(session, profile.user_id)
            if data:
                profile_data_list.append(data)

        return profile_data_list
