"""
Task SQLModel class representing a todo item.

This module defines the Task model which represents a single todo item
with metadata including title, description, completion status, timestamps,
and user ownership.
"""

from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, Column
from sqlalchemy import ForeignKey
from pydantic import field_validator, model_validator, ConfigDict


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
        user_id: User identifier (foreign key to User, nullable for legacy tasks from Spec-1)

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

    user_id: Optional[str] = Field(
        default=None,
        sa_column=Column(
            "user_id",
            ForeignKey("users.id", ondelete="CASCADE"),
            index=True,
            nullable=True
        ),
        max_length=36,
        description="Owner of the task (foreign key to User, nullable for legacy tasks)"
    )

    team_id: Optional[str] = Field(
        default=None,
        sa_column=Column(
            "team_id",
            ForeignKey("teams.id", ondelete="SET NULL"),
            index=True,
            nullable=True
        ),
        max_length=36,
        description="Optional team ownership (foreign key to Team, NULL = personal task)"
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

    @field_validator('title', mode='before')
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        """Validate that title is not empty and within length limits.

        Note: Allows None for partial updates (validate_assignment=True).
        The title field itself is required (not Optional), so None will only
        occur during partial updates where title is not being changed.
        """
        if v is None:
            # Allow None during partial updates - the existing value will be preserved
            return v
        if not isinstance(v, str):
            raise ValueError('Title must be a string')
        if len(v) == 0 or len(v.strip()) == 0:
            raise ValueError('Title cannot be empty')
        if len(v) > 200:
            raise ValueError('Title cannot exceed 200 characters')
        return v

    @field_validator('description', mode='before')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate that description is within length limits."""
        if v is not None and len(v) > 1000:
            raise ValueError('Description cannot exceed 1000 characters')
        return v

    @field_validator('user_id', mode='before')
    @classmethod
    def validate_user_id(cls, v: Optional[str]) -> Optional[str]:
        """Validate that user_id is within length limits."""
        if v is not None and len(v) > 36:
            raise ValueError('User ID cannot exceed 36 characters')
        return v

    model_config = ConfigDict(
        validate_assignment=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "completed": False,
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "created_at": "2026-01-20T10:30:00Z",
                "updated_at": "2026-01-20T10:30:00Z"
            }
        }
    )

    def __repr__(self) -> str:
        """String representation of the Task."""
        return (
            f"Task(id={self.id}, title='{self.title}', "
            f"completed={self.completed}, user_id='{self.user_id}')"
        )
