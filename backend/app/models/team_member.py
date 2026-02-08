"""
TeamMember SQLModel class representing team membership with role-based access control.

This module defines the TeamMember model which represents the many-to-many
relationship between users and teams, with an additional role attribute for RBAC.
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


class TeamRole(str, Enum):
    """
    Enumeration of team member roles for role-based access control.

    Roles define the level of access and permissions a team member has:
    - OWNER: Full control over team, members, and all tasks
    - ADMIN: Team management and task management (cannot change owner)
    - MEMBER: Can create and edit own tasks, view all team tasks
    - VIEWER: Read-only access to team tasks
    """
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class TeamMember(SQLModel, table=True):
    """
    TeamMember model representing a user's membership in a team with a specific role.

    This is a junction table that creates a many-to-many relationship between
    users and teams, with an additional role attribute for RBAC.

    Attributes:
        id: Unique identifier for the membership record (UUID, auto-generated)
        team_id: Foreign key to the team (UUID)
        user_id: Foreign key to the user (string UUID)
        role: User's role in the team (TeamRole enum)
        joined_at: Timestamp when the user joined the team (UTC, auto-generated)

    Database Table:
        Name: team_members
        Indexes:
            - Primary key on id
            - Index on team_id for efficient team member lookups
            - Index on user_id for efficient user membership lookups
            - Index on role for role-based queries
        Constraints:
            - UNIQUE(team_id, user_id): A user can only have one membership per team
            - Foreign key team_id → teams.id (CASCADE on delete)
            - Foreign key user_id → users.id (CASCADE on delete)

    Role Permissions:
        - owner: Full control, manage team, manage members, assign all roles, delete team
        - admin: Manage members, assign member/viewer roles, create/edit/delete all tasks
        - member: Create tasks, edit own tasks, view all tasks
        - viewer: Read-only access, view all tasks

    Example:
        ```python
        # Add a user to a team as a member
        membership = TeamMember(
            team_id="team-uuid-here",
            user_id="user-uuid-here",
            role=TeamRole.MEMBER
        )
        db.add(membership)
        db.commit()
        ```
    """

    __tablename__ = "team_members"

    # Primary key - auto-generated UUID
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        max_length=36,
        description="Unique identifier for the membership record (UUID)"
    )

    # Foreign keys
    team_id: str = Field(
        sa_column=Column(
            "team_id",
            ForeignKey("teams.id", ondelete="CASCADE"),
            index=True,
            nullable=False
        ),
        max_length=36,
        description="Team this membership belongs to (foreign key to teams.id)"
    )

    user_id: str = Field(
        sa_column=Column(
            "user_id",
            ForeignKey("users.id", ondelete="CASCADE"),
            index=True,
            nullable=False
        ),
        max_length=36,
        description="User who is a member (foreign key to users.id)"
    )

    # Role with enum constraint
    role: TeamRole = Field(
        sa_column=Column(
            SQLAlchemyEnum(TeamRole),
            nullable=False,
            index=True
        ),
        description="User's role in the team (owner/admin/member/viewer)"
    )

    # Timestamp
    joined_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when user joined the team (UTC)"
    )

    # Relationships
    user: Optional["User"] = Relationship(back_populates="team_memberships")

    class Config:
        """Pydantic configuration for the TeamMember model."""
        # Unique constraint on team_id and user_id combination
        table_args = (
            UniqueConstraint('team_id', 'user_id', name='uq_team_user'),
        )

        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "team_id": "660e8400-e29b-41d4-a716-446655440001",
                "user_id": "770e8400-e29b-41d4-a716-446655440002",
                "role": "member",
                "joined_at": "2026-02-04T10:30:00Z"
            }
        }

    def __repr__(self) -> str:
        """String representation of the TeamMember."""
        return (
            f"TeamMember(id='{self.id}', team_id='{self.team_id}', "
            f"user_id='{self.user_id}', role='{self.role.value}')"
        )
