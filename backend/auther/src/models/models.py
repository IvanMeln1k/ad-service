from sqlalchemy import Column, String, DateTime, Boolean, Index, Text
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()


class UserAuth(Base):
    __tablename__ = "user_auth"

    # Using string as primary key for flexibility (UUID or any string)
    uid = Column(String(255), primary_key=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False,
    )

    # Index for faster lookups
    __table_args__ = (Index("idx_user_auth_uid", uid),)


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    # Using token_hash as primary key since it's unique
    token_hash = Column(String(255), primary_key=True)
    uid = Column(String(255), nullable=False)
    expires_at = Column(DateTime, nullable=True)  # NULL means never expires
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    # Composite index for common query patterns
    __table_args__ = (
        Index("idx_refresh_tokens_uid", uid),
        Index("idx_refresh_tokens_uid_token", uid, token_hash),
        Index("idx_refresh_tokens_expires", expires_at),
    )
