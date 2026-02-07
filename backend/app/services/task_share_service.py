"""
Task Share service for database operations on TaskShare model.

This module provides service functions for sharing tasks with other users,
revoking shares, and retrieving shared task information. It handles task
sharing business logic and database interactions.

Extended to emit WebSocket events for real-time updates (Phase 7).
"""

from typing import List, Dict
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
import asyncio

from app.models.task_share import TaskShare, SharePermission
from app.models.task import Task
from app.models.user import User
from app.services.websocket_manager import websocket_manager


def share_task(
    db: Session,
    task_id: int,
    owner_id: str,
    shared_with_user_id: str,
    permission: str
) -> TaskShare:
    """
    Share a task with another user.

    Creates a TaskShare record granting the specified user access to the task.
    Only the task owner can share tasks. Users cannot share tasks with themselves.

    Args:
        db: Database session
        task_id: ID of the task to share
        owner_id: User ID of the task owner (for verification)
        shared_with_user_id: User ID to share the task with
        permission: Access level to grant ("view" or "edit")

    Returns:
        Created TaskShare object

    Raises:
        HTTPException 400: If attempting to share with self
        HTTPException 403: If user is not the task owner
        HTTPException 404: If task or target user does not exist
        HTTPException 409: If task is already shared with this user

    Example:
        ```python
        share = share_task(
            db=db,
            task_id=123,
            owner_id="owner-uuid",
            shared_with_user_id="colleague-uuid",
            permission="edit"
        )
        ```
    """
    # Prevent self-sharing
    if owner_id == shared_with_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot share task with yourself"
        )

    # Verify task exists and user is the owner
    task = db.exec(select(Task).where(Task.id == task_id)).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )

    if task.user_id != owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the task owner can share this task"
        )

    # Verify target user exists
    target_user = db.exec(select(User).where(User.id == shared_with_user_id)).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {shared_with_user_id} not found"
        )

    # Convert permission string to enum
    try:
        permission_enum = SharePermission(permission)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid permission: {permission}. Must be 'view' or 'edit'"
        )

    # Create share record
    try:
        share = TaskShare(
            task_id=task_id,
            shared_with_user_id=shared_with_user_id,
            shared_by_user_id=owner_id,
            permission=permission_enum
        )

        db.add(share)
        db.commit()
        db.refresh(share)

        # Emit WebSocket event for real-time updates (Phase 7)
        try:
            asyncio.create_task(
                websocket_manager.broadcast_task_shared(
                    task_id=task_id,
                    shared_with_user_id=shared_with_user_id,
                    shared_by_user_id=owner_id
                )
            )
        except Exception as e:
            # Log error but don't fail the operation
            import logging
            logging.getLogger(__name__).warning(f"Failed to emit task_shared event: {e}")

        return share

    except IntegrityError as e:
        db.rollback()
        # Check if it's a duplicate share (unique constraint violation)
        if "uq_task_share" in str(e).lower() or "unique" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Task {task_id} is already shared with user {shared_with_user_id}"
            )
        raise


def revoke_share(
    db: Session,
    task_id: int,
    owner_id: str,
    shared_with_user_id: str
) -> None:
    """
    Revoke task sharing access from a user.

    Removes the TaskShare record, revoking the user's access to the task.
    Only the task owner can revoke shares.

    Args:
        db: Database session
        task_id: ID of the task
        owner_id: User ID of the task owner (for verification)
        shared_with_user_id: User ID to revoke access from

    Raises:
        HTTPException 403: If user is not the task owner
        HTTPException 404: If task or share does not exist

    Example:
        ```python
        revoke_share(
            db=db,
            task_id=123,
            owner_id="owner-uuid",
            shared_with_user_id="colleague-uuid"
        )
        ```
    """
    # Verify task exists and user is the owner
    task = db.exec(select(Task).where(Task.id == task_id)).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )

    if task.user_id != owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the task owner can revoke sharing"
        )

    # Find and delete the share record
    share = db.exec(
        select(TaskShare).where(
            TaskShare.task_id == task_id,
            TaskShare.shared_with_user_id == shared_with_user_id
        )
    ).first()

    if not share:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} is not shared with user {shared_with_user_id}"
        )

    db.delete(share)
    db.commit()


def get_shared_tasks(db: Session, user_id: str) -> List[Dict]:
    """
    Get all tasks that have been shared with a user.

    Returns a list of tasks shared with the user, including the owner's email
    and the user's permission level for each task.

    Args:
        db: Database session
        user_id: User ID to get shared tasks for

    Returns:
        List of dictionaries containing task details, owner email, permission, and shared_at

    Example:
        ```python
        shared_tasks = get_shared_tasks(db=db, user_id="user-uuid")
        # Returns:
        # [
        #     {
        #         "id": 123,
        #         "title": "Review PR",
        #         "description": "Review PR #456",
        #         "completed": False,
        #         "owner_email": "owner@example.com",
        #         "permission": "edit",
        #         "shared_at": datetime(...),
        #         "created_at": datetime(...),
        #         "updated_at": datetime(...)
        #     }
        # ]
        ```
    """
    # Query for all shares where user is the recipient
    shares = db.exec(
        select(TaskShare).where(TaskShare.shared_with_user_id == user_id)
    ).all()

    result = []
    for share in shares:
        # Get the task
        task = db.exec(select(Task).where(Task.id == share.task_id)).first()
        if not task:
            continue  # Skip if task was deleted

        # Get the owner's email
        owner = db.exec(select(User).where(User.id == task.user_id)).first()
        if not owner:
            continue  # Skip if owner was deleted

        result.append({
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "completed": task.completed,
            "owner_email": owner.email,
            "permission": share.permission.value,
            "shared_at": share.shared_at,
            "created_at": task.created_at,
            "updated_at": task.updated_at
        })

    return result


def get_task_shares(db: Session, task_id: int, owner_id: str) -> List[Dict]:
    """
    Get all users with whom a task has been shared.

    Returns a list of users who have access to the task via direct sharing.
    Only the task owner can view this information.

    Args:
        db: Database session
        task_id: ID of the task
        owner_id: User ID of the task owner (for verification)

    Returns:
        List of dictionaries containing user_id, email, permission, and shared_at

    Raises:
        HTTPException 403: If user is not the task owner
        HTTPException 404: If task does not exist

    Example:
        ```python
        shares = get_task_shares(db=db, task_id=123, owner_id="owner-uuid")
        # Returns:
        # [
        #     {
        #         "user_id": "colleague-uuid",
        #         "email": "colleague@example.com",
        #         "permission": "edit",
        #         "shared_at": datetime(...)
        #     }
        # ]
        ```
    """
    # Verify task exists and user is the owner
    task = db.exec(select(Task).where(Task.id == task_id)).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )

    if task.user_id != owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the task owner can view sharing information"
        )

    # Query for all shares of this task
    shares = db.exec(
        select(TaskShare).where(TaskShare.task_id == task_id)
    ).all()

    result = []
    for share in shares:
        # Get the user's email
        user = db.exec(select(User).where(User.id == share.shared_with_user_id)).first()
        if not user:
            continue  # Skip if user was deleted

        result.append({
            "user_id": share.shared_with_user_id,
            "email": user.email,
            "permission": share.permission.value,
            "shared_at": share.shared_at
        })

    return result
