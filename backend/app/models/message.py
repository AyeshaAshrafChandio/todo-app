"""
Message SQLModel class representing a single message in a conversation.

This module defines the Message model and MessageRole enum for the AI-powered
chatbot backend (Spec 005).
"""

from datetime import datetime
from typing import Optional, TYPE_CHECKING
from enum import Enum
from sqlmodel import Field, SQLModel, Relationship, Column
from sqlalchemy import Enum as SQLAlchemyEnum

if TYPE_CHECKING:
    from .user import User
    from .conversation import Conversation


class MessageRole(str, Enum):
    """
    Enum representing the role of a message sender.

    Values:
        USER: Message sent by the user
        ASSISTANT: Message sent by the AI assistant
    """
    USER = "user"
    ASSISTANT = "assistant"


class Message(SQLModel, table=True):
    """
    Message model representing a single message in a conversation.

    This model stores individual messages from either the user or the AI assistant.
    Messages are immutable after creation and ordered chronologically.

    Attributes:
        id: Unique identifier for the message (auto-generated)
        conversation_id: Conversation this message belongs to (foreign key)
        user_id: Owner of the conversation (denormalized for security filtering)
        role: Message sender role (user or assistant)
        content: Message content text (max 10,000 characters)
        created_at: Timestamp when message was created (UTC, auto-generated)

    Relationships:
        conversation: The conversation this message belongs to
        user: The user who owns the conversation

    Database Table:
        Name: messages
        Indexes:
            - Primary key on id
            - Index on conversation_id (for efficient conversation history queries)
            - Index on user_id (for security filtering)
            - Index on created_at (for ordering messages chronologically)
            - Composite index on (conversation_id, created_at) for efficient loading

    Validation Rules:
        - conversation_id must reference existing conversation
        - user_id must match conversation owner (enforced at application level)
        - role must be either 'user' or 'assistant'
        - content length must be <= 10,000 characters
        - created_at cannot be modified after creation (immutable)

    Lifecycle:
        - Created when user sends message or agent responds
        - Immutable after creation (no updates or deletes)
        - Ordered by created_at for conversation history
        - Persists indefinitely with conversation

    Example:
        ```python
        # Create a user message
        message = Message(
            conversation_id=conversation.id,
            user_id=user.id,
            role=MessageRole.USER,
            content="Add buy groceries to my list"
        )
        db.add(message)
        db.commit()
        ```
    """

    __tablename__ = "messages"

    # Primary key - auto-generated integer
    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Unique identifier for the message"
    )

    # Required fields
    conversation_id: int = Field(
        foreign_key="conversations.id",
        nullable=False,
        index=True,
        description="Conversation this message belongs to"
    )

    user_id: str = Field(
        foreign_key="users.id",
        nullable=False,
        index=True,
        max_length=36,
        description="Owner of the conversation (denormalized for security)"
    )

    role: MessageRole = Field(
        sa_column=Column(SQLAlchemyEnum(MessageRole), nullable=False),
        description="Message sender role (user or assistant)"
    )

    content: str = Field(
        nullable=False,
        max_length=10000,
        description="Message content text (max 10,000 characters)"
    )

    # Timestamp (auto-managed, immutable)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        index=True,
        description="Timestamp when message was created (UTC)"
    )

    # Relationships
    conversation: Optional["Conversation"] = Relationship(back_populates="messages")
    user: Optional["User"] = Relationship(back_populates="messages")

    class Config:
        """Pydantic configuration for the Message model."""
        json_schema_extra = {
            "example": {
                "id": 1,
                "conversation_id": 1,
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "role": "user",
                "content": "Add buy groceries to my list",
                "created_at": "2026-02-06T10:00:00Z"
            }
        }

    def __repr__(self) -> str:
        """String representation of the Message."""
        content_preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"Message(id={self.id}, role={self.role.value}, content='{content_preview}')"
