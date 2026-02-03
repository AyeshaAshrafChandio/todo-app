"""
API routes for Task CRUD operations.

This module defines the REST API endpoints for task management:
- POST /api/{user_id}/tasks - Create new task
- GET /api/{user_id}/tasks - List all tasks for user
- GET /api/{user_id}/tasks/{id} - Get single task by ID
- PUT /api/{user_id}/tasks/{id} - Update task (User Story 2)
- DELETE /api/{user_id}/tasks/{id} - Delete task (User Story 2)
- PATCH /api/{user_id}/tasks/{id}/complete - Toggle completion (User Story 3)
"""

from typing import List
from fastapi import APIRouter, Depends, status
from sqlmodel import Session
from app.database.connection import get_db
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.services.task_service import (
    create_task,
    get_tasks_by_user,
    get_task_by_id,
    update_task,
    delete_task,
    toggle_task_completion
)


# Create API router for task endpoints
router = APIRouter()


@router.post(
    "/api/{user_id}/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
    description="Create a new task for the specified user with title and optional description",
    tags=["Tasks"]
)
def create_task_endpoint(
    user_id: str,
    task_data: TaskCreate,
    db: Session = Depends(get_db)
) -> TaskResponse:
    """
    Create a new task for a user.

    This endpoint accepts task creation data and returns the created task
    with auto-generated ID and timestamps.

    Args:
        user_id: User identifier from path parameter
        task_data: Task creation data (title, description)
        db: Database session (injected via dependency)

    Returns:
        TaskResponse: Created task with all fields

    Raises:
        422 Unprocessable Entity: Invalid request data (handled by Pydantic)
        500 Internal Server Error: Database error

    Example Request:
        POST /api/user123/tasks
        {
            "title": "Buy groceries",
            "description": "Milk, eggs, bread"
        }

    Example Response (201 Created):
        {
            "id": 1,
            "title": "Buy groceries",
            "description": "Milk, eggs, bread",
            "completed": false,
            "created_at": "2026-01-20T10:30:00Z",
            "updated_at": "2026-01-20T10:30:00Z",
            "user_id": "user123"
        }
    """
    # Call service layer to create task
    task = create_task(db, user_id, task_data)

    # Return task as TaskResponse (Pydantic will convert from ORM model)
    return task


@router.get(
    "/api/{user_id}/tasks",
    response_model=List[TaskResponse],
    status_code=status.HTTP_200_OK,
    summary="List all tasks for a user",
    description="Retrieve all tasks belonging to the specified user",
    tags=["Tasks"]
)
def list_tasks_endpoint(
    user_id: str,
    db: Session = Depends(get_db)
) -> List[TaskResponse]:
    """
    Retrieve all tasks for a specific user.

    This endpoint returns all tasks belonging to the specified user_id.
    Returns an empty array if no tasks exist (not an error).

    Args:
        user_id: User identifier from path parameter
        db: Database session (injected via dependency)

    Returns:
        List[TaskResponse]: Array of tasks (can be empty)

    Example Request:
        GET /api/user123/tasks

    Example Response (200 OK):
        [
            {
                "id": 1,
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "completed": false,
                "created_at": "2026-01-20T10:30:00Z",
                "updated_at": "2026-01-20T10:30:00Z",
                "user_id": "user123"
            },
            {
                "id": 2,
                "title": "Walk the dog",
                "description": null,
                "completed": true,
                "created_at": "2026-01-20T11:00:00Z",
                "updated_at": "2026-01-20T12:00:00Z",
                "user_id": "user123"
            }
        ]

    Example Response (200 OK - No tasks):
        []
    """
    # Call service layer to get all tasks for user
    tasks = get_tasks_by_user(db, user_id)

    # Return tasks as List[TaskResponse] (Pydantic will convert from ORM models)
    return tasks


@router.get(
    "/api/{user_id}/tasks/{id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a single task by ID",
    description="Retrieve a specific task by its ID for the specified user",
    tags=["Tasks"]
)
def get_task_endpoint(
    user_id: str,
    id: int,
    db: Session = Depends(get_db)
) -> TaskResponse:
    """
    Retrieve a single task by ID.

    This endpoint returns a specific task that matches both the task ID
    and user_id. Ensures users can only access their own tasks.

    Args:
        user_id: User identifier from path parameter
        id: Task identifier from path parameter
        db: Database session (injected via dependency)

    Returns:
        TaskResponse: Task details

    Raises:
        404 Not Found: Task does not exist or doesn't belong to user

    Example Request:
        GET /api/user123/tasks/5

    Example Response (200 OK):
        {
            "id": 5,
            "title": "Buy groceries",
            "description": "Milk, eggs, bread",
            "completed": false,
            "created_at": "2026-01-20T10:30:00Z",
            "updated_at": "2026-01-20T10:30:00Z",
            "user_id": "user123"
        }

    Example Response (404 Not Found):
        {
            "detail": "Task not found"
        }
    """
    # Call service layer to get task by ID
    # Service will raise HTTPException(404) if not found
    task = get_task_by_id(db, user_id, id)

    # Return task as TaskResponse (Pydantic will convert from ORM model)
    return task


@router.put(
    "/api/{user_id}/tasks/{id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a task",
    description="Update an existing task by ID for the specified user",
    tags=["Tasks"]
)
def update_task_endpoint(
    user_id: str,
    id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db)
) -> TaskResponse:
    """
    Update an existing task.

    This endpoint updates a specific task that matches both the task ID
    and user_id. Ensures users can only update their own tasks.
    The updated_at timestamp is automatically refreshed.

    Args:
        user_id: User identifier from path parameter
        id: Task identifier from path parameter
        task_data: Task update data (title, description, completed)
        db: Database session (injected via dependency)

    Returns:
        TaskResponse: Updated task details with refreshed updated_at

    Raises:
        404 Not Found: Task does not exist or doesn't belong to user
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
            "user_id": "user123"
        }

    Example Response (404 Not Found):
        {
            "detail": "Task not found"
        }
    """
    # Call service layer to update task
    # Service will raise HTTPException(404) if not found
    task = update_task(db, user_id, id, task_data)

    # Return task as TaskResponse (Pydantic will convert from ORM model)
    return task


@router.delete(
    "/api/{user_id}/tasks/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task",
    description="Delete an existing task by ID for the specified user",
    tags=["Tasks"]
)
def delete_task_endpoint(
    user_id: str,
    id: int,
    db: Session = Depends(get_db)
) -> None:
    """
    Delete a task.

    This endpoint deletes a specific task that matches both the task ID
    and user_id. Ensures users can only delete their own tasks.
    This is a hard delete (permanent removal from database).

    Args:
        user_id: User identifier from path parameter
        id: Task identifier from path parameter
        db: Database session (injected via dependency)

    Returns:
        None (204 No Content - no response body)

    Raises:
        404 Not Found: Task does not exist or doesn't belong to user

    Example Request:
        DELETE /api/user123/tasks/5

    Example Response (204 No Content):
        (No response body)

    Example Response (404 Not Found):
        {
            "detail": "Task not found"
        }
    """
    # Call service layer to delete task
    # Service will raise HTTPException(404) if not found
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
        db: Database session (injected via dependency)

    Returns:
        TaskResponse: Updated task with toggled completion status

    Raises:
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
    # Call service layer to toggle task completion
    # Service will raise HTTPException(404) if not found
    task = toggle_task_completion(db, user_id, id)

    # Return task as TaskResponse (Pydantic will convert from ORM model)
    return task
