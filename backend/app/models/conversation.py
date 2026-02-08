"""
Conversation SQLModel class representing a chat session between user and AI assistant.

This module defines the Conversation model which represents a persistent chat session
for the AI-powered chatbot backend (Spec 005).
"""

from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .user import User
    from .message import Message


class Conversation(SQLModel, table=True):
    """
    Conversation model representing a persistent chat session.

    This model stores conversation metadata and serves as a container for messages.
    All conversation context is persisted in the database to support stateless
    architecture (no in-memory session state).

    Attributes:
        id: Unique identifier for the conversation (auto-generated)
        user_id: Owner of the conversation (foreign key to users.id)
        created_at: Timestamp when conversation was created (UTC, auto-generated)
        updated_at: Timestamp when conversation was last updated (UTC, auto-updated)

    Relationships:
        user: The user who owns this conversation
        messages: All messages in this conversation (ordered by created_at)

    Database Table:
        Name: conversations
        Indexes:
            - Primary key on id
            - Index on user_id (for efficient user conversation queries)
            - Index on updated_at (for sorting by recent activity)

    Lifecycle:
        - Created when user sends first message without conversation_id
        - Updated on every new message (updated_at timestamp)
        - Persists indefinitely (archival strategy out of scope for Phase III)

    Example:
        ```python
        # Create a new conversation
        conversation = Conversation(user_id=user.id)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        ```
    """

    __tablename__ = "conversations"

    # Primary key - auto-generated integer
    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Unique identifier for the conversation"
    )

    # Required fields
    user_id: str = Field(
        foreign_key="users.id",
        nullable=False,
        index=True,
        max_length=36,
        description="Owner of the conversation (UUID)"
    )

    # Timestamps (auto-managed)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Timestamp when conversation was created (UTC)"
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"onupdate": datetime.utcnow},
        description="Timestamp when conversation was last updated (UTC)"
    )

    # Relationships
    user: Optional["User"] = Relationship(back_populates="conversations")
    messages: List["Message"] = Relationship(
        back_populates="conversation",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    class Config:
        """Pydantic configuration for the Conversation model."""
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "created_at": "2026-02-06T10:00:00Z",
                "updated_at": "2026-02-06T10:05:00Z"
            }
        }

    def __repr__(self) -> str:
        """String representation of the Conversation."""
        return f"Conversation(id={self.id}, user_id='{self.user_id}')"
