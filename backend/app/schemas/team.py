"""
Team Pydantic schemas for API request/response validation.

This module defines schemas for team-related API endpoints including:
- TeamCreate: Request schema for creating new teams
- TeamResponse: Response schema for team data
- TeamUpdate: Request schema for updating team settings
- TeamListResponse: Response schema for team list with membership info
- TeamDetailResponse: Response schema for team details with members
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator


class TeamCreate(BaseModel):
    """
    Request schema for creating a new team.

    The authenticated user automatically becomes the team owner.

    Attributes:
        name: Team name (required, 1-255 chars, must be unique)
        description: Optional team description (max 5000 chars)

    Example:
        ```json
        {
            "name": "Engineering Team",
            "description": "Core engineering team for product development"
        }
        ```
    """

    name: str = Field(
        min_length=1,
        max_length=255,
        description="Team name (unique across all teams)",
        examples=["Engineering Team"]
    )

    description: Optional[str] = Field(
        default=None,
        max_length=5000,
        description="Optional team description",
        examples=["Core engineering team for product development"]
    )

    @validator('name')
    def validate_name(cls, v):
        """Validate team name is not empty after trimming."""
        if not v or not v.strip():
            raise ValueError("Team name cannot be empty or whitespace only")
        return v.strip()

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "name": "Engineering Team",
                "description": "Core engineering team for product development"
            }
        }


class TeamResponse(BaseModel):
    """
    Response schema for team data.

    Returns complete team information including owner and timestamps.

    Attributes:
        id: Unique identifier for the team (UUID)
        name: Team name
        description: Optional team description
        owner_id: User ID of the team owner
        created_at: Timestamp when team was created (UTC)
        updated_at: Timestamp when team was last modified (UTC)

    Example:
        ```json
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "name": "Engineering Team",
            "description": "Core engineering team",
            "owner_id": "660e8400-e29b-41d4-a716-446655440001",
            "created_at": "2026-02-04T10:30:00Z",
            "updated_at": "2026-02-04T10:30:00Z"
        }
        ```
    """

    id: str = Field(
        description="Unique identifier for the team (UUID)",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )

    name: str = Field(
        description="Team name",
        examples=["Engineering Team"]
    )

    description: Optional[str] = Field(
        default=None,
        description="Optional team description",
        examples=["Core engineering team for product development"]
    )

    owner_id: str = Field(
        description="User ID of the team owner (UUID)",
        examples=["660e8400-e29b-41d4-a716-446655440001"]
    )

    created_at: datetime = Field(
        description="Timestamp when team was created (UTC)",
        examples=["2026-02-04T10:30:00Z"]
    )

    updated_at: datetime = Field(
        description="Timestamp when team was last modified (UTC)",
        examples=["2026-02-04T10:30:00Z"]
    )

    class Config:
        """Pydantic configuration."""
        from_attributes = True  # Enable ORM mode for SQLModel compatibility
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "Engineering Team",
                "description": "Core engineering team for product development",
                "owner_id": "660e8400-e29b-41d4-a716-446655440001",
                "created_at": "2026-02-04T10:30:00.000Z",
                "updated_at": "2026-02-04T10:30:00.000Z"
            }
        }


class TeamUpdate(BaseModel):
    """
    Request schema for updating team settings.

    All fields are optional. Only provided fields will be updated.

    Attributes:
        name: New team name (optional, 1-255 chars, must be unique)
        description: New team description (optional, max 5000 chars)

    Example:
        ```json
        {
            "description": "Updated team description"
        }
        ```
    """

    name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="New team name (optional, must be unique)",
        examples=["Engineering Team - Updated"]
    )

    description: Optional[str] = Field(
        default=None,
        max_length=5000,
        description="New team description (optional)",
        examples=["Updated team description"]
    )

    @validator('name')
    def validate_name(cls, v):
        """Validate team name is not empty after trimming if provided."""
        if v is not None:
            if not v.strip():
                raise ValueError("Team name cannot be empty or whitespace only")
            return v.strip()
        return v

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "description": "Updated team description"
            }
        }


class TeamListResponse(BaseModel):
    """
    Response schema for team list with membership information.

    Used by GET /api/teams to return teams the user is a member of.

    Attributes:
        id: Unique identifier for the team (UUID)
        name: Team name
        description: Optional team description
        role: User's role in the team (owner/admin/member/viewer)
        member_count: Number of members in the team
        created_at: Timestamp when team was created (UTC)

    Example:
        ```json
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "name": "Engineering Team",
            "description": "Core engineering team",
            "role": "owner",
            "member_count": 5,
            "created_at": "2026-02-04T10:30:00Z"
        }
        ```
    """

    id: str = Field(
        description="Unique identifier for the team (UUID)",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )

    name: str = Field(
        description="Team name",
        examples=["Engineering Team"]
    )

    description: Optional[str] = Field(
        default=None,
        description="Optional team description",
        examples=["Core engineering team for product development"]
    )

    role: str = Field(
        description="User's role in the team (owner/admin/member/viewer)",
        examples=["owner"]
    )

    member_count: int = Field(
        description="Number of members in the team",
        examples=[5]
    )

    created_at: datetime = Field(
        description="Timestamp when team was created (UTC)",
        examples=["2026-02-04T10:30:00Z"]
    )

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "Engineering Team",
                "description": "Core engineering team for product development",
                "role": "owner",
                "member_count": 5,
                "created_at": "2026-02-04T10:30:00.000Z"
            }
        }


class TeamMemberInfo(BaseModel):
    """
    Schema for team member information in team details.

    Attributes:
        user_id: User's unique identifier (UUID)
        email: User's email address
        role: User's role in the team (owner/admin/member/viewer)
        joined_at: Timestamp when user joined the team (UTC)

    Example:
        ```json
        {
            "user_id": "660e8400-e29b-41d4-a716-446655440001",
            "email": "user@example.com",
            "role": "owner",
            "joined_at": "2026-02-04T10:30:00Z"
        }
        ```
    """

    user_id: str = Field(
        description="User's unique identifier (UUID)",
        examples=["660e8400-e29b-41d4-a716-446655440001"]
    )

    email: str = Field(
        description="User's email address",
        examples=["user@example.com"]
    )

    role: str = Field(
        description="User's role in the team (owner/admin/member/viewer)",
        examples=["owner"]
    )

    joined_at: datetime = Field(
        description="Timestamp when user joined the team (UTC)",
        examples=["2026-02-04T10:30:00Z"]
    )

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "user_id": "660e8400-e29b-41d4-a716-446655440001",
                "email": "user@example.com",
                "role": "owner",
                "joined_at": "2026-02-04T10:30:00.000Z"
            }
        }


class TeamDetailResponse(BaseModel):
    """
    Response schema for detailed team information including all members.

    Used by GET /api/teams/{team_id} to return complete team details.

    Attributes:
        id: Unique identifier for the team (UUID)
        name: Team name
        description: Optional team description
        owner_id: User ID of the team owner
        created_at: Timestamp when team was created (UTC)
        updated_at: Timestamp when team was last modified (UTC)
        members: List of all team members with their roles

    Example:
        ```json
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "name": "Engineering Team",
            "description": "Core engineering team",
            "owner_id": "660e8400-e29b-41d4-a716-446655440001",
            "created_at": "2026-02-04T10:30:00Z",
            "updated_at": "2026-02-04T10:30:00Z",
            "members": [
                {
                    "user_id": "660e8400-e29b-41d4-a716-446655440001",
                    "email": "owner@example.com",
                    "role": "owner",
                    "joined_at": "2026-02-04T10:30:00Z"
                }
            ]
        }
        ```
    """

    id: str = Field(
        description="Unique identifier for the team (UUID)",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )

    name: str = Field(
        description="Team name",
        examples=["Engineering Team"]
    )

    description: Optional[str] = Field(
        default=None,
        description="Optional team description",
        examples=["Core engineering team for product development"]
    )

    owner_id: str = Field(
        description="User ID of the team owner (UUID)",
        examples=["660e8400-e29b-41d4-a716-446655440001"]
    )

    created_at: datetime = Field(
        description="Timestamp when team was created (UTC)",
        examples=["2026-02-04T10:30:00Z"]
    )

    updated_at: datetime = Field(
        description="Timestamp when team was last modified (UTC)",
        examples=["2026-02-04T10:30:00Z"]
    )

    members: List[TeamMemberInfo] = Field(
        description="List of all team members with their roles",
        examples=[[{
            "user_id": "660e8400-e29b-41d4-a716-446655440001",
            "email": "owner@example.com",
            "role": "owner",
            "joined_at": "2026-02-04T10:30:00Z"
        }]]
    )

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "Engineering Team",
                "description": "Core engineering team for product development",
                "owner_id": "660e8400-e29b-41d4-a716-446655440001",
                "created_at": "2026-02-04T10:30:00.000Z",
                "updated_at": "2026-02-04T10:30:00.000Z",
                "members": [
                    {
                        "user_id": "660e8400-e29b-41d4-a716-446655440001",
                        "email": "owner@example.com",
                        "role": "owner",
                        "joined_at": "2026-02-04T10:30:00.000Z"
                    }
                ]
            }
        }
