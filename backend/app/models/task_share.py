"""
TaskShare SQLModel class representing direct task sharing between users.

This module defines the TaskShare model which enables users to share specific
tasks with other users outside of team context, with view or edit permissions.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Column, Relationship
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.types import Enum as SQLAlchemyEnum
import uuid

if TYPE_CHECKING:
    from .user import User


class SharePermission(str, Enum):
    """
    Enumeration of task sharing permission levels.

    Permissions define what actions a user can perform on a shared task:
    - VIEW: Read-only access, can view task details but cannot modify
    - EDIT: Modify access, can view and update task details but cannot delete
    """
    VIEW = "view"
    EDIT = "edit"


class TaskShare(SQLModel, table=True):
    """
    TaskShare model representing direct sharing of a task with a specific user.

    This model enables collaboration outside of team context by allowing task
    owners to share specific tasks with individual users.

    Attributes:
        id: Unique identifier for the share record (UUID, auto-generated)
        task_id: Foreign key to the task being shared (integer)
        shared_with_user_id: Foreign key to the user receiving access (string UUID)
        shared_by_user_id: Foreign key to the user who shared the task (string UUID)
        permission: Level of access granted (SharePermission enum)
        shared_at: Timestamp when the task was shared (UTC, auto-generated)

    Database Table:
        Name: task_shares
        Indexes:
            - Primary key on id
            - Index on task_id for efficient task share lookups
            - Index on shared_with_user_id for efficient user share lookups
            - Index on shared_by_user_id for tracking who shared what
        Constraints:
            - UNIQUE(task_id, shared_with_user_id): A task can only be shared once with each user
            - Foreign key task_id → tasks.id (CASCADE on delete)
            - Foreign key shared_with_user_id → users.id (CASCADE on delete)
            - Foreign key shared_by_user_id → users.id (CASCADE on delete)

    Permission Levels:
        - view: Read-only access to task details
        - edit: Can view and update task details (cannot delete)

    Validation Rules (enforced at application level):
        - Cannot share a task with yourself
        - Only task owner can share tasks
        - Task must exist and be accessible to sharer

    Example:
        ```python
        # Share a task with edit permission
        share = TaskShare(
            task_id=123,
            shared_with_user_id="user-uuid-here",
            shared_by_user_id="owner-uuid-here",
            permission=SharePermission.EDIT
        )
        db.add(share)
        db.commit()
        ```
    """

    __tablename__ = "task_shares"

    # Primary key - auto-generated UUID
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        max_length=36,
        description="Unique identifier for the share record (UUID)"
    )

    # Foreign keys
    task_id: int = Field(
        sa_column=Column(
            "task_id",
            ForeignKey("tasks.id", ondelete="CASCADE"),
            index=True,
            nullable=False
        ),
        description="Task being shared (foreign key to tasks.id)"
    )

    shared_with_user_id: str = Field(
        sa_column=Column(
            "shared_with_user_id",
            ForeignKey("users.id", ondelete="CASCADE"),
            index=True,
            nullable=False
        ),
        max_length=36,
        description="User receiving access (foreign key to users.id)"
    )

    shared_by_user_id: str = Field(
        sa_column=Column(
            "shared_by_user_id",
            ForeignKey("users.id", ondelete="CASCADE"),
            index=True,
            nullable=False
        ),
        max_length=36,
        description="User who shared the task (foreign key to users.id)"
    )

    # Permission with enum constraint
    permission: SharePermission = Field(
        sa_column=Column(
            SQLAlchemyEnum(SharePermission),
            nullable=False
        ),
        description="Level of access granted (view/edit)"
    )

    # Timestamp
    shared_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when task was shared (UTC)"
    )

    # Relationships
    shared_with_user: Optional["User"] = Relationship(
        back_populates="received_shares",
        sa_relationship_kwargs={"foreign_keys": "[TaskShare.shared_with_user_id]"}
    )

    shared_by_user: Optional["User"] = Relationship(
        back_populates="given_shares",
        sa_relationship_kwargs={"foreign_keys": "[TaskShare.shared_by_user_id]"}
    )

    class Config:
        """Pydantic configuration for the TaskShare model."""
        # Unique constraint on task_id and shared_with_user_id combination
        table_args = (
            UniqueConstraint('task_id', 'shared_with_user_id', name='uq_task_share'),
        )

        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "task_id": 123,
                "shared_with_user_id": "660e8400-e29b-41d4-a716-446655440001",
                "shared_by_user_id": "770e8400-e29b-41d4-a716-446655440002",
                "permission": "edit",
                "shared_at": "2026-02-04T10:30:00Z"
            }
        }

    def __repr__(self) -> str:
        """String representation of the TaskShare."""
        return (
            f"TaskShare(id='{self.id}', task_id={self.task_id}, "
            f"shared_with='{self.shared_with_user_id}', permission='{self.permission.value}')"
        )
