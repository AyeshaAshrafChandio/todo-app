"""
Authentication middleware for JWT token verification.

This module provides FastAPI dependency functions for extracting and verifying
JWT tokens from Authorization headers. It ensures that protected endpoints
are only accessible to authenticated users with valid tokens.
"""

from typing import Dict
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

from app.config import settings


# HTTPBearer security scheme for extracting Bearer tokens from Authorization header
security = HTTPBearer(
    scheme_name="Bearer Token",
    description="JWT token obtained from /auth/signup or /auth/signin endpoints"
)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, str]:
    """
    FastAPI dependency that verifies JWT token and returns authenticated user info.

    This function extracts the JWT token from the Authorization header,
    verifies its signature and expiration, and returns the user information
    contained in the token claims.

    Token Format:
        Authorization: Bearer <jwt_token>

    Token Claims (expected):
        - userId: User's unique identifier (UUID string)
        - email: User's email address
        - iat: Issued at timestamp (Unix timestamp)
        - exp: Expiration timestamp (Unix timestamp)

    Args:
        credentials: HTTP Bearer credentials extracted from Authorization header

    Returns:
        Dictionary containing authenticated user information:
        {
            "user_id": "550e8400-e29b-41d4-a716-446655440000",
            "email": "user@example.com"
        }

    Raises:
        HTTPException: 401 Unauthorized if:
            - Token signature is invalid
            - Token has expired
            - Token is malformed
            - Required claims are missing

    Security:
        - Verifies token signature using BETTER_AUTH_SECRET
        - Validates token expiration (exp claim)
        - Uses HS256 algorithm (HMAC with SHA-256)
        - Stateless verification (no database lookup required)

    Example Usage:
        ```python
        @router.get("/api/{user_id}/tasks")
        def list_tasks(
            user_id: str,
            current_user: dict = Depends(get_current_user)
        ):
            # Verify user_id matches authenticated user
            if current_user["user_id"] != user_id:
                raise HTTPException(status_code=403, detail="Access denied")
            # ... rest of endpoint logic
        ```
    """
    token = credentials.credentials

    try:
        # Decode and verify JWT token
        payload = jwt.decode(
            token,
            settings.BETTER_AUTH_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            options={
                "verify_signature": True,
                "verify_exp": True,
                "require": ["userId", "email", "iat", "exp"]
            }
        )

        # Extract user information from token claims
        user_id = payload.get("userId")
        email = payload.get("email")

        # Validate required claims are present
        if not user_id or not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing required claims",
                headers={"WWW-Authenticate": "Bearer"}
            )

        return {
            "user_id": user_id,
            "email": email
        }

    except ExpiredSignatureError:
        # Token has expired
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    except InvalidTokenError as e:
        # Token is invalid (malformed, wrong signature, etc.)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"}
        )

    except Exception as e:
        # Catch-all for unexpected errors
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"}
        )


def verify_user_access(user_id: str, current_user: Dict[str, str]) -> None:
    """
    Verify that the authenticated user has access to the requested user's resources.

    This helper function checks that the user_id in the URL path matches
    the authenticated user's ID from the JWT token. This prevents users
    from accessing other users' data.

    Args:
        user_id: User ID from URL path parameter
        current_user: Authenticated user info from get_current_user dependency

    Raises:
        HTTPException: 403 Forbidden if user_id doesn't match authenticated user

    Example Usage:
        ```python
        @router.get("/api/{user_id}/tasks")
        def list_tasks(
            user_id: str,
            current_user: dict = Depends(get_current_user)
        ):
            verify_user_access(user_id, current_user)
            # ... rest of endpoint logic
        ```
    """
    if current_user["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You can only access your own resources"
        )
