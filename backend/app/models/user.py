"""
User SQLModel class representing an authenticated user account.

This module defines the User model which represents a user account
with email-based authentication and password hashing.
"""

from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
import uuid
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .team import Team
    from .team_member import TeamMember
    from .task_share import TaskShare
    from .conversation import Conversation
    from .message import Message


class User(SQLModel, table=True):
    """
    User model representing an authenticated user account.

    This model uses SQLModel which combines SQLAlchemy (ORM) and Pydantic (validation).
    The table=True parameter indicates this is a database table model.

    Attributes:
        id: Unique identifier for the user (UUID, auto-generated)
        email: User's email address (unique, used for login)
        password_hash: Bcrypt-hashed password (never store plaintext)
        created_at: Timestamp when user account was created (UTC, auto-generated)
        updated_at: Timestamp when user account was last updated (UTC, auto-updated)

    Database Table:
        Name: users
        Indexes:
            - Primary key on id
            - Unique index on email (case-insensitive)

    Security:
        - Passwords are hashed using bcrypt with cost factor 12
        - Email addresses are unique and indexed for fast lookup
        - Password hash field requires minimum 60 characters (bcrypt output length)

    Example:
        ```python
        # Create a new user
        user = User(
            email="user@example.com",
            password_hash=hash_password("SecurePass123")
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        ```
    """

    __tablename__ = "users"

    # Primary key - auto-generated UUID
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        max_length=36,
        description="Unique identifier for the user (UUID)"
    )

    # Required fields
    email: str = Field(
        max_length=255,
        unique=True,
        index=True,
        description="User's email address (unique, case-insensitive)"
    )

    password_hash: str = Field(
        min_length=60,
        description="Bcrypt-hashed password (never store plaintext)"
    )

    # Timestamps (auto-managed)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when user was created (UTC)"
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
        description="Timestamp when user was last updated (UTC)"
    )

    # Relationships (NEW - Spec 003)
    owned_teams: List["Team"] = Relationship(
        back_populates="owner",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    team_memberships: List["TeamMember"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    received_shares: List["TaskShare"] = Relationship(
        back_populates="shared_with_user",
        sa_relationship_kwargs={
            "foreign_keys": "TaskShare.shared_with_user_id",
            "cascade": "all, delete-orphan"
        }
    )

    given_shares: List["TaskShare"] = Relationship(
        back_populates="shared_by_user",
        sa_relationship_kwargs={
            "foreign_keys": "TaskShare.shared_by_user_id",
            "cascade": "all, delete-orphan"
        }
    )

    # Relationships (NEW - Spec 005: AI Chat Backend)
    conversations: List["Conversation"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    messages: List["Message"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    class Config:
        """Pydantic configuration for the User model."""
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqJfitzXCO",
                "created_at": "2026-02-04T10:30:00Z",
                "updated_at": "2026-02-04T10:30:00Z"
            }
        }

    def __repr__(self) -> str:
        """String representation of the User."""
        return f"User(id='{self.id}', email='{self.email}')"
