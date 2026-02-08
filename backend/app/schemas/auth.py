"""
Authentication request and response schemas.

This module defines Pydantic schemas for authentication endpoints
including signup, signin, and authentication responses with JWT tokens.
"""

from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator
import re

from app.schemas.user import UserResponse


class SignupRequest(BaseModel):
    """
    Request schema for user signup/registration.

    Validates email format and password strength requirements.

    Attributes:
        email: User's email address (must be valid email format)
        password: User's password (min 8 chars, must contain uppercase, lowercase, digit)

    Validation Rules:
        - Email must be valid RFC 5322 format
        - Password minimum 8 characters
        - Password must contain at least one uppercase letter
        - Password must contain at least one lowercase letter
        - Password must contain at least one digit

    Example:
        ```json
        {
            "email": "user@example.com",
            "password": "SecurePass123"
        }
        ```
    """

    email: EmailStr = Field(
        description="User's email address (valid email format required)",
        examples=["user@example.com"]
    )

    password: str = Field(
        min_length=8,
        description="User's password (min 8 chars, must contain uppercase, lowercase, digit)",
        examples=["SecurePass123"]
    )

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        """
        Validate password meets strength requirements.

        Requirements:
            - At least one uppercase letter
            - At least one lowercase letter
            - At least one digit

        Args:
            value: Password to validate

        Returns:
            The validated password

        Raises:
            ValueError: If password doesn't meet requirements
        """
        if not re.search(r'[A-Z]', value):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r'[a-z]', value):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r'\d', value):
            raise ValueError("Password must contain at least one digit")
        return value

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123"
            }
        }


class SigninRequest(BaseModel):
    """
    Request schema for user signin/login.

    Attributes:
        email: User's email address
        password: User's password

    Example:
        ```json
        {
            "email": "user@example.com",
            "password": "SecurePass123"
        }
        ```
    """

    email: EmailStr = Field(
        description="User's email address",
        examples=["user@example.com"]
    )

    password: str = Field(
        description="User's password",
        examples=["SecurePass123"]
    )

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123"
            }
        }


class AuthResponse(BaseModel):
    """
    Response schema for successful authentication (signup/signin).

    Contains user information and JWT token for subsequent API requests.

    Attributes:
        user: User information (id, email, created_at)
        token: JWT access token (valid for 24 hours)
        expires_at: Token expiration timestamp (UTC)

    Token Usage:
        Include token in Authorization header for protected endpoints:
        ```
        Authorization: Bearer <token>
        ```

    Example:
        ```json
        {
            "user": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "created_at": "2026-02-04T10:30:00Z"
            },
            "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "expires_at": "2026-02-05T10:30:00Z"
        }
        ```
    """

    user: UserResponse = Field(
        description="User information (id, email, created_at)"
    )

    token: str = Field(
        description="JWT access token (valid for 24 hours)",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI1NTBlODQwMC1lMjliLTQxZDQtYTcxNi00NDY2NTU0NDAwMDAiLCJlbWFpbCI6InVzZXJAZXhhbXBsZS5jb20iLCJpYXQiOjE3MDY5NzYwMDAsImV4cCI6MTcwNzA2MjQwMH0.signature"]
    )

    expires_at: datetime = Field(
        description="Token expiration timestamp (UTC)",
        examples=["2026-02-05T10:30:00Z"]
    )

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "user": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "email": "user@example.com",
                    "created_at": "2026-02-04T10:30:00.000Z"
                },
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI1NTBlODQwMC1lMjliLTQxZDQtYTcxNi00NDY2NTU0NDAwMDAiLCJlbWFpbCI6InVzZXJAZXhhbXBsZS5jb20iLCJpYXQiOjE3MDY5NzYwMDAsImV4cCI6MTcwNzA2MjQwMH0.signature",
                "expires_at": "2026-02-05T10:30:00.000Z"
            }
        }
