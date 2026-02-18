"""
Base SQLModel class with common fields for all database models.

This module provides a base class that includes standard fields (id, created_at, updated_at)
that should be present in all database tables. All models should inherit from this base class
to ensure consistency across the schema.
"""

from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class BaseModel(SQLModel):
    """
    Base model class with common fields for all database tables.

    This class provides standard fields that should be present in all tables:
    - id: Auto-incrementing primary key
    - created_at: Timestamp when record was created (UTC, auto-generated)
    - updated_at: Timestamp when record was last updated (UTC, auto-updated)

    All database models should inherit from this class to ensure consistency.

    Example:
        ```python
        class Task(BaseModel, table=True):
            __tablename__ = "tasks"

            title: str = Field(max_length=200)
            description: Optional[str] = Field(default=None, max_length=1000)
            completed: bool = Field(default=False)
            user_id: str = Field(foreign_key="users.id")
        ```

    Note:
        - The table=True parameter must be specified in the child class, not here
        - Child classes should define __tablename__ explicitly
        - created_at uses default_factory to generate timestamp at creation time
        - updated_at uses sa_column_kwargs with onupdate to auto-update on changes
    """

    # Primary key - auto-generated integer ID
    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Unique identifier (auto-generated)"
    )

    # Timestamps (auto-managed)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Timestamp when record was created (UTC, auto-generated)"
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
        nullable=False,
        description="Timestamp when record was last updated (UTC, auto-updated)"
    )

    class Config:
        """Pydantic configuration for the base model."""
        # Enable validation on assignment (validate when fields are updated)
        validate_assignment = True
        # Use enum values instead of enum objects in JSON
        use_enum_values = True
        # Allow arbitrary types (needed for SQLAlchemy types)
        arbitrary_types_allowed = True
