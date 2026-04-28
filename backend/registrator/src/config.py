import os


class Config:
    AUTHER_URL: str = os.getenv("AUTHER_URL", "http://localhost:8003")
    PROFILER_URL: str = os.getenv("PROFILER_URL", "http://localhost:8001")


config = Config()
