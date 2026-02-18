"""
Authorization middleware for comprehensive access control.

This module provides centralized authorization functions that combine
authentication (JWT verification) with permission checking for resources.
It serves as a unified entry point for all authorization decisions.

All authorization failures are logged for security auditing.
"""

import logging
from typing import Dict, Optional
from fastapi import Depends, HTTPException, status
from sqlmodel import Session

from app.middleware.auth import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.models.task import Task
from app.models.team import Team
from app.middleware.permissions import (
    require_team_member,
    require_team_admin,
    require_team_owner,
    can_access_task,
    can_edit_task,
    can_delete_task
)


# Configure logger for authorization events
logger = logging.getLogger(__name__)


# ============================================================================
# User Authorization Functions
# ============================================================================

def get_authenticated_user(
    current_user: Dict[str, str] = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> User:
    """
    Get authenticated user object from JWT token.

    This function verifies the JWT token and retrieves the full User object
    from the database. It ensures the user exists and is valid.

    Args:
        current_user: User info from JWT token (injected by get_current_user)
        db: Database session (injected by get_db)

    Returns:
        User: Full user object from database

    Raises:
        HTTPException: 401 if user not found in database

    Example:
        ```python
        @router.get("/api/profile")
        def get_profile(user: User = Depends(get_authenticated_user)):
            return {"email": user.email}
        ```
    """
    user_id = current_user["user_id"]

    # Retrieve user from database
    user = db.get(User, user_id)

    if not user:
        logger.error(
            f"Authorization failed: user_id={user_id} reason=user_not_found_in_database"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return user


def verify_resource_ownership(
    resource_user_id: str,
    current_user: Dict[str, str] = Depends(get_current_user)
) -> None:
    """
    Verify that the authenticated user owns the requested resource.

    This function checks that the user_id in the URL path matches the
    authenticated user's ID from the JWT token. This prevents users from
    accessing other users' resources.

    Args:
        resource_user_id: User ID from URL path parameter
        current_user: Authenticated user info from JWT token

    Raises:
        HTTPException: 403 Forbidden if user_id doesn't match

    Example:
        ```python
        @router.get("/api/{user_id}/tasks")
        def list_tasks(
            user_id: str,
            _: None = Depends(lambda user_id=user_id: verify_resource_ownership(user_id))
        ):
            # User is authorized to access this resource
            pass
        ```
    """
    if current_user["user_id"] != resource_user_id:
        logger.warning(
            f"Authorization failed: authenticated_user={current_user['user_id']} "
            f"attempted=access_resource resource_owner={resource_user_id} "
            f"reason=ownership_mismatch"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You can only access your own resources"
        )


# ============================================================================
# Task Authorization Functions
# ============================================================================

def authorize_task_access(
    task: Task,
    user: User,
    db: Session
) -> str:
    """
    Authorize user access to a task and return access type.

    This function checks if the user has permission to view the task
    through ownership, team membership, or direct sharing.

    Args:
        task: Task to check access for
        user: Authenticated user
        db: Database session

    Returns:
        str: Access type (owner, team_owner, team_admin, etc.)

    Raises:
        HTTPException: 403 if user doesn't have access

    Example:
        ```python
        task = db.get(Task, task_id)
        access_type = authorize_task_access(task, user, db)
        print(f"User has {access_type} access")
        ```
    """
    can_access, access_type = can_access_task(db, task, user.id)

    if not can_access:
        logger.warning(
            f"Authorization failed: user={user.id} attempted=access_task "
            f"task={task.id} owner={task.user_id} team={task.team_id} "
            f"reason=no_access_permission"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You don't have permission to view this task"
        )

    return access_type


def authorize_task_edit(
    task: Task,
    user: User,
    db: Session
) -> None:
    """
    Authorize user to edit a task.

    This function checks if the user has permission to modify the task
    through ownership, team admin role, or edit permission from sharing.

    Args:
        task: Task to check edit permission for
        user: Authenticated user
        db: Database session

    Raises:
        HTTPException: 403 if user doesn't have edit permission

    Example:
        ```python
        task = db.get(Task, task_id)
        authorize_task_edit(task, user, db)
        # User is authorized to edit
        ```
    """
    if not can_edit_task(db, task, user.id):
        logger.warning(
            f"Authorization failed: user={user.id} attempted=edit_task "
            f"task={task.id} owner={task.user_id} team={task.team_id} "
            f"reason=no_edit_permission"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You don't have permission to edit this task"
        )


def authorize_task_delete(
    task: Task,
    user: User,
    db: Session
) -> None:
    """
    Authorize user to delete a task.

    This function checks if the user has permission to delete the task.
    Only task owners and team admins can delete tasks.

    Args:
        task: Task to check delete permission for
        user: Authenticated user
        db: Database session

    Raises:
        HTTPException: 403 if user doesn't have delete permission

    Example:
        ```python
        task = db.get(Task, task_id)
        authorize_task_delete(task, user, db)
        # User is authorized to delete
        ```
    """
    if not can_delete_task(db, task, user.id):
        logger.warning(
            f"Authorization failed: user={user.id} attempted=delete_task "
            f"task={task.id} owner={task.user_id} team={task.team_id} "
            f"reason=no_delete_permission"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You don't have permission to delete this task"
        )


# ============================================================================
# Team Authorization Functions
# ============================================================================

def authorize_team_access(
    team_id: str,
    user: User,
    db: Session
) -> None:
    """
    Authorize user access to a team.

    This function verifies that the user is a member of the team.

    Args:
        team_id: Team identifier
        user: Authenticated user
        db: Database session

    Raises:
        HTTPException: 403 if user is not a team member

    Example:
        ```python
        authorize_team_access(team_id, user, db)
        # User is a team member
        ```
    """
    require_team_member(db, team_id, user.id)


def authorize_team_admin(
    team_id: str,
    user: User,
    db: Session
) -> None:
    """
    Authorize user as team admin or owner.

    This function verifies that the user has admin or owner role in the team.

    Args:
        team_id: Team identifier
        user: Authenticated user
        db: Database session

    Raises:
        HTTPException: 403 if user is not an admin or owner

    Example:
        ```python
        authorize_team_admin(team_id, user, db)
        # User is admin or owner
        ```
    """
    require_team_admin(db, team_id, user.id)


def authorize_team_owner(
    team_id: str,
    user: User,
    db: Session
) -> None:
    """
    Authorize user as team owner.

    This function verifies that the user is the owner of the team.

    Args:
        team_id: Team identifier
        user: Authenticated user
        db: Database session

    Raises:
        HTTPException: 403 if user is not the team owner

    Example:
        ```python
        authorize_team_owner(team_id, user, db)
        # User is team owner
        ```
    """
    require_team_owner(db, team_id, user.id)


# ============================================================================
# Dashboard Authorization Functions
# ============================================================================

def authorize_dashboard_access(
    user: User = Depends(get_authenticated_user)
) -> User:
    """
    Authorize user access to dashboard endpoints.

    This is a convenience function that ensures the user is authenticated
    and returns the full User object for dashboard operations.

    Args:
        user: Authenticated user (injected by get_authenticated_user)

    Returns:
        User: Authenticated user object

    Example:
        ```python
        @router.get("/api/dashboard/statistics")
        def get_statistics(user: User = Depends(authorize_dashboard_access)):
            # User is authorized to access dashboard
            return compute_statistics(user.id)
        ```
    """
    logger.info(f"Dashboard access: user={user.id} email={user.email}")
    return user


# ============================================================================
# Helper Functions
# ============================================================================

def log_authorization_success(
    user_id: str,
    action: str,
    resource_type: str,
    resource_id: Optional[str] = None
) -> None:
    """
    Log successful authorization for audit trail.

    Args:
        user_id: User who performed the action
        action: Action performed (e.g., "access_task", "edit_task")
        resource_type: Type of resource (e.g., "task", "team")
        resource_id: Optional resource identifier

    Example:
        ```python
        log_authorization_success(user.id, "access_task", "task", task.id)
        ```
    """
    logger.info(
        f"Authorization success: user={user_id} action={action} "
        f"resource_type={resource_type} resource_id={resource_id or 'N/A'}"
    )


def log_authorization_failure(
    user_id: str,
    action: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    reason: str = "permission_denied"
) -> None:
    """
    Log failed authorization for security audit.

    Args:
        user_id: User who attempted the action
        action: Action attempted (e.g., "access_task", "edit_task")
        resource_type: Type of resource (e.g., "task", "team")
        resource_id: Optional resource identifier
        reason: Reason for failure

    Example:
        ```python
        log_authorization_failure(user.id, "delete_task", "task", task.id, "not_owner")
        ```
    """
    logger.warning(
        f"Authorization failure: user={user_id} action={action} "
        f"resource_type={resource_type} resource_id={resource_id or 'N/A'} "
        f"reason={reason}"
    )
