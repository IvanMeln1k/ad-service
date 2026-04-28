import os


class Config:
    KAFKA_BOOTSTRAP_SERVERS: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    KAFKA_TOPIC_REGISTRATIONS: str = os.getenv("KAFKA_TOPIC_REGISTRATIONS", "registrations")
    KAFKA_GROUP_ID: str = os.getenv("KAFKA_GROUP_ID", "profiler-unloader")

    PROFILER_URL: str = os.getenv("PROFILER_URL", "http://localhost:8001")
    NOTIFICATOR_URL: str = os.getenv("NOTIFICATOR_URL", "http://localhost:8002")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")


config = Config()
