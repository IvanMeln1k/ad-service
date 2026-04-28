import os


class Config:
    ALLOWED_IMAGE_TYPES: tuple[str, ...] = tuple(
        os.getenv("ALLOWED_IMAGE_TYPES", "image/jpeg,image/png,image/webp").split(",")
    )
    MAX_IMAGE_SIZE_BYTES: int = int(os.getenv("MAX_IMAGE_SIZE_BYTES", str(10 * 1024 * 1024)))

    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASS: str = os.getenv("DB_PASS", "postgres")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_NAME: str = os.getenv("DB_NAME", "adser_service")

    KAFKA_BOOTSTRAP_SERVERS: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    KAFKA_TOPIC_ADS: str = os.getenv("KAFKA_TOPIC_ADS", "ads")

    S3_ENDPOINT: str = os.getenv("S3_ENDPOINT", "http://localhost:9000")
    S3_PUBLIC_ENDPOINT: str = os.getenv("S3_PUBLIC_ENDPOINT", "http://localhost:9000")
    S3_ACCESS_KEY: str = os.getenv("S3_ACCESS_KEY", "minioadmin")
    S3_SECRET_KEY: str = os.getenv("S3_SECRET_KEY", "minioadmin")
    S3_BUCKET: str = os.getenv("S3_BUCKET", "ad-photos")

    AUTHER_URL: str = os.getenv("AUTHER_URL", "http://localhost:8003")
    PROFILER_URL: str = os.getenv("PROFILER_URL", "http://localhost:8001")
    PUBLIC_SITE_URL: str = os.getenv("PUBLIC_SITE_URL", "http://localhost:3000")

    OPENWEATHER_API_BASE_URL: str = os.getenv("OPENWEATHER_API_BASE_URL", "https://api.openweathermap.org")
    OPENWEATHER_API_KEY: str = os.getenv("OPENWEATHER_API_KEY", "")
    EXTERNAL_API_TIMEOUT_S: float = float(os.getenv("EXTERNAL_API_TIMEOUT_S", "2.5"))
    EXTERNAL_API_RETRIES: int = int(os.getenv("EXTERNAL_API_RETRIES", "2"))
    EXTERNAL_API_RATE_LIMIT: int = int(os.getenv("EXTERNAL_API_RATE_LIMIT", "30"))
    EXTERNAL_API_RATE_WINDOW_S: int = int(os.getenv("EXTERNAL_API_RATE_WINDOW_S", "60"))

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


config = Config()
