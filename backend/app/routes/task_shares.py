"""
API routes for Task Sharing operations.

This module defines the REST API endpoints for task sharing:
- POST /api/tasks/{task_id}/share - Share a task with another user
- DELETE /api/tasks/{task_id}/share/{user_id} - Revoke task sharing
- GET /api/tasks/shared-with-me - List tasks shared with authenticated user

All endpoints require JWT authentication.
"""

from typing import List
from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.database.connection import get_db
from app.schemas.task_share import (
    ShareTaskRequest,
    TaskShareResponse,
    SharedTaskResponse
)
from app.services.task_share_service import (
    share_task,
    revoke_share,
    get_shared_tasks
)
from app.middleware.auth import get_current_user


# Create API router for task sharing endpoints
router = APIRouter()


@router.post(
    "/api/tasks/{task_id}/share",
    response_model=TaskShareResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Share a task with another user",
    description="Share a task with another user, granting them view or edit permission. Only task owner can share.",
    tags=["Task Sharing"]
)
def share_task_endpoint(
    task_id: int,
    share_data: ShareTaskRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> TaskShareResponse:
    """
    Share a task with another user.

    This endpoint allows the task owner to share a task with another user,
    granting them either view (read-only) or edit (read-write) permission.

    Permission Levels:
    - view: User can view task details but cannot modify
    - edit: User can view and update task details (cannot delete)

    Args:
        task_id: Task identifier from path parameter
        share_data: Share request data (user_id and permission)
        current_user: Authenticated user info from JWT token
        db: Database session (injected via dependency)

    Returns:
        TaskShareResponse: Created share record with all fields

    Raises:
        400 Bad Request: Invalid request data or attempting to share with self
        401 Unauthorized: Invalid or expired JWT token
        403 Forbidden: Not the task owner
        404 Not Found: Task or target user does not exist
        409 Conflict: Task already shared with this user

    Example Request:
        POST /api/tasks/123/share
        {
            "user_id": "789abcde-f012-3456-7890-abcdef123456",
            "permission": "edit"
        }

    Example Response (201 Created):
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "task_id": 123,
            "shared_with_user_id": "789abcde-f012-3456-7890-abcdef123456",
            "shared_by_user_id": "660e8400-e29b-41d4-a716-446655440001",
            "permission": "edit",
            "shared_at": "2026-02-04T10:30:00Z"
        }
    """
    # Get authenticated user ID
    owner_id = current_user["user_id"]

    # Call service layer to create share
    share = share_task(
        db=db,
        task_id=task_id,
        owner_id=owner_id,
        shared_with_user_id=share_data.user_id,
        permission=share_data.permission
    )

    # Convert to response schema
    return TaskShareResponse.model_validate(share)


@router.delete(
    "/api/tasks/{task_id}/share/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Revoke task sharing",
    description="Revoke task sharing access from a user. Only task owner can revoke.",
    tags=["Task Sharing"]
)
def revoke_share_endpoint(
    task_id: int,
    user_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> None:
    """
    Revoke task sharing access from a user.

    This endpoint allows the task owner to revoke sharing access from a user,
    removing their ability to view or edit the task.

    Args:
        task_id: Task identifier from path parameter
        user_id: User identifier to revoke access from (path parameter)
        current_user: Authenticated user info from JWT token
        db: Database session (injected via dependency)

    Returns:
        None (204 No Content - no response body)

    Raises:
        401 Unauthorized: Invalid or expired JWT token
        403 Forbidden: Not the task owner
        404 Not Found: Task or share does not exist

    Example Request:
        DELETE /api/tasks/123/share/789abcde-f012-3456-7890-abcdef123456

    Example Response (204 No Content):
        (No response body)
    """
    # Get authenticated user ID
    owner_id = current_user["user_id"]

    # Call service layer to revoke share
    revoke_share(
        db=db,
        task_id=task_id,
        owner_id=owner_id,
        shared_with_user_id=user_id
    )

    # Return None for 204 No Content (FastAPI handles this automatically)


@router.get(
    "/api/tasks/shared-with-me",
    response_model=List[SharedTaskResponse],
    status_code=status.HTTP_200_OK,
    summary="List tasks shared with me",
    description="Retrieve all tasks that have been shared with the authenticated user",
    tags=["Task Sharing"]
)
def get_shared_tasks_endpoint(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[SharedTaskResponse]:
    """
    List all tasks that have been shared with the authenticated user.

    This endpoint returns all tasks that other users have shared with the
    authenticated user, including the owner's email and the user's permission
    level for each task.

    Args:
        current_user: Authenticated user info from JWT token
        db: Database session (injected via dependency)

    Returns:
        List[SharedTaskResponse]: Array of shared tasks with owner email and permission

    Raises:
        401 Unauthorized: Invalid or expired JWT token

    Example Request:
        GET /api/tasks/shared-with-me

    Example Response (200 OK):
        [
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
        ]

    Example Response (200 OK - No shared tasks):
        []
    """
    # Get authenticated user ID
    user_id = current_user["user_id"]

    # Call service layer to get shared tasks
    shared_tasks = get_shared_tasks(db=db, user_id=user_id)

    # Convert to response schema
    return [SharedTaskResponse(**task) for task in shared_tasks]
