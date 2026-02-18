"""
Configuration and environment variables for Todo Backend.

This module loads configuration from environment variables and provides
settings for database connection, application behavior, and other parameters.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """
    Application settings loaded from environment variables.

    All settings have sensible defaults for development, but should be
    explicitly configured for production environments.
    """

    # Database Configuration
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost:5432/todo_db"
    )

    DATABASE_POOL_SIZE: int = int(os.getenv("DATABASE_POOL_SIZE", "5"))
    DATABASE_POOL_RECYCLE: int = int(os.getenv("DATABASE_POOL_RECYCLE", "3600"))
    DATABASE_ECHO: bool = os.getenv("DATABASE_ECHO", "false").lower() == "true"

    # Application Configuration
    APP_NAME: str = os.getenv("APP_NAME", "Todo Backend API")
    APP_VERSION: str = os.getenv("APP_VERSION", "0.1.0")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

    # CORS Configuration (for frontend integration)
    CORS_ORIGINS: list[str] = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://localhost:3001"
    ).split(",")

    # Authentication Configuration (Spec 2)
    BETTER_AUTH_SECRET: str = os.getenv("BETTER_AUTH_SECRET", "")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRATION_SECONDS: int = int(os.getenv("JWT_EXPIRATION_SECONDS", "86400"))

    # OpenAI Configuration (Spec 005 - AI Chat Backend)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")  # Default to accessible model
    OPENAI_MAX_TOKENS: int = int(os.getenv("OPENAI_MAX_TOKENS", "4096"))

    # Mock Mode (for testing without API calls)
    MOCK_OPENAI: bool = os.getenv("MOCK_OPENAI", "false").lower() == "true"

    def __init__(self):
        """Validate required configuration on initialization."""
        if not self.BETTER_AUTH_SECRET:
            raise ValueError(
                "BETTER_AUTH_SECRET environment variable is required. "
                "Generate one using: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
            )

        # Check OpenAI configuration (skip if mock mode is enabled)
        if self.MOCK_OPENAI:
            import warnings
            warnings.warn(
                "MOCK_OPENAI is enabled. Using mock agent service (no real API calls). "
                "Set MOCK_OPENAI=false to use real OpenAI API.",
                UserWarning
            )
        elif not self.OPENAI_API_KEY or self.OPENAI_API_KEY == "your-openai-api-key-here":
            import warnings
            warnings.warn(
                "OPENAI_API_KEY is not configured. AI Chat features will not work. "
                "Get your API key from: https://platform.openai.com/api-keys "
                "Or set MOCK_OPENAI=true for testing without API calls.",
                UserWarning
            )

    def __repr__(self) -> str:
        """String representation (masks sensitive data)."""
        return (
            f"Settings(DATABASE_URL=***masked***, "
            f"POOL_SIZE={self.DATABASE_POOL_SIZE}, "
            f"APP_NAME={self.APP_NAME})"
        )


# Global settings instance
settings = Settings()
