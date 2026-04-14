"""
Application configuration settings.
Loads environment variables and provides configuration for the application.
"""
from pathlib import Path
from pydantic_settings import BaseSettings

# Resolve the project root (.env lives next to the app/ package)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_ENV_FILE = _PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database Configuration
    DATABASE_URL: str

    # JWT Configuration (local auth)
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24 * 7  # 7 days

    # Application Settings
    APP_NAME: str = "Smart Student Expense & Budget System"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # Groq AI Configuration
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    GROQ_MAX_TOKENS: int = 1024
    GROQ_TEMPERATURE: float = 0.7

    # MarketAux Market News Configuration
    MARKETAUX_API_TOKEN: str = ""

    class Config:
        env_file = str(_ENV_FILE)
        case_sensitive = True


# Global settings instance
settings = Settings()
