import os
import secrets
from typing import List, Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings and configuration."""

    # Application settings
    APP_NAME: str = "Clock Bucks - Meeting Cost Calculator"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # Server settings
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    WORKERS: int = 1

    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS settings
    ALLOWED_ORIGINS: List[str] = ["*"]

    # Database settings
    DATABASE_URL: str = "sqlite:///./clockbucks.db"
    DATABASE_ECHO: bool = False

    # Redis settings
    REDIS_URL: Optional[str] = None

    # API settings
    API_PREFIX: str = "/api"
    API_V1_STR: str = "/api/v1"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Rate limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60

    # Monitoring
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def validate_database_url(cls, v):
        if not v:
            return "sqlite:///./clockbucks.db"
        return v

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
    }


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
