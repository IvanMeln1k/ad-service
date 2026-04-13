import os
from typing import Optional


class Config:
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASS: str = os.getenv("DB_PASS", "password")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_NAME: str = os.getenv("DB_NAME", "auth_service")

    JWT_SECRET: str = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
    ACCESS_TOKEN_TTL: int = int(os.getenv("ACCESS_TOKEN_TTL", "3600"))
    REFRESH_TOKEN_TTL: int = int(os.getenv("REFRESH_TOKEN_TTL", "2592000"))

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


config = Config()
