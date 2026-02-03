"""
Service layer for Task business logic.

This module contains the business logic for task operations, separated from
the API route handlers. All functions accept a database session and return
domain objects (Task instances) or raise HTTPException for errors.
"""

from typing import List, Optional
from sqlmodel import Session, select
from fastapi import HTTPException, status
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate


def create_task(db: Session, user_id: str, task_data: TaskCreate) -> Task:
    """
    Create a new task for a user.

    This function handles the business logic for task creation:
    - Validates input data (handled by Pydantic TaskCreate schema)
    - Creates Task instance with user_id from path parameter
    - Sets completed=False (default in model)
    - Auto-generates timestamps (default in model)
    - Persists to database

    Args:
        db: Database session for persistence
        user_id: User identifier from path parameter
        task_data: Validated task creation data (title, description)

    Returns:
        Task: Created task instance with auto-generated id and timestamps

    Raises:
        HTTPException: 500 if database error occurs

    Example:
        ```python
        task_data = TaskCreate(title="Buy groceries", description="Milk, eggs")
        task = create_task(db, "user123", task_data)
        print(task.id)  # Auto-generated ID
        ```
    """
    try:
        # Create Task instance from schema data
        task = Task(
            title=task_data.title,
            description=task_data.description,
            user_id=user_id,
            # completed defaults to False in model
            # created_at and updated_at auto-generated in model
        )

        # Add to session and commit to database
        db.add(task)
        db.commit()

        # Refresh to get auto-generated values (id, timestamps)
        db.refresh(task)

        return task

    except Exception as e:
        # Rollback on error
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error occurred while creating task: {str(e)}"
        )


def get_tasks_by_user(db: Session, user_id: str) -> List[Task]:
    """
    Retrieve all tasks for a specific user.

    This function queries all tasks belonging to the specified user_id.
    Returns an empty list if no tasks exist (not an error condition).

    Args:
        db: Database session for querying
        user_id: User identifier to filter tasks

    Returns:
        List[Task]: List of task instances (can be empty)

    Example:
        ```python
        tasks = get_tasks_by_user(db, "user123")
        print(f"Found {len(tasks)} tasks")
        ```
    """
    # Query all tasks for this user_id
    statement = select(Task).where(Task.user_id == user_id)
    tasks = db.exec(statement).all()

    return tasks


def get_task_by_id(db: Session, user_id: str, task_id: int) -> Task:
    """
    Retrieve a single task by ID and user_id.

    This function queries for a specific task that matches both the task ID
    and user_id. This ensures users can only access their own tasks.

    Args:
        db: Database session for querying
        user_id: User identifier to filter tasks
        task_id: Task identifier to retrieve

    Returns:
        Task: Task instance if found

    Raises:
        HTTPException: 404 if task not found or doesn't belong to user

    Example:
        ```python
        task = get_task_by_id(db, "user123", 5)
        print(task.title)
        ```
    """
    # Query for task matching both id and user_id
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id
    )
    task = db.exec(statement).first()

    # Raise 404 if task not found
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return task


def update_task(db: Session, user_id: str, task_id: int, task_data: TaskUpdate) -> Task:
    """
    Update an existing task for a user.

    This function handles the business logic for task updates:
    - Queries for task matching both task_id and user_id
    - Raises 404 if task not found or doesn't belong to user
    - Updates provided fields (title, description, completed)
    - Auto-refreshes updated_at timestamp (handled by SQLModel onupdate)
    - Persists changes to database

    Args:
        db: Database session for persistence
        user_id: User identifier from path parameter
        task_id: Task identifier to update
        task_data: Validated task update data (title, description, completed)

    Returns:
        Task: Updated task instance with refreshed updated_at timestamp

    Raises:
        HTTPException: 404 if task not found or doesn't belong to user
        HTTPException: 500 if database error occurs

    Example:
        ```python
        task_data = TaskUpdate(title="Buy groceries", description="Updated list", completed=True)
        task = update_task(db, "user123", 5, task_data)
        print(task.updated_at)  # Refreshed timestamp
        ```
    """
    try:
        # Query for task matching both id and user_id
        statement = select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id
        )
        task = db.exec(statement).first()

        # Raise 404 if task not found
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        # Update provided fields
        task.title = task_data.title
        task.description = task_data.description
        if task_data.completed is not None:
            task.completed = task_data.completed

        # Commit changes to database
        # updated_at will be auto-refreshed by SQLModel onupdate
        db.add(task)
        db.commit()

        # Refresh to get updated timestamp
        db.refresh(task)

        return task

    except HTTPException:
        # Re-raise HTTP exceptions (404)
        raise
    except Exception as e:
        # Rollback on error
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error occurred while updating task: {str(e)}"
        )


def delete_task(db: Session, user_id: str, task_id: int) -> None:
    """
    Delete a task for a user.

    This function handles the business logic for task deletion:
    - Queries for task matching both task_id and user_id
    - Raises 404 if task not found or doesn't belong to user
    - Performs hard delete (removes from database)
    - Commits changes to database

    Args:
        db: Database session for persistence
        user_id: User identifier from path parameter
        task_id: Task identifier to delete

    Returns:
        None

    Raises:
        HTTPException: 404 if task not found or doesn't belong to user
        HTTPException: 500 if database error occurs

    Example:
        ```python
        delete_task(db, "user123", 5)
        # Task is permanently removed from database
        ```
    """
    try:
        # Query for task matching both id and user_id
        statement = select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id
        )
        task = db.exec(statement).first()

        # Raise 404 if task not found
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        # Delete task from database (hard delete)
        db.delete(task)
        db.commit()

    except HTTPException:
        # Re-raise HTTP exceptions (404)
        raise
    except Exception as e:
        # Rollback on error
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error occurred while deleting task: {str(e)}"
        )


def toggle_task_completion(db: Session, user_id: str, task_id: int) -> Task:
    """
    Toggle the completion status of a task.

    This function handles the business logic for toggling task completion:
    - Queries for task matching both task_id and user_id
    - Raises 404 if task not found or doesn't belong to user
    - Toggles completed field (False → True, True → False)
    - Auto-refreshes updated_at timestamp (handled by SQLModel onupdate)
    - Persists changes to database

    Args:
        db: Database session for persistence
        user_id: User identifier from path parameter
        task_id: Task identifier to toggle

    Returns:
        Task: Updated task instance with toggled completion status

    Raises:
        HTTPException: 404 if task not found or doesn't belong to user
        HTTPException: 500 if database error occurs

    Example:
        ```python
        # Toggle from False to True
        task = toggle_task_completion(db, "user123", 5)
        print(task.completed)  # True

        # Toggle again from True to False
        task = toggle_task_completion(db, "user123", 5)
        print(task.completed)  # False
        ```
    """
    try:
        # Query for task matching both id and user_id
        statement = select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id
        )
        task = db.exec(statement).first()

        # Raise 404 if task not found
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        # Toggle completed field (boolean negation)
        task.completed = not task.completed

        # Commit changes to database
        # updated_at will be auto-refreshed by SQLModel onupdate
        db.add(task)
        db.commit()

        # Refresh to get updated timestamp
        db.refresh(task)

        return task

    except HTTPException:
        # Re-raise HTTP exceptions (404)
        raise
    except Exception as e:
        # Rollback on error
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error occurred while toggling task completion: {str(e)}"
        )
