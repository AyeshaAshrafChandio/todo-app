"""
User response schemas for API endpoints.

This module defines Pydantic schemas for user data returned by API endpoints.
These schemas exclude sensitive fields like password_hash for security.
"""

from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserResponse(BaseModel):
    """
    User response schema for API responses.

    This schema represents user data returned to clients. It excludes
    sensitive fields like password_hash for security reasons.

    Attributes:
        id: Unique identifier for the user (UUID string)
        email: User's email address
        created_at: Timestamp when user account was created (UTC)

    Security:
        - password_hash is NEVER included in responses
        - updated_at is excluded (internal field)

    Example:
        ```json
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "email": "user@example.com",
            "created_at": "2026-02-04T10:30:00Z"
        }
        ```
    """

    id: str = Field(
        description="Unique identifier for the user (UUID)",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )

    email: EmailStr = Field(
        description="User's email address",
        examples=["user@example.com"]
    )

    created_at: datetime = Field(
        description="Timestamp when user was created (UTC)",
        examples=["2026-02-04T10:30:00Z"]
    )

    class Config:
        """Pydantic configuration."""
        from_attributes = True  # Enable ORM mode for SQLModel compatibility
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "created_at": "2026-02-04T10:30:00.000Z"
            }
        }
