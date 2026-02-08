"""
Authentication service for password hashing and JWT token generation.

This module provides core authentication functionality including:
- Password hashing using bcrypt with cost factor 12
- Password verification with timing-safe comparison
- JWT token generation with user claims
"""

from datetime import datetime, timedelta
from typing import Dict
import bcrypt
import jwt

from app.config import settings


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt with cost factor 12.

    Bcrypt automatically generates a unique salt for each password and
    includes it in the hash output. The cost factor of 12 provides a
    good balance between security and performance.

    Args:
        password: Plain text password to hash

    Returns:
        Bcrypt hash string (60 characters, includes salt)
        Format: $2b$12$<salt><hash>

    Security:
        - Cost factor 12 (2^12 = 4096 iterations)
        - Automatic salt generation (unique per password)
        - Timing-safe comparison when verifying
        - Resistant to rainbow table attacks

    Example:
        ```python
        password_hash = hash_password("SecurePass123")
        # Returns: "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqJfitzXCO"
        ```

    Performance:
        - Hashing time: ~100-200ms (intentionally slow for security)
        - Cost factor 12 is recommended for 2026 hardware
    """
    # Generate salt with cost factor 12
    salt = bcrypt.gensalt(rounds=12)

    # Hash password with salt
    password_bytes = password.encode('utf-8')
    hashed = bcrypt.hashpw(password_bytes, salt)

    # Return hash as string
    return hashed.decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verify a password against a bcrypt hash using timing-safe comparison.

    This function uses bcrypt's built-in verification which includes
    timing-safe comparison to prevent timing attacks.

    Args:
        password: Plain text password to verify
        password_hash: Bcrypt hash to compare against

    Returns:
        True if password matches hash, False otherwise

    Security:
        - Timing-safe comparison (constant time)
        - Prevents timing attacks
        - No information leakage about password correctness

    Example:
        ```python
        is_valid = verify_password("SecurePass123", stored_hash)
        if is_valid:
            # Password is correct
            pass
        ```

    Performance:
        - Verification time: ~100-200ms (same as hashing)
        - Intentionally slow to prevent brute force attacks
    """
    try:
        password_bytes = password.encode('utf-8')
        hash_bytes = password_hash.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hash_bytes)
    except Exception:
        # If any error occurs during verification, return False
        # This prevents information leakage through error messages
        return False


def create_jwt_token(user_id: str, email: str) -> Dict[str, any]:
    """
    Create a JWT access token with user claims.

    Generates a signed JWT token containing user identification claims
    and expiration information. The token is signed using HS256 algorithm
    with the BETTER_AUTH_SECRET from environment variables.

    Token Claims:
        - userId: User's unique identifier (UUID string)
        - email: User's email address
        - iat: Issued at timestamp (Unix timestamp)
        - exp: Expiration timestamp (Unix timestamp, iat + 24 hours)

    Args:
        user_id: User's unique identifier (UUID string)
        email: User's email address

    Returns:
        Dictionary containing:
        {
            "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "expires_at": datetime(2026, 2, 5, 10, 30, 0)
        }

    Security:
        - Signed with HS256 (HMAC with SHA-256)
        - Secret key from environment variable (BETTER_AUTH_SECRET)
        - 24-hour expiration (configurable via JWT_EXPIRATION_SECONDS)
        - Stateless verification (no server-side storage required)

    Example:
        ```python
        token_data = create_jwt_token(
            user_id="550e8400-e29b-41d4-a716-446655440000",
            email="user@example.com"
        )
        # Returns:
        # {
        #     "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        #     "expires_at": datetime(2026, 2, 5, 10, 30, 0)
        # }
        ```

    Token Structure:
        ```json
        {
            "userId": "550e8400-e29b-41d4-a716-446655440000",
            "email": "user@example.com",
            "iat": 1706976000,
            "exp": 1707062400
        }
        ```

    Usage:
        Client includes token in Authorization header:
        ```
        Authorization: Bearer <token>
        ```
    """
    # Calculate expiration time (current time + JWT_EXPIRATION_SECONDS)
    now = datetime.utcnow()
    expires_at = now + timedelta(seconds=settings.JWT_EXPIRATION_SECONDS)

    # Create token payload with required claims
    payload = {
        "userId": user_id,  # Note: Better Auth uses "userId" not "user_id"
        "email": email,
        "iat": int(now.timestamp()),  # Issued at (Unix timestamp)
        "exp": int(expires_at.timestamp())  # Expiration (Unix timestamp)
    }

    # Sign token with secret key
    token = jwt.encode(
        payload,
        settings.BETTER_AUTH_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )

    return {
        "token": token,
        "expires_at": expires_at
    }
