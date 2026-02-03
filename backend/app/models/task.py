"""
Task SQLModel class representing a todo item.

This module defines the Task model which represents a single todo item
with metadata including title, description, completion status, timestamps,
and user ownership.
"""

from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class Task(SQLModel, table=True):
    """
    Task model representing a todo item.

    This model uses SQLModel which combines SQLAlchemy (ORM) and Pydantic (validation).
    The table=True parameter indicates this is a database table model.

    Attributes:
        id: Unique identifier for the task (auto-generated)
        title: Task title (required, non-empty, 1-200 characters)
        description: Optional detailed description (max 1000 characters)
        completed: Completion status (defaults to False)
        created_at: Timestamp when task was created (UTC, auto-generated)
        updated_at: Timestamp when task was last updated (UTC, auto-updated)
        user_id: User identifier (placeholder for authentication in Spec-2)

    Database Table:
        Name: tasks
        Indexes:
            - Primary key on id
            - Index on user_id for efficient filtering
            - Composite index on (user_id, created_at) for efficient listing

    Example:
        ```python
        # Create a new task
        task = Task(
            title="Buy groceries",
            description="Milk, eggs, bread",
            user_id="user123"
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        ```
    """

    __tablename__ = "tasks"

    # Primary key - auto-generated integer ID
    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Unique identifier for the task (auto-generated)"
    )

    # Required fields
    title: str = Field(
        min_length=1,
        max_length=200,
        description="Task title (required, non-empty)"
    )

    completed: bool = Field(
        default=False,
        description="Completion status (defaults to False)"
    )

    user_id: str = Field(
        max_length=100,
        index=True,
        description="User identifier (placeholder for Spec-2, no enforcement)"
    )

    # Optional fields
    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Optional detailed description"
    )

    # Timestamps (auto-managed)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when task was created (UTC)"
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
        description="Timestamp when task was last updated (UTC)"
    )

    class Config:
        """Pydantic configuration for the Task model."""
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "completed": False,
                "user_id": "user123",
                "created_at": "2026-01-20T10:30:00Z",
                "updated_at": "2026-01-20T10:30:00Z"
            }
        }

    def __repr__(self) -> str:
        """String representation of the Task."""
        return (
            f"Task(id={self.id}, title='{self.title}', "
            f"completed={self.completed}, user_id='{self.user_id}')"
        )
