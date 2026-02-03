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

    def __repr__(self) -> str:
        """String representation (masks sensitive data)."""
        return (
            f"Settings(DATABASE_URL=***masked***, "
            f"POOL_SIZE={self.DATABASE_POOL_SIZE}, "
            f"APP_NAME={self.APP_NAME})"
        )


# Global settings instance
settings = Settings()
