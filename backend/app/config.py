"""Application configuration."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "Psychological Assessment Chatbot"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./psychological.db"

    # For PostgreSQL in production:
    # DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost/psychological"

    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4"

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

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
