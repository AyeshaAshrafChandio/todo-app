"""
Pydantic schemas for Task API request/response validation.

This module defines the data validation schemas used by the FastAPI endpoints:
- TaskCreate: Schema for creating new tasks (POST requests)
- TaskUpdate: Schema for updating existing tasks (PUT requests)
- TaskResponse: Schema for task responses (all endpoints)
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict, field_validator


class TaskCreate(BaseModel):
    """
    Schema for creating a new task.

    Used by POST /api/tasks endpoint.
    Supports both personal tasks (team_id=None) and team tasks (team_id provided).
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "team_id": None
            }
        }
    )

    title: str = Field(
        min_length=1,
        max_length=200,
        description="Task title (required, non-empty)"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Optional detailed description"
    )
    team_id: Optional[str] = Field(
        default=None,
        max_length=36,
        description="Optional team ID for team-owned tasks (null for personal tasks)"
    )

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate that title is not empty."""
        if not v or len(v.strip()) == 0:
            raise ValueError('Title cannot be empty')
        return v


class TaskUpdate(BaseModel):
    """
    Schema for updating an existing task.

    Used by PUT /api/{user_id}/tasks/{id} endpoint.
    All fields are optional to support partial updates.
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Buy groceries",
                "description": "Milk, eggs, bread, cheese",
                "completed": False
            }
        }
    )

    title: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=200,
        description="Task title (optional for partial updates)"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Optional detailed description"
    )
    completed: Optional[bool] = Field(
        default=None,
        description="Completion status (optional)"
    )

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        """Validate that title is not empty if provided."""
        if v is not None and (not v or len(v.strip()) == 0):
            raise ValueError('Title cannot be empty')
        return v


class TaskShareInfo(BaseModel):
    """
    Schema for share information in task detail response.

    Used in the shared_with list of TaskResponse.

    Attributes:
        user_id: UUID of the user with whom the task is shared
        email: Email of the user with whom the task is shared
        permission: Access level granted (view or edit)
        shared_at: Timestamp when the task was shared (UTC)
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_id": "789abcde-f012-3456-7890-abcdef123456",
                "email": "colleague@example.com",
                "permission": "edit",
                "shared_at": "2026-02-04T10:30:00.000Z"
            }
        }
    )

    user_id: str = Field(
        description="UUID of the user with whom the task is shared"
    )
    email: str = Field(
        description="Email of the user with whom the task is shared"
    )
    permission: str = Field(
        description="Access level granted (view or edit)"
    )
    shared_at: datetime = Field(
        description="Timestamp when the task was shared (UTC)"
    )


class TaskResponse(BaseModel):
    """
    Schema for task responses.

    Used by all endpoints that return task data.
    Includes all task fields from the database model plus access control information.
    For task owners, includes the shared_with list showing all users with whom the task is shared.
    """
    model_config = ConfigDict(
        from_attributes=True,  # Enable ORM mode for SQLModel compatibility
        json_schema_extra={
            "example": {
                "id": 1,
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "completed": False,
                "created_at": "2026-01-20T10:30:00Z",
                "updated_at": "2026-01-20T10:30:00Z",
                "user_id": "user123",
                "team_id": None,
                "access_type": "owner",
                "shared_with": [
                    {
                        "user_id": "789abcde-f012-3456-7890-abcdef123456",
                        "email": "colleague@example.com",
                        "permission": "edit",
                        "shared_at": "2026-02-04T10:30:00Z"
                    }
                ]
            }
        }
    )

    id: int
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime
    user_id: str
    team_id: Optional[str] = Field(
        default=None,
        description="Team ID if task is team-owned, null for personal tasks"
    )
    access_type: Optional[str] = Field(
        default=None,
        description="User's access level: owner, team_owner, team_admin, team_member, team_viewer, shared_view, shared_edit"
    )
    shared_with: Optional[List[TaskShareInfo]] = Field(
        default=None,
        description="List of users with whom the task is shared (only visible to task owner)"
    )
