"""
Middleware package for authentication and request processing.

This package contains middleware components for JWT token verification,
authentication, permission checking, and other request processing logic.
"""

from .permissions import (
    require_team_member,
    require_team_role,
    require_team_admin,
    require_team_owner,
    get_user_team_role,
    can_access_task,
    can_edit_task,
    can_delete_task,
    require_task_access,
    require_task_edit,
    require_task_delete,
    validate_role_change
)

__all__ = [
    "require_team_member",
    "require_team_role",
    "require_team_admin",
    "require_team_owner",
    "get_user_team_role",
    "can_access_task",
    "can_edit_task",
    "can_delete_task",
    "require_task_access",
    "require_task_edit",
    "require_task_delete",
    "validate_role_change"
]
