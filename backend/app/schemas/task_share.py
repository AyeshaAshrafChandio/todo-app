"""
Task Sharing Pydantic schemas for API request/response validation.

This module defines schemas for task sharing endpoints including:
- ShareTaskRequest: Request schema for sharing a task with another user
- TaskShareResponse: Response schema for share record data
- SharedTaskResponse: Response schema for tasks shared with the user
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator


class ShareTaskRequest(BaseModel):
    """
    Request schema for sharing a task with another user.

    Used by POST /api/tasks/{task_id}/share endpoint.

    Attributes:
        user_id: UUID of the user to share the task with (required)
        permission: Access level to grant (view or edit, required)

    Example:
        ```json
        {
            "user_id": "789abcde-f012-3456-7890-abcdef123456",
            "permission": "edit"
        }
        ```
    """

    user_id: str = Field(
        min_length=36,
        max_length=36,
        description="UUID of the user to share the task with",
        examples=["789abcde-f012-3456-7890-abcdef123456"]
    )

    permission: str = Field(
        description="Access level to grant (view or edit)",
        examples=["edit"]
    )

    @validator('permission')
    def validate_permission(cls, v):
        """Validate permission is either 'view' or 'edit'."""
        if v not in ['view', 'edit']:
            raise ValueError("Permission must be either 'view' or 'edit'")
        return v

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "user_id": "789abcde-f012-3456-7890-abcdef123456",
                "permission": "edit"
            }
        }


class TaskShareResponse(BaseModel):
    """
    Response schema for task share record.

    Used by POST /api/tasks/{task_id}/share endpoint.

    Attributes:
        id: Unique identifier for the share record (UUID)
        task_id: ID of the task being shared
        shared_with_user_id: UUID of the user receiving access
        shared_by_user_id: UUID of the user who shared the task
        permission: Access level granted (view or edit)
        shared_at: Timestamp when the task was shared (UTC)

    Example:
        ```json
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "task_id": 123,
            "shared_with_user_id": "789abcde-f012-3456-7890-abcdef123456",
            "shared_by_user_id": "660e8400-e29b-41d4-a716-446655440001",
            "permission": "edit",
            "shared_at": "2026-02-04T10:30:00Z"
        }
        ```
    """

    id: str = Field(
        description="Unique identifier for the share record (UUID)",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )

    task_id: int = Field(
        description="ID of the task being shared",
        examples=[123]
    )

    shared_with_user_id: str = Field(
        description="UUID of the user receiving access",
        examples=["789abcde-f012-3456-7890-abcdef123456"]
    )

    shared_by_user_id: str = Field(
        description="UUID of the user who shared the task",
        examples=["660e8400-e29b-41d4-a716-446655440001"]
    )

    permission: str = Field(
        description="Access level granted (view or edit)",
        examples=["edit"]
    )

    shared_at: datetime = Field(
        description="Timestamp when the task was shared (UTC)",
        examples=["2026-02-04T10:30:00Z"]
    )

    class Config:
        """Pydantic configuration."""
        from_attributes = True  # Enable ORM mode for SQLModel compatibility
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "task_id": 123,
                "shared_with_user_id": "789abcde-f012-3456-7890-abcdef123456",
                "shared_by_user_id": "660e8400-e29b-41d4-a716-446655440001",
                "permission": "edit",
                "shared_at": "2026-02-04T10:30:00.000Z"
            }
        }


class SharedTaskResponse(BaseModel):
    """
    Response schema for tasks shared with the authenticated user.

    Used by GET /api/tasks/shared-with-me endpoint.

    Attributes:
        id: Task identifier
        title: Task title
        description: Optional task description
        completed: Task completion status
        owner_email: Email of the task owner (not owner_id)
        permission: User's access level (view or edit)
        shared_at: Timestamp when the task was shared (UTC)
        created_at: Timestamp when task was created (UTC)
        updated_at: Timestamp when task was last modified (UTC)

    Example:
        ```json
        {
            "id": 123,
            "title": "Review pull request",
            "description": "Review PR #456",
            "completed": false,
            "owner_email": "owner@example.com",
            "permission": "edit",
            "shared_at": "2026-02-04T10:30:00Z",
            "created_at": "2026-02-03T09:00:00Z",
            "updated_at": "2026-02-04T10:30:00Z"
        }
        ```
    """

    id: int = Field(
        description="Task identifier",
        examples=[123]
    )

    title: str = Field(
        description="Task title",
        examples=["Review pull request"]
    )

    description: Optional[str] = Field(
        default=None,
        description="Optional task description",
        examples=["Review PR #456"]
    )

    completed: bool = Field(
        description="Task completion status",
        examples=[False]
    )

    owner_email: str = Field(
        description="Email of the task owner",
        examples=["owner@example.com"]
    )

    permission: str = Field(
        description="User's access level (view or edit)",
        examples=["edit"]
    )

    shared_at: datetime = Field(
        description="Timestamp when the task was shared (UTC)",
        examples=["2026-02-04T10:30:00Z"]
    )

    created_at: datetime = Field(
        description="Timestamp when task was created (UTC)",
        examples=["2026-02-03T09:00:00Z"]
    )

    updated_at: datetime = Field(
        description="Timestamp when task was last modified (UTC)",
        examples=["2026-02-04T10:30:00Z"]
    )

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "id": 123,
                "title": "Review pull request",
                "description": "Review PR #456",
                "completed": False,
                "owner_email": "owner@example.com",
                "permission": "edit",
                "shared_at": "2026-02-04T10:30:00.000Z",
                "created_at": "2026-02-03T09:00:00.000Z",
                "updated_at": "2026-02-04T10:30:00.000Z"
            }
        }


class TaskShareInfo(BaseModel):
    """
    Schema for share information in task detail response.

    Used in the shared_with list of GET /api/tasks/{task_id} response.

    Attributes:
        user_id: UUID of the user with whom the task is shared
        email: Email of the user with whom the task is shared
        permission: Access level granted (view or edit)
        shared_at: Timestamp when the task was shared (UTC)

    Example:
        ```json
        {
            "user_id": "789abcde-f012-3456-7890-abcdef123456",
            "email": "colleague@example.com",
            "permission": "edit",
            "shared_at": "2026-02-04T10:30:00Z"
        }
        ```
    """

    user_id: str = Field(
        description="UUID of the user with whom the task is shared",
        examples=["789abcde-f012-3456-7890-abcdef123456"]
    )

    email: str = Field(
        description="Email of the user with whom the task is shared",
        examples=["colleague@example.com"]
    )

    permission: str = Field(
        description="Access level granted (view or edit)",
        examples=["edit"]
    )

    shared_at: datetime = Field(
        description="Timestamp when the task was shared (UTC)",
        examples=["2026-02-04T10:30:00Z"]
    )

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "user_id": "789abcde-f012-3456-7890-abcdef123456",
                "email": "colleague@example.com",
                "permission": "edit",
                "shared_at": "2026-02-04T10:30:00.000Z"
            }
        }
