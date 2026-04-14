import enum
import datetime
import uuid

from sqlalchemy import (
    Column,
    String,
    DateTime,
    Enum,
    ForeignKey,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Role(enum.Enum):
    MODERATOR = "MODERATOR"
    ADMIN = "ADMIN"


class Profile(Base):
    __tablename__ = "profiles"

    user_id = Column(String(255), primary_key=True)
    name = Column(String(255), nullable=False)
    city = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)


class ProfileRole(Base):
    __tablename__ = "profile_roles"

    user_id = Column(
        String(255),
        ForeignKey("profiles.user_id", ondelete="CASCADE"),
        primary_key=True,
    )
    role = Column(Enum(Role, name="role_enum"), primary_key=True)
    assigned_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)


class ProfileAvatar(Base):
    __tablename__ = "profile_avatars"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        String(255),
        ForeignKey("profiles.user_id", ondelete="CASCADE"),
        nullable=False,
    )
    s3_key = Column(String(1024), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    __table_args__ = (Index("idx_profile_avatars_user_id", user_id),)


class UserEmail(Base):
    __tablename__ = "user_emails"

    user_id = Column(
        String(255),
        ForeignKey("profiles.user_id", ondelete="CASCADE"),
        primary_key=True,
    )
    email = Column(String(255), nullable=False)
    confirmed_at = Column(DateTime, nullable=True)

    __table_args__ = (Index("idx_user_emails_email", email),)


class EmailConfirmationToken(Base):
    __tablename__ = "email_confirmation_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255), nullable=False)
    token = Column(String(255), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)

    __table_args__ = (
        Index("idx_email_confirmation_tokens_token", token),
        Index("idx_email_confirmation_tokens_user_id", user_id),
    )
