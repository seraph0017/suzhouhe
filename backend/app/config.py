"""
Application Configuration
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Application
    APP_NAME: str = "AI Manga Pipeline"
    APP_ENV: str = "development"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql://suzhou:suzhou_dev_password@localhost:5432/suzhou"

    # Security
    SECRET_KEY: str = "change-this-secret-key-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"

    # Object Storage (MinIO/S3)
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "suzhou_admin"
    MINIO_SECRET_KEY: str = "suzhou_dev_secret"
    MINIO_BUCKET: str = "assets"
    MINIO_SECURE: bool = False

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # File Upload
    MAX_UPLOAD_SIZE_MB: int = 100
    UPLOAD_DIR: str = "./uploads"

    # Default AI Providers
    DEFAULT_LLM_PROVIDER: str = "anthropic"
    DEFAULT_IMAGE_PROVIDER: str = "openai"
    DEFAULT_VIDEO_PROVIDER: str = "runway"
    DEFAULT_TTS_PROVIDER: str = "openai"
    DEFAULT_BGM_PROVIDER: str = "muse-net"

    # AI Provider API Keys
    OPENAI_API_KEY: str = ""
    OPENAI_API_BASE: str = "https://api.openai.com/v1"
    ANTHROPIC_API_KEY: str = ""
    RUNWAY_API_KEY: str = ""

    # Logging
    LOG_LEVEL: str = "INFO"

    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
