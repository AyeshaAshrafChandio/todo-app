"""
Service layer for Task business logic.

This module contains the business logic for task operations, separated from
the API route handlers. All functions accept a database session and return
domain objects (Task instances) or raise HTTPException for errors.

Extended to support team-based tasks with role-based access control.
"""

from typing import List, Optional
from sqlmodel import Session, select, or_
from fastapi import HTTPException, status
from app.models.task import Task
from app.models.team_member import TeamMember, TeamRole
from app.models.task_share import TaskShare
from app.schemas.task import TaskCreate, TaskUpdate
from app.middleware.permissions import (
    require_team_member,
    can_access_task,
    can_edit_task,
    can_delete_task
)


def create_task(db: Session, user_id: str, task_data: TaskCreate) -> Task:
    """
    Create a new task for a user (personal or team-owned).

    This function handles the business logic for task creation:
    - Validates input data (handled by Pydantic TaskCreate schema)
    - If team_id provided, validates team membership and permissions
    - Creates Task instance with user_id and optional team_id
    - Sets completed=False (default in model)
    - Auto-generates timestamps (default in model)
    - Persists to database

    Args:
        db: Database session for persistence
        user_id: User identifier (task creator)
        task_data: Validated task creation data (title, description, team_id)

    Returns:
        Task: Created task instance with auto-generated id and timestamps

    Raises:
        HTTPException: 403 if user is not a team member or has viewer role
        HTTPException: 404 if team does not exist
        HTTPException: 500 if database error occurs

    Example:
        ```python
        # Personal task
        task_data = TaskCreate(title="Buy groceries", description="Milk, eggs")
        task = create_task(db, "user123", task_data)

        # Team task
        task_data = TaskCreate(title="Sprint planning", team_id="team456")
        task = create_task(db, "user123", task_data)
        ```
    """
    try:
        # If team_id provided, validate team membership and permissions
        if task_data.team_id:
            # Verify user is a team member
            membership = require_team_member(db, task_data.team_id, user_id)

            # Viewers cannot create tasks
            if membership.role == TeamRole.VIEWER:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Viewers cannot create team tasks"
                )

        # Create Task instance from schema data
        task = Task(
            title=task_data.title,
            description=task_data.description,
            user_id=user_id,
            team_id=task_data.team_id,
            # completed defaults to False in model
            # created_at and updated_at auto-generated in model
        )

        # Add to session and commit to database
        db.add(task)
        db.commit()

        # Refresh to get auto-generated values (id, timestamps)
        db.refresh(task)

        return task

    except HTTPException:
        # Re-raise HTTP exceptions (403, 404)
        raise
    except Exception as e:
        # Rollback on error
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error occurred while creating task: {str(e)}"
        )


def get_tasks_by_user(db: Session, user_id: str, team_id: Optional[str] = None) -> List[Task]:
    """
    Retrieve all tasks accessible to a specific user.

    This function returns a union of:
    1. Personal tasks (user_id matches, team_id is NULL)
    2. Team tasks (user is a member of the team)
    3. Shared tasks (task is shared with user)

    Args:
        db: Database session for querying
        user_id: User identifier to filter tasks
        team_id: Optional team filter (only return tasks from this team)

    Returns:
        List[Task]: List of task instances accessible to user (can be empty)

    Example:
        ```python
        # Get all accessible tasks
        tasks = get_tasks_by_user(db, "user123")

        # Get tasks for specific team
        tasks = get_tasks_by_user(db, "user123", team_id="team456")
        ```
    """
    # If team_id filter is provided, return only tasks from that team
    if team_id:
        # Verify user is a team member
        require_team_member(db, team_id, user_id)

        # Return all tasks for this team
        statement = select(Task).where(Task.team_id == team_id)
        tasks = db.exec(statement).all()
        return tasks

    # Otherwise, return union of personal, team, and shared tasks

    # 1. Get personal tasks (user_id matches, team_id is NULL)
    personal_tasks = db.exec(
        select(Task).where(
            Task.user_id == user_id,
            Task.team_id == None
        )
    ).all()

    # 2. Get team tasks (user is a member of teams)
    # First get all team IDs user is a member of
    team_memberships = db.exec(
        select(TeamMember.team_id).where(TeamMember.user_id == user_id)
    ).all()

    team_tasks = []
    if team_memberships:
        team_tasks = db.exec(
            select(Task).where(Task.team_id.in_(team_memberships))
        ).all()

    # 3. Get shared tasks (task is shared with user)
    shared_task_ids = db.exec(
        select(TaskShare.task_id).where(TaskShare.shared_with_user_id == user_id)
    ).all()

    shared_tasks = []
    if shared_task_ids:
        shared_tasks = db.exec(
            select(Task).where(Task.id.in_(shared_task_ids))
        ).all()

    # Combine all tasks and remove duplicates (using set of IDs)
    all_tasks = personal_tasks + team_tasks + shared_tasks
    seen_ids = set()
    unique_tasks = []
    for task in all_tasks:
        if task.id not in seen_ids:
            seen_ids.add(task.id)
            unique_tasks.append(task)

    return unique_tasks


def get_task_by_id(db: Session, user_id: str, task_id: int) -> Task:
    """
    Retrieve a single task by ID with team access permission checking.

    This function queries for a specific task and verifies the user has access
    through one of: task ownership, team membership, or direct sharing.

    Args:
        db: Database session for querying
        user_id: User identifier requesting access
        task_id: Task identifier to retrieve

    Returns:
        Task: Task instance if found and accessible

    Raises:
        HTTPException: 404 if task not found
        HTTPException: 403 if user doesn't have access to task

    Example:
        ```python
        task = get_task_by_id(db, "user123", 5)
        print(task.title)
        ```
    """
    # Query for task by ID
    statement = select(Task).where(Task.id == task_id)
    task = db.exec(statement).first()

    # Raise 404 if task not found
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Check if user has access to this task
    can_access, access_type = can_access_task(db, task, user_id)

    if not can_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this task"
        )

    return task


def update_task(db: Session, user_id: str, task_id: int, task_data: TaskUpdate) -> Task:
    """
    Update an existing task with team role permission enforcement.

    This function handles the business logic for task updates:
    - Queries for task by ID
    - Checks edit permissions based on team roles:
      * Task owner: can edit
      * Team owner/admin: can edit all team tasks
      * Team member: can edit own tasks only
      * Shared with edit permission: can edit
    - Updates provided fields (title, description, completed)
    - Auto-refreshes updated_at timestamp (handled by SQLModel onupdate)
    - Persists changes to database

    Args:
        db: Database session for persistence
        user_id: User identifier requesting update
        task_id: Task identifier to update
        task_data: Validated task update data (title, description, completed)

    Returns:
        Task: Updated task instance with refreshed updated_at timestamp

    Raises:
        HTTPException: 404 if task not found
        HTTPException: 403 if user doesn't have edit permission
        HTTPException: 500 if database error occurs

    Example:
        ```python
        task_data = TaskUpdate(title="Buy groceries", description="Updated list", completed=True)
        task = update_task(db, "user123", 5, task_data)
        print(task.updated_at)  # Refreshed timestamp
        ```
    """
    try:
        # Query for task by ID
        statement = select(Task).where(Task.id == task_id)
        task = db.exec(statement).first()

        # Raise 404 if task not found
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        # Check if user has edit permission
        if not can_edit_task(db, task, user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to edit this task"
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
        # Re-raise HTTP exceptions (404, 403)
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
    Delete a task with team role permission enforcement.

    This function handles the business logic for task deletion:
    - Queries for task by ID
    - Checks delete permissions based on team roles:
      * Task owner: can delete
      * Team owner/admin: can delete all team tasks
      * Others: cannot delete (including shared users)
    - Performs hard delete (removes from database)
    - Commits changes to database

    Args:
        db: Database session for persistence
        user_id: User identifier requesting deletion
        task_id: Task identifier to delete

    Returns:
        None

    Raises:
        HTTPException: 404 if task not found
        HTTPException: 403 if user doesn't have delete permission
        HTTPException: 500 if database error occurs

    Example:
        ```python
        delete_task(db, "user123", 5)
        # Task is permanently removed from database
        ```
    """
    try:
        # Query for task by ID
        statement = select(Task).where(Task.id == task_id)
        task = db.exec(statement).first()

        # Raise 404 if task not found
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        # Check if user has delete permission
        if not can_delete_task(db, task, user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to delete this task"
            )

        # Delete task from database (hard delete)
        db.delete(task)
        db.commit()

    except HTTPException:
        # Re-raise HTTP exceptions (404, 403)
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
