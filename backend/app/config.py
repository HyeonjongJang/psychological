"""Application configuration."""
import os
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional, List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "Psychological Assessment Chatbot"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./psychological.db"

    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4"

    # CORS - accepts comma-separated string from env or list
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def fix_database_url(cls, v: str) -> str:
        """Convert Render's postgres:// to postgresql+asyncpg://"""
        if v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql+asyncpg://", 1)
        if v.startswith("postgresql://") and "+asyncpg" not in v:
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS_ORIGINS from comma-separated string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    # Assessment settings
    # SE threshold based on Monte Carlo validation with Mini-IPIP6 items
    # 0.65 provides good accuracy (r=0.73) with ~5% item reduction
    # Lower values require all items; higher values trade accuracy for efficiency
    DOSE_SE_THRESHOLD: float = 0.65
    DOSE_MAX_ITEMS_PER_TRAIT: int = 4
    NATURAL_MIN_TURNS: int = 10

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
