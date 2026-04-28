import enum
import datetime
import uuid

from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Integer, Index, Text, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class AdStatus(enum.Enum):
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"


class AdCategory(enum.Enum):
    AUTO = "AUTO"
    REALTY = "REALTY"
    ELECTRONICS = "ELECTRONICS"
    CLOTHING = "CLOTHING"
    SERVICES = "SERVICES"
    OTHER = "OTHER"


class Ad(Base):
    __tablename__ = "ads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    price = Column(Numeric(12, 2), nullable=True)
    city = Column(String(255), nullable=True)
    category = Column(Enum(AdCategory, name="category_enum"), nullable=True)
    status = Column(Enum(AdStatus, name="ad_status_enum"), nullable=False, default=AdStatus.ACTIVE)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("idx_ads_user_id", user_id),
        Index("idx_ads_status", status),
        Index("idx_ads_category", category),
        Index("idx_ads_city", city),
        Index("idx_ads_price", price),
    )


class AdPhoto(Base):
    __tablename__ = "ad_photos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ad_id = Column(UUID(as_uuid=True), ForeignKey("ads.id", ondelete="CASCADE"), nullable=False)
    s3_key = Column(String(1024), nullable=False)
    position = Column(Integer, nullable=False, default=0)
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    __table_args__ = (Index("idx_ad_photos_ad_id", ad_id),)


class AdBan(Base):
    __tablename__ = "ad_bans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ad_id = Column(UUID(as_uuid=True), ForeignKey("ads.id", ondelete="CASCADE"), nullable=False)
    moderator_id = Column(String(255), nullable=False)
    reason = Column(Text, nullable=False)
    banned_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    unbanned_by_id = Column(String(255), nullable=True)
    unban_reason = Column(Text, nullable=True)
    unbanned_at = Column(DateTime, nullable=True)

    __table_args__ = (Index("idx_ad_bans_ad_id", ad_id),)
