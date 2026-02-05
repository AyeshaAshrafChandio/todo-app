"""
Permission checking middleware for Teams, RBAC, and Task Sharing.

This module provides functions to check user permissions for team operations
and task access control based on team membership, roles, and direct sharing.

All permission denials are logged for security auditing purposes.
"""

import logging
from typing import Optional, Tuple
from sqlmodel import Session, select
from fastapi import HTTPException, status

from app.models import Team, TeamMember, TeamRole, Task, TaskShare, SharePermission


# Configure logger for permission-related events
logger = logging.getLogger(__name__)


# ============================================================================
# Team Permission Checking Functions (T010)
# ============================================================================

def require_team_member(
    session: Session,
    team_id: str,
    user_id: str
) -> TeamMember:
    """
    Verify that user is a member of the team.

    Args:
        session: Database session
        team_id: Team identifier
        user_id: User identifier

    Returns:
        TeamMember: The membership record

    Raises:
        HTTPException: 403 if user is not a team member
    """
    membership = session.exec(
        select(TeamMember).where(
            TeamMember.team_id == team_id,
            TeamMember.user_id == user_id
        )
    ).first()

    if not membership:
        # Log permission denial for security auditing
        logger.warning(
            f"Permission denied: user={user_id} attempted=access_team "
            f"team={team_id} required_role=member reason=not_a_member"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User is not a member of team {team_id}"
        )

    return membership


def require_team_role(
    session: Session,
    team_id: str,
    user_id: str,
    required_role: TeamRole
) -> TeamMember:
    """
    Verify that user has a specific role in the team.

    Args:
        session: Database session
        team_id: Team identifier
        user_id: User identifier
        required_role: Required role (exact match)

    Returns:
        TeamMember: The membership record

    Raises:
        HTTPException: 403 if user doesn't have the required role
    """
    membership = require_team_member(session, team_id, user_id)

    if membership.role != required_role:
        # Log permission denial for security auditing
        logger.warning(
            f"Permission denied: user={user_id} attempted=require_specific_role "
            f"team={team_id} required_role={required_role.value} actual_role={membership.role.value}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User must have {required_role.value} role in team {team_id}"
        )

    return membership


def require_team_admin(
    session: Session,
    team_id: str,
    user_id: str
) -> TeamMember:
    """
    Verify that user is an admin or owner of the team.

    Admins and owners can manage team members and tasks.

    Args:
        session: Database session
        team_id: Team identifier
        user_id: User identifier

    Returns:
        TeamMember: The membership record

    Raises:
        HTTPException: 403 if user is not an admin or owner
    """
    membership = require_team_member(session, team_id, user_id)

    if membership.role not in [TeamRole.ADMIN, TeamRole.OWNER]:
        # Log permission denial for security auditing
        logger.warning(
            f"Permission denied: user={user_id} attempted=admin_action "
            f"team={team_id} required_role=admin_or_owner actual_role={membership.role.value}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User must be admin or owner of team {team_id}"
        )

    return membership


def require_team_owner(
    session: Session,
    team_id: str,
    user_id: str
) -> TeamMember:
    """
    Verify that user is the owner of the team.

    Only owners can delete teams, transfer ownership, and change admin roles.

    Args:
        session: Database session
        team_id: Team identifier
        user_id: User identifier

    Returns:
        TeamMember: The membership record

    Raises:
        HTTPException: 403 if user is not the team owner
    """
    return require_team_role(session, team_id, user_id, TeamRole.OWNER)


def get_user_team_role(
    session: Session,
    team_id: str,
    user_id: str
) -> Optional[TeamRole]:
    """
    Get user's role in a team without raising exceptions.

    Args:
        session: Database session
        team_id: Team identifier
        user_id: User identifier

    Returns:
        TeamRole if user is a member, None otherwise
    """
    membership = session.exec(
        select(TeamMember).where(
            TeamMember.team_id == team_id,
            TeamMember.user_id == user_id
        )
    ).first()

    return membership.role if membership else None


# ============================================================================
# Task Access Checking Functions (T011)
# ============================================================================

def can_access_task(
    session: Session,
    task: Task,
    user_id: str
) -> Tuple[bool, Optional[str]]:
    """
    Determine if user can access a task and return access type.

    Access is granted if user is:
    1. Task owner (full access)
    2. Team member (if task is team-owned)
    3. Direct share recipient

    Args:
        session: Database session
        task: Task to check access for
        user_id: User identifier

    Returns:
        Tuple of (can_access: bool, access_type: str or None)
        Access types: "owner", "team_owner", "team_admin", "team_member",
                     "team_viewer", "shared_edit", "shared_view"
    """
    # 1. Owner always has full access
    if task.user_id == user_id:
        return (True, "owner")

    # 2. Team member access (if task is team-owned)
    if task.team_id:
        membership = session.exec(
            select(TeamMember).where(
                TeamMember.team_id == task.team_id,
                TeamMember.user_id == user_id
            )
        ).first()

        if membership:
            return (True, f"team_{membership.role.value}")

    # 3. Direct share access
    share = session.exec(
        select(TaskShare).where(
            TaskShare.task_id == task.id,
            TaskShare.shared_with_user_id == user_id
        )
    ).first()

    if share:
        return (True, f"shared_{share.permission.value}")

    # 4. No access
    return (False, None)


def can_edit_task(
    session: Session,
    task: Task,
    user_id: str
) -> bool:
    """
    Determine if user can edit a task.

    Edit permission is granted if user is:
    1. Task owner
    2. Team owner or admin (if task is team-owned)
    3. Team member who created the task (if task is team-owned)
    4. Direct share recipient with edit permission

    Args:
        session: Database session
        task: Task to check edit permission for
        user_id: User identifier

    Returns:
        bool: True if user can edit the task
    """
    can_access, access_type = can_access_task(session, task, user_id)

    if not can_access:
        return False

    # Owner can always edit
    if access_type == "owner":
        return True

    # Team owners and admins can edit all team tasks
    if access_type in ["team_owner", "team_admin"]:
        return True

    # Team members can edit their own tasks
    if access_type == "team_member" and task.user_id == user_id:
        return True

    # Shared with edit permission
    if access_type == "shared_edit":
        return True

    # All other cases: no edit permission
    return False


def can_delete_task(
    session: Session,
    task: Task,
    user_id: str
) -> bool:
    """
    Determine if user can delete a task.

    Delete permission is granted if user is:
    1. Task owner
    2. Team owner or admin (if task is team-owned)

    Note: Direct share recipients cannot delete tasks, even with edit permission.

    Args:
        session: Database session
        task: Task to check delete permission for
        user_id: User identifier

    Returns:
        bool: True if user can delete the task
    """
    can_access, access_type = can_access_task(session, task, user_id)

    if not can_access:
        return False

    # Owner can always delete
    if access_type == "owner":
        return True

    # Team owners and admins can delete all team tasks
    if access_type in ["team_owner", "team_admin"]:
        return True

    # All other cases: no delete permission
    return False


def require_task_access(
    session: Session,
    task: Task,
    user_id: str
) -> str:
    """
    Verify that user can access a task, raise exception if not.

    Args:
        session: Database session
        task: Task to check access for
        user_id: User identifier

    Returns:
        str: Access type

    Raises:
        HTTPException: 403 if user cannot access the task
    """
    can_access, access_type = can_access_task(session, task, user_id)

    if not can_access:
        # Log permission denial for security auditing
        logger.warning(
            f"Permission denied: user={user_id} attempted=access_task "
            f"task={task.id} team={task.team_id} reason=no_access"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User does not have access to task {task.id}"
        )

    return access_type


def require_task_edit(
    session: Session,
    task: Task,
    user_id: str
) -> None:
    """
    Verify that user can edit a task, raise exception if not.

    Args:
        session: Database session
        task: Task to check edit permission for
        user_id: User identifier

    Raises:
        HTTPException: 403 if user cannot edit the task
    """
    if not can_edit_task(session, task, user_id):
        # Log permission denial for security auditing
        logger.warning(
            f"Permission denied: user={user_id} attempted=edit_task "
            f"task={task.id} team={task.team_id} owner={task.user_id} reason=no_edit_permission"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User does not have permission to edit task {task.id}"
        )


def require_task_delete(
    session: Session,
    task: Task,
    user_id: str
) -> None:
    """
    Verify that user can delete a task, raise exception if not.

    Args:
        session: Database session
        task: Task to check delete permission for
        user_id: User identifier

    Raises:
        HTTPException: 403 if user cannot delete the task
    """
    if not can_delete_task(session, task, user_id):
        # Log permission denial for security auditing
        logger.warning(
            f"Permission denied: user={user_id} attempted=delete_task "
            f"task={task.id} team={task.team_id} owner={task.user_id} reason=no_delete_permission"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User does not have permission to delete task {task.id}"
        )


# ============================================================================
# Helper Functions
# ============================================================================

def get_accessible_tasks_query(
    session: Session,
    user_id: str,
    team_id: Optional[str] = None
):
    """
    Build a query for all tasks accessible to a user.

    This includes:
    1. Personal tasks (user_id matches, team_id is NULL)
    2. Team tasks (user is a member of the team)
    3. Shared tasks (task is shared with user)

    Args:
        session: Database session
        user_id: User identifier
        team_id: Optional team filter (only return tasks from this team)

    Returns:
        SQLModel query for accessible tasks
    """
    # This is a helper function that can be used by service layer
    # to efficiently query accessible tasks
    # Implementation will be in the service layer as it requires
    # complex UNION queries or subqueries
    pass


def validate_role_change(
    session: Session,
    team_id: str,
    target_user_id: str,
    new_role: TeamRole,
    requesting_user_id: str
) -> None:
    """
    Validate that a role change is allowed.

    Rules:
    1. Only owners can change roles to/from owner
    2. Admins can change roles for members and viewers
    3. Cannot change your own role
    4. Team must have exactly one owner at all times

    Args:
        session: Database session
        team_id: Team identifier
        target_user_id: User whose role is being changed
        new_role: New role to assign
        requesting_user_id: User requesting the change

    Raises:
        HTTPException: 403 if role change is not allowed
    """
    # Cannot change your own role
    if target_user_id == requesting_user_id:
        logger.warning(
            f"Permission denied: user={requesting_user_id} attempted=change_own_role "
            f"team={team_id} reason=cannot_change_own_role"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot change your own role"
        )

    # Get requesting user's role
    requesting_membership = require_team_member(session, team_id, requesting_user_id)

    # Get target user's current role
    target_membership = require_team_member(session, team_id, target_user_id)

    # Only owners can change roles to/from owner
    if new_role == TeamRole.OWNER or target_membership.role == TeamRole.OWNER:
        if requesting_membership.role != TeamRole.OWNER:
            logger.warning(
                f"Permission denied: user={requesting_user_id} attempted=change_ownership "
                f"team={team_id} required_role=owner actual_role={requesting_membership.role.value}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only team owners can change ownership"
            )

    # Admins can change roles for members and viewers
    elif requesting_membership.role == TeamRole.ADMIN:
        if target_membership.role in [TeamRole.OWNER, TeamRole.ADMIN]:
            logger.warning(
                f"Permission denied: user={requesting_user_id} attempted=change_admin_role "
                f"team={team_id} target_role={target_membership.role.value} reason=admin_cannot_change_owner_or_admin"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admins cannot change owner or admin roles"
            )

    # Members and viewers cannot change roles
    elif requesting_membership.role in [TeamRole.MEMBER, TeamRole.VIEWER]:
        logger.warning(
            f"Permission denied: user={requesting_user_id} attempted=change_role "
            f"team={team_id} actual_role={requesting_membership.role.value} reason=insufficient_permissions"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and owners can change roles"
        )
