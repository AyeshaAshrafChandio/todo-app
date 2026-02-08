"""
User service for database operations on User model.

This module provides service functions for creating and retrieving users
from the database. It handles user-related business logic and database
interactions.
"""

from typing import Optional
from sqlmodel import Session, select

from app.models.user import User
from app.services.auth_service import hash_password


def create_user(db: Session, email: str, password: str) -> User:
    """
    Create a new user account with hashed password.

    This function creates a new user in the database with the provided
    email and password. The password is automatically hashed using bcrypt
    before storage.

    Args:
        db: Database session
        email: User's email address (must be unique)
        password: User's plain text password (will be hashed)

    Returns:
        Created User object with generated ID and timestamps

    Raises:
        IntegrityError: If email already exists (unique constraint violation)
        ValueError: If email or password is invalid

    Security:
        - Password is hashed with bcrypt (cost factor 12)
        - Email uniqueness enforced by database constraint
        - Password never stored in plain text

    Example:
        ```python
        user = create_user(
            db=db,
            email="user@example.com",
            password="SecurePass123"
        )
        # Returns: User(id='550e8400-...', email='user@example.com', ...)
        ```

    Database Operations:
        1. Hash password using bcrypt
        2. Create User object with email and password_hash
        3. Add to database session
        4. Commit transaction
        5. Refresh to get generated ID and timestamps
    """
    # Hash password before storing
    password_hash = hash_password(password)

    # Create user object
    user = User(
        email=email.lower(),  # Store email in lowercase for case-insensitive comparison
        password_hash=password_hash
    )

    # Add to database
    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Retrieve a user by email address (case-insensitive).

    Args:
        db: Database session
        email: User's email address to search for

    Returns:
        User object if found, None otherwise

    Security:
        - Case-insensitive email comparison
        - Returns full User object including password_hash
        - Should only be used internally (never expose password_hash to API)

    Example:
        ```python
        user = get_user_by_email(db, "user@example.com")
        if user:
            # User exists
            print(f"Found user: {user.email}")
        else:
            # User not found
            print("User does not exist")
        ```

    Database Query:
        ```sql
        SELECT * FROM users WHERE LOWER(email) = LOWER('user@example.com') LIMIT 1
        ```
    """
    statement = select(User).where(User.email == email.lower())
    return db.exec(statement).first()


def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
    """
    Retrieve a user by their unique ID.

    Args:
        db: Database session
        user_id: User's unique identifier (UUID string)

    Returns:
        User object if found, None otherwise

    Security:
        - Returns full User object including password_hash
        - Should only be used internally (never expose password_hash to API)

    Example:
        ```python
        user = get_user_by_id(db, "550e8400-e29b-41d4-a716-446655440000")
        if user:
            # User exists
            print(f"Found user: {user.email}")
        else:
            # User not found
            print("User does not exist")
        ```

    Database Query:
        ```sql
        SELECT * FROM users WHERE id = '550e8400-e29b-41d4-a716-446655440000' LIMIT 1
        ```
    """
    statement = select(User).where(User.id == user_id)
    return db.exec(statement).first()
