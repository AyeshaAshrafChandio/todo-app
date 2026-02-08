"""
API routes for Task CRUD operations.

This module defines the REST API endpoints for task management:
- POST /api/{user_id}/tasks - Create new task (personal or team-owned)
- GET /api/{user_id}/tasks - List all accessible tasks (personal + team + shared)
- GET /api/{user_id}/tasks/{id} - Get single task by ID (with team access check)
- PUT /api/{user_id}/tasks/{id} - Update task (with team role permissions)
- DELETE /api/{user_id}/tasks/{id} - Delete task (with team role permissions)
- PATCH /api/{user_id}/tasks/{id}/complete - Toggle completion (with team role permissions)

Extended to support team-based tasks with role-based access control.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session
from app.database.connection import get_db
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskShareInfo
from app.services.task_service import (
    create_task,
    get_tasks_by_user,
    get_task_by_id,
    update_task,
    delete_task,
    toggle_task_completion
)
from app.services.task_share_service import get_task_shares
from app.middleware.permissions import can_access_task
from app.middleware.auth import get_current_user, verify_user_access


# Create API router for task endpoints
router = APIRouter()


@router.post(
    "/api/{user_id}/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
    description="Create a new task (personal or team-owned) with title and optional description",
    tags=["Tasks"]
)
def create_task_endpoint(
    user_id: str,
    task_data: TaskCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> TaskResponse:
    """
    Create a new task for a user (personal or team-owned).

    This endpoint accepts task creation data and returns the created task
    with auto-generated ID and timestamps. If team_id is provided, validates
    team membership and permissions (viewers cannot create tasks).

    Args:
        user_id: User identifier from path parameter
        task_data: Task creation data (title, description, team_id)
        current_user: Authenticated user info from JWT token
        db: Database session (injected via dependency)

    Returns:
        TaskResponse: Created task with all fields including team_id and access_type

    Raises:
        401 Unauthorized: Invalid or expired JWT token
        400 Bad Request: Invalid request data (handled by Pydantic)
        403 Forbidden: Not a team member or viewer role (cannot create)
        404 Not Found: Team does not exist
        500 Internal Server Error: Database error

    Example Request (Personal Task):
        POST /api/user123/tasks
        {
            "title": "Buy groceries",
            "description": "Milk, eggs, bread",
            "team_id": null
        }

    Example Request (Team Task):
        POST /api/user123/tasks
        {
            "title": "Sprint planning",
            "description": "Plan next sprint",
            "team_id": "team456"
        }

    Example Response (201 Created):
        {
            "id": 1,
            "title": "Buy groceries",
            "description": "Milk, eggs, bread",
            "completed": false,
            "created_at": "2026-01-20T10:30:00Z",
            "updated_at": "2026-01-20T10:30:00Z",
            "user_id": "user123",
            "team_id": null,
            "access_type": "owner"
        }
    """
    # Verify authenticated user matches the user_id in path
    verify_user_access(user_id, current_user)

    # Call service layer to create task (validates team membership if team_id provided)
    task = create_task(db, user_id, task_data)

    # Determine access type for response
    _, access_type = can_access_task(db, task, user_id)

    # Convert to response with access_type
    response = TaskResponse.model_validate(task)
    response.access_type = access_type

    return response


@router.get(
    "/api/{user_id}/tasks",
    response_model=List[TaskResponse],
    status_code=status.HTTP_200_OK,
    summary="List all accessible tasks",
    description="Retrieve all tasks accessible to the user (personal + team + shared)",
    tags=["Tasks"]
)
def list_tasks_endpoint(
    user_id: str,
    team_id: Optional[str] = Query(None, description="Filter by specific team"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[TaskResponse]:
    """
    Retrieve all tasks accessible to a specific user.

    This endpoint returns a union of:
    1. Personal tasks (user_id matches, team_id is NULL)
    2. Team tasks (user is a member of the team)
    3. Shared tasks (task is shared with user)

    If team_id filter is provided, only returns tasks from that team.
    Returns an empty array if no tasks exist (not an error).

    Args:
        user_id: User identifier from path parameter
        team_id: Optional team filter (query parameter)
        current_user: Authenticated user info from JWT token
        db: Database session (injected via dependency)

    Returns:
        List[TaskResponse]: Array of tasks with access_type (can be empty)

    Raises:
        401 Unauthorized: Invalid or expired JWT token
        403 Forbidden: Not a member of the specified team (if team_id filter used)

    Example Request (All accessible tasks):
        GET /api/user123/tasks

    Example Request (Team-specific tasks):
        GET /api/user123/tasks?team_id=team456

    Example Response (200 OK):
        [
            {
                "id": 1,
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "completed": false,
                "created_at": "2026-01-20T10:30:00Z",
                "updated_at": "2026-01-20T10:30:00Z",
                "user_id": "user123",
                "team_id": null,
                "access_type": "owner"
            },
            {
                "id": 2,
                "title": "Sprint planning",
                "description": "Plan next sprint",
                "completed": false,
                "created_at": "2026-01-20T11:00:00Z",
                "updated_at": "2026-01-20T11:00:00Z",
                "user_id": "user456",
                "team_id": "team789",
                "access_type": "team_member"
            }
        ]

    Example Response (200 OK - No tasks):
        []
    """
    # Verify authenticated user matches the user_id in path
    verify_user_access(user_id, current_user)

    # Call service layer to get all accessible tasks (with optional team filter)
    tasks = get_tasks_by_user(db, user_id, team_id=team_id)

    # Add access_type to each task response
    response_tasks = []
    for task in tasks:
        _, access_type = can_access_task(db, task, user_id)
        task_response = TaskResponse.model_validate(task)
        task_response.access_type = access_type
        response_tasks.append(task_response)

    return response_tasks


@router.get(
    "/api/{user_id}/tasks/{id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a single task by ID",
    description="Retrieve a specific task by its ID with team access permission check",
    tags=["Tasks"]
)
def get_task_endpoint(
    user_id: str,
    id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> TaskResponse:
    """
    Retrieve a single task by ID with team access permission check.

    This endpoint returns a specific task if the user has access through:
    - Task ownership
    - Team membership (if task is team-owned)
    - Direct sharing

    For task owners, the response includes a shared_with list showing all users
    with whom the task has been shared.

    Args:
        user_id: User identifier from path parameter
        id: Task identifier from path parameter
        current_user: Authenticated user info from JWT token
        db: Database session (injected via dependency)

    Returns:
        TaskResponse: Task details with access_type and shared_with list (if owner)

    Raises:
        401 Unauthorized: Invalid or expired JWT token
        403 Forbidden: User doesn't have access to this task
        404 Not Found: Task does not exist

    Example Request:
        GET /api/user123/tasks/5

    Example Response (200 OK - Task Owner):
        {
            "id": 5,
            "title": "Buy groceries",
            "description": "Milk, eggs, bread",
            "completed": false,
            "created_at": "2026-01-20T10:30:00Z",
            "updated_at": "2026-01-20T10:30:00Z",
            "user_id": "user123",
            "team_id": null,
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

    Example Response (200 OK - Shared User):
        {
            "id": 5,
            "title": "Buy groceries",
            "description": "Milk, eggs, bread",
            "completed": false,
            "created_at": "2026-01-20T10:30:00Z",
            "updated_at": "2026-01-20T10:30:00Z",
            "user_id": "user123",
            "team_id": null,
            "access_type": "shared_edit",
            "shared_with": null
        }

    Example Response (403 Forbidden):
        {
            "detail": "You do not have access to this task"
        }

    Example Response (404 Not Found):
        {
            "detail": "Task not found"
        }
    """
    # Verify authenticated user matches the user_id in path
    verify_user_access(user_id, current_user)

    # Call service layer to get task by ID (checks access permissions)
    # Service will raise HTTPException(404) if not found or HTTPException(403) if no access
    task = get_task_by_id(db, user_id, id)

    # Determine access type for response
    _, access_type = can_access_task(db, task, user_id)

    # Convert to response with access_type
    response = TaskResponse.model_validate(task)
    response.access_type = access_type

    # If user is the task owner, include shared_with list
    if task.user_id == user_id:
        try:
            shares = get_task_shares(db=db, task_id=task.id, owner_id=user_id)
            response.shared_with = [TaskShareInfo(**share) for share in shares]
        except Exception:
            # If there's an error getting shares, just set to empty list
            response.shared_with = []
    else:
        # Non-owners don't see the shared_with list
        response.shared_with = None

    return response


@router.put(
    "/api/{user_id}/tasks/{id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a task",
    description="Update an existing task with team role permission enforcement",
    tags=["Tasks"]
)
def update_task_endpoint(
    user_id: str,
    id: int,
    task_data: TaskUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> TaskResponse:
    """
    Update an existing task with team role permission enforcement.

    This endpoint updates a specific task if the user has edit permission:
    - Task owner: can edit
    - Team owner/admin: can edit all team tasks
    - Team member: can edit own tasks only
    - Shared with edit permission: can edit

    The updated_at timestamp is automatically refreshed.

    Args:
        user_id: User identifier from path parameter
        id: Task identifier from path parameter
        task_data: Task update data (title, description, completed)
        current_user: Authenticated user info from JWT token
        db: Database session (injected via dependency)

    Returns:
        TaskResponse: Updated task details with refreshed updated_at and access_type

    Raises:
        401 Unauthorized: Invalid or expired JWT token
        403 Forbidden: User doesn't have edit permission
        404 Not Found: Task does not exist
        422 Unprocessable Entity: Invalid request data (handled by Pydantic)

    Example Request:
        PUT /api/user123/tasks/5
        {
            "title": "Buy groceries",
            "description": "Milk, eggs, bread, cheese",
            "completed": true
        }

    Example Response (200 OK):
        {
            "id": 5,
            "title": "Buy groceries",
            "description": "Milk, eggs, bread, cheese",
            "completed": true,
            "created_at": "2026-01-20T10:30:00Z",
            "updated_at": "2026-01-20T15:45:00Z",
            "user_id": "user123",
            "team_id": null,
            "access_type": "owner"
        }

    Example Response (403 Forbidden):
        {
            "detail": "You do not have permission to edit this task"
        }

    Example Response (404 Not Found):
        {
            "detail": "Task not found"
        }
    """
    # Verify authenticated user matches the user_id in path
    verify_user_access(user_id, current_user)

    # Call service layer to update task (checks edit permissions)
    # Service will raise HTTPException(404) if not found or HTTPException(403) if no edit permission
    task = update_task(db, user_id, id, task_data)

    # Determine access type for response
    _, access_type = can_access_task(db, task, user_id)

    # Convert to response with access_type
    response = TaskResponse.model_validate(task)
    response.access_type = access_type

    return response


@router.delete(
    "/api/{user_id}/tasks/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task",
    description="Delete an existing task with team role permission enforcement",
    tags=["Tasks"]
)
def delete_task_endpoint(
    user_id: str,
    id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> None:
    """
    Delete a task with team role permission enforcement.

    This endpoint deletes a specific task if the user has delete permission:
    - Task owner: can delete
    - Team owner/admin: can delete all team tasks
    - Others: cannot delete (including shared users)

    This is a hard delete (permanent removal from database).

    Args:
        user_id: User identifier from path parameter
        id: Task identifier from path parameter
        current_user: Authenticated user info from JWT token
        db: Database session (injected via dependency)

    Returns:
        None (204 No Content - no response body)

    Raises:
        401 Unauthorized: Invalid or expired JWT token
        403 Forbidden: User doesn't have delete permission
        404 Not Found: Task does not exist

    Example Request:
        DELETE /api/user123/tasks/5

    Example Response (204 No Content):
        (No response body)

    Example Response (403 Forbidden):
        {
            "detail": "You do not have permission to delete this task"
        }

    Example Response (404 Not Found):
        {
            "detail": "Task not found"
        }
    """
    # Verify authenticated user matches the user_id in path
    verify_user_access(user_id, current_user)

    # Call service layer to delete task (checks delete permissions)
    # Service will raise HTTPException(404) if not found or HTTPException(403) if no delete permission
    delete_task(db, user_id, id)

    # Return None for 204 No Content (FastAPI handles this automatically)


@router.patch(
    "/api/{user_id}/tasks/{id}/complete",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Toggle task completion status",
    description="Toggle the completion status of a task (False → True, True → False)",
    tags=["Tasks"]
)
def toggle_task_completion_endpoint(
    user_id: str,
    id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> TaskResponse:
    """
    Toggle the completion status of a task.

    This endpoint toggles the completed field of a specific task that matches
    both the task ID and user_id. No request body is required - the endpoint
    simply flips the boolean value (False → True, True → False).
    The updated_at timestamp is automatically refreshed.

    Args:
        user_id: User identifier from path parameter
        id: Task identifier from path parameter
        current_user: Authenticated user info from JWT token
        db: Database session (injected via dependency)

    Returns:
        TaskResponse: Updated task with toggled completion status

    Raises:
        401 Unauthorized: Invalid or expired JWT token
        404 Not Found: Task does not exist or doesn't belong to user

    Example Request (task currently has completed=false):
        PATCH /api/user123/tasks/5/complete

    Example Response (200 OK):
        {
            "id": 5,
            "title": "Buy groceries",
            "description": "Milk, eggs, bread",
            "completed": true,
            "created_at": "2026-01-20T10:30:00Z",
            "updated_at": "2026-01-20T16:00:00Z",
            "user_id": "user123"
        }

    Example Request (task currently has completed=true):
        PATCH /api/user123/tasks/5/complete

    Example Response (200 OK):
        {
            "id": 5,
            "title": "Buy groceries",
            "description": "Milk, eggs, bread",
            "completed": false,
            "created_at": "2026-01-20T10:30:00Z",
            "updated_at": "2026-01-20T16:05:00Z",
            "user_id": "user123"
        }

    Example Response (404 Not Found):
        {
            "detail": "Task not found"
        }
    """
    # Verify authenticated user matches the user_id in path
    verify_user_access(user_id, current_user)

    # Call service layer to toggle task completion
    # Service will raise HTTPException(404) if not found
    task = toggle_task_completion(db, user_id, id)

    # Return task as TaskResponse (Pydantic will convert from ORM model)
    return task
