"""
Team Member Pydantic schemas for API request/response validation.

This module defines schemas for team membership-related API endpoints including:
- InviteMemberRequest: Request schema for inviting users to teams
- TeamMemberResponse: Response schema for team membership data
"""

from datetime import datetime
from pydantic import BaseModel, Field, validator
from app.models.team_member import TeamRole


class InviteMemberRequest(BaseModel):
    """
    Request schema for inviting a user to join a team.

    Only owners and admins can invite members. The 'owner' role cannot be
    assigned via this endpoint (use role change endpoint for ownership transfer).

    Attributes:
        user_id: UUID of the user to invite (required)
        role: Role to assign (admin/member/viewer, required)

    Example:
        ```json
        {
            "user_id": "987fcdeb-51a2-43f7-b123-456789abcdef",
            "role": "member"
        }
        ```
    """

    user_id: str = Field(
        description="UUID of the user to invite to the team",
        examples=["987fcdeb-51a2-43f7-b123-456789abcdef"]
    )

    role: TeamRole = Field(
        description="Role to assign to the user (admin/member/viewer)",
        examples=["member"]
    )

    @validator('role')
    def validate_role(cls, v):
        """Validate that role is not 'owner' (ownership transfer uses different endpoint)."""
        if v == TeamRole.OWNER:
            raise ValueError("Cannot assign 'owner' role via invite. Use role change endpoint for ownership transfer.")
        return v

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "user_id": "987fcdeb-51a2-43f7-b123-456789abcdef",
                "role": "member"
            }
        }


class ChangeRoleRequest(BaseModel):
    """
    Request schema for changing a team member's role.

    Used by team owners and admins to change member roles. Owners can assign
    any role (including owner for ownership transfer). Admins can only assign
    member/viewer roles.

    Attributes:
        role: New role to assign (owner/admin/member/viewer)

    Example:
        ```json
        {
            "role": "admin"
        }
        ```
    """

    role: TeamRole = Field(
        description="New role to assign to the team member",
        examples=["admin"]
    )

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "role": "admin"
            }
        }


class TeamMemberResponse(BaseModel):
    """
    Response schema for team membership data.

    Returns information about a user's membership in a team.

    Attributes:
        id: Unique identifier for the membership record (UUID)
        team_id: Team identifier (UUID)
        user_id: User identifier (UUID)
        role: User's role in the team (owner/admin/member/viewer)
        joined_at: Timestamp when user joined the team (UTC)

    Example:
        ```json
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "team_id": "660e8400-e29b-41d4-a716-446655440001",
            "user_id": "770e8400-e29b-41d4-a716-446655440002",
            "role": "member",
            "joined_at": "2026-02-04T10:30:00Z"
        }
        ```
    """

    id: str = Field(
        description="Unique identifier for the membership record (UUID)",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )

    team_id: str = Field(
        description="Team identifier (UUID)",
        examples=["660e8400-e29b-41d4-a716-446655440001"]
    )

    user_id: str = Field(
        description="User identifier (UUID)",
        examples=["770e8400-e29b-41d4-a716-446655440002"]
    )

    role: str = Field(
        description="User's role in the team (owner/admin/member/viewer)",
        examples=["member"]
    )

    joined_at: datetime = Field(
        description="Timestamp when user joined the team (UTC)",
        examples=["2026-02-04T10:30:00Z"]
    )

    class Config:
        """Pydantic configuration."""
        from_attributes = True  # Enable ORM mode for SQLModel compatibility
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "team_id": "660e8400-e29b-41d4-a716-446655440001",
                "user_id": "770e8400-e29b-41d4-a716-446655440002",
                "role": "member",
                "joined_at": "2026-02-04T10:30:00.000Z"
            }
        }
