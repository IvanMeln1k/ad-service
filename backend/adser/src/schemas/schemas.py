import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class CreateAdRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=500)
    description: str = Field(..., min_length=10, max_length=5000)
    price: Optional[float] = Field(default=None, ge=0)
    city: Optional[str] = Field(default=None, min_length=2, max_length=255)
    category: Optional[str] = None

    @field_validator("category", mode="before")
    @classmethod
    def normalize_category(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        normalized = value.strip().upper()
        if normalized not in ALLOWED_CATEGORIES:
            raise ValueError("Unsupported category")
        return normalized


class UpdateAdRequest(BaseModel):
    title: Optional[str] = Field(default=None, min_length=3, max_length=500)
    description: Optional[str] = Field(default=None, min_length=10, max_length=5000)
    price: Optional[float] = Field(default=None, ge=0)
    city: Optional[str] = Field(default=None, min_length=2, max_length=255)
    category: Optional[str] = None

    @field_validator("category", mode="before")
    @classmethod
    def normalize_category(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        normalized = value.strip().upper()
        if normalized not in ALLOWED_CATEGORIES:
            raise ValueError("Unsupported category")
        return normalized


class PhotoResponse(BaseModel):
    id: str
    s3_key: str
    position: int


class AuthorResponse(BaseModel):
    user_id: str
    name: str
    email: Optional[str] = None
    city: Optional[str] = None
    avatar_url: Optional[str] = None


class AdResponse(BaseModel):
    id: str
    user_id: str
    title: str
    description: str
    status: str
    price: Optional[float] = None
    city: Optional[str] = None
    category: Optional[str] = None
    is_banned: bool = False
    ban_reason: Optional[str] = None
    photos: list[PhotoResponse] = []
    author: Optional[AuthorResponse] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None


class ConfirmPhotoRequest(BaseModel):
    s3_key: str
    position: int = 0


class PresignPhotoRequest(BaseModel):
    file_name: str = Field(..., min_length=1, max_length=255)
    content_type: str = Field(..., min_length=3, max_length=255)
    file_size: int = Field(..., ge=1)


class PresignResponse(BaseModel):
    upload_url: str
    s3_key: str
    max_file_size: int


class AdsListResponse(BaseModel):
    items: list[AdResponse]
    total: int
    limit: int
    offset: int


class CityContextResponse(BaseModel):
    city: str
    country: Optional[str] = None
    temperature_c: Optional[float] = None
    weather_description: Optional[str] = None
    source: str
    available: bool
    unavailable_reason: Optional[str] = None


class BanRequest(BaseModel):
    reason: str


class UnbanRequest(BaseModel):
    unban_reason: str


class BanResponse(BaseModel):
    id: str
    ad_id: str
    moderator_id: str
    reason: str
    banned_at: Optional[datetime.datetime] = None
    unbanned_by_id: Optional[str] = None
    unban_reason: Optional[str] = None
    unbanned_at: Optional[datetime.datetime] = None


ALLOWED_CATEGORIES = {"AUTO", "REALTY", "ELECTRONICS", "CLOTHING", "SERVICES", "OTHER"}
