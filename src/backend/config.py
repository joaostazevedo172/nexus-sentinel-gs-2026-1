"""Application configuration loaded from environment variables."""
import os
from functools import lru_cache


class Settings:
    allowed_origins: list[str]
    yolo_rotation_seconds: float
    blockchain_max_history: int

    def __init__(self) -> None:
        raw = os.getenv(
            "ALLOWED_ORIGINS",
            # Default for local dev
            "http://localhost:3000,http://localhost:3001,"
            # And any *.vercel.app preview deployment (validated via regex
            # downstream — for production, set ALLOWED_ORIGINS explicitly).
            "https://nexus-sentinel.vercel.app"
        )
        self.allowed_origins = [o.strip() for o in raw.split(",") if o.strip()]
        self.yolo_rotation_seconds = float(os.getenv("YOLO_ROTATION_S", "3.2"))
        self.blockchain_max_history = int(os.getenv("BLOCKCHAIN_MAX_HISTORY", "500"))


@lru_cache
def get_settings() -> Settings:
    return Settings()
