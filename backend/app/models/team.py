"""
Team SQLModel class representing a collaboration group.

This module defines the Team model which represents a group that can own tasks
and have multiple members with different roles.
"""

from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Column, Relationship
from sqlalchemy import ForeignKey
import uuid

if TYPE_CHECKING:
    from .user import User


class Team(SQLModel, table=True):
    """
    Team model representing a collaboration group for task management.

    Teams enable multiple users to collaborate on shared tasks with role-based
    access control. Each team has an owner and can have multiple members.

    Attributes:
        id: Unique identifier for the team (UUID, auto-generated)
        name: Team name (required, unique across all teams, 1-255 characters)
        description: Optional team description (max 5000 characters)
        owner_id: Foreign key to the user who owns the team (string UUID)
        created_at: Timestamp when team was created (UTC, auto-generated)
        updated_at: Timestamp when team was last modified (UTC, auto-updated)

    Database Table:
        Name: teams
        Indexes:
            - Primary key on id
            - Unique index on name (team names must be unique)
            - Index on owner_id for efficient owner lookups
        Constraints:
            - name must be unique across all teams
            - owner_id must reference a valid user
            - Foreign key owner_id → users.id (CASCADE on delete)

    Relationships:
        - owner: Many-to-One with User (owner_id → users.id)
        - members: One-to-Many with TeamMember (team.id ← team_members.team_id)
        - tasks: One-to-Many with Task (team.id ← tasks.team_id)

    Validation Rules:
        - Name: 1-255 characters, non-empty after trimming
        - Description: Optional, max 5000 characters
        - Owner must be a valid, existing user

    State Transitions:
        - Created → Active (on creation)
        - Active → Deleted (on deletion)
        - No soft delete; deletion is permanent with cascading effects

    Cascading Behavior:
        - When team is deleted:
          - All team_members are deleted (CASCADE)
          - All tasks.team_id are set to NULL (SET NULL - converts to personal tasks)

    Example:
        ```python
        # Create a new team
        team = Team(
            name="Engineering Team",
            description="Backend development team",
            owner_id="user-uuid-here"
        )
        db.add(team)
        db.commit()
        db.refresh(team)
        ```
    """

    __tablename__ = "teams"

    # Primary key - auto-generated UUID
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        max_length=36,
        description="Unique identifier for the team (UUID)"
    )

    # Required fields
    name: str = Field(
        min_length=1,
        max_length=255,
        unique=True,
        index=True,
        description="Team name (unique across all teams)"
    )

    owner_id: str = Field(
        sa_column=Column(
            "owner_id",
            ForeignKey("users.id", ondelete="CASCADE"),
            index=True,
            nullable=False
        ),
        max_length=36,
        description="User who owns the team (foreign key to users.id)"
    )

    # Optional fields
    description: Optional[str] = Field(
        default=None,
        max_length=5000,
        description="Optional team description"
    )

    # Timestamps (auto-managed)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when team was created (UTC)"
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
        description="Timestamp when team was last modified (UTC)"
    )

    # Relationships
    owner: Optional["User"] = Relationship(back_populates="owned_teams")

    class Config:
        """Pydantic configuration for the Team model."""
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "Engineering Team",
                "description": "Backend development team",
                "owner_id": "660e8400-e29b-41d4-a716-446655440001",
                "created_at": "2026-02-04T10:30:00Z",
                "updated_at": "2026-02-04T10:30:00Z"
            }
        }

    def __repr__(self) -> str:
        """String representation of the Team."""
        return (
            f"Team(id='{self.id}', name='{self.name}', "
            f"owner_id='{self.owner_id}')"
        )
