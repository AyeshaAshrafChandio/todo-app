"""
Test unauthorized access scenarios and security controls.

This module tests security controls including authentication, authorization,
token validation, and protection against common attack vectors.

Test Scenarios:
- Unauthorized access attempts (401)
- Insufficient permissions (403)
- Invalid JWT tokens
- Expired JWT tokens
- SQL injection attempts
- Cross-user data access attempts
- Missing authentication headers
"""

import pytest
import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException
from sqlmodel import Session

from app.models.user import User
from app.models.task import Task
from app.models.team import Team
from app.models.team_member import TeamMember, TeamRole
from app.middleware.auth import get_current_user
from app.middleware.permissions import (
    require_team_member,
    require_team_admin,
    require_team_owner,
    can_access_task,
    can_edit_task,
    can_delete_task
)
from app.services.task_service import (
    create_task,
    get_task_by_id,
    update_task,
    delete_task
)
from app.services.team_service import create_team
from app.schemas.task import TaskCreate, TaskUpdate
from app.config import settings


@pytest.fixture
def test_user(session: Session) -> User:
    """Create a test user."""
    user = User(
        email="test@example.com",
        password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqJfitzXCO"
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def other_user(session: Session) -> User:
    """Create another test user."""
    user = User(
        email="other@example.com",
        password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqJfitzXCO"
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


# ============================================================================
# JWT Token Validation Tests
# ============================================================================

def test_invalid_jwt_token():
    """Test that invalid JWT tokens are rejected."""
    from fastapi.security import HTTPAuthorizationCredentials

    # Create invalid token
    invalid_token = "invalid.jwt.token"
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials=invalid_token
    )

    # Should raise 401 Unauthorized
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(credentials)

    assert exc_info.value.status_code == 401
    assert "Invalid token" in exc_info.value.detail


def test_expired_jwt_token(test_user: User):
    """Test that expired JWT tokens are rejected."""
    from fastapi.security import HTTPAuthorizationCredentials

    # Create expired token (expired 1 hour ago)
    expired_payload = {
        "userId": test_user.id,
        "email": test_user.email,
        "iat": datetime.utcnow() - timedelta(hours=2),
        "exp": datetime.utcnow() - timedelta(hours=1)
    }

    expired_token = jwt.encode(
        expired_payload,
        settings.BETTER_AUTH_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )

    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials=expired_token
    )

    # Should raise 401 Unauthorized
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(credentials)

    assert exc_info.value.status_code == 401
    assert "expired" in exc_info.value.detail.lower()


def test_jwt_token_missing_required_claims():
    """Test that JWT tokens missing required claims are rejected."""
    from fastapi.security import HTTPAuthorizationCredentials

    # Create token without required claims
    incomplete_payload = {
        "userId": "user123",
        # Missing email, iat, exp
    }

    incomplete_token = jwt.encode(
        incomplete_payload,
        settings.BETTER_AUTH_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )

    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials=incomplete_token
    )

    # Should raise 401 Unauthorized
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(credentials)

    assert exc_info.value.status_code == 401


def test_jwt_token_wrong_signature():
    """Test that JWT tokens with wrong signature are rejected."""
    from fastapi.security import HTTPAuthorizationCredentials

    # Create token with wrong secret
    payload = {
        "userId": "user123",
        "email": "test@example.com",
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=1)
    }

    wrong_token = jwt.encode(
        payload,
        "wrong-secret-key",
        algorithm=settings.JWT_ALGORITHM
    )

    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials=wrong_token
    )

    # Should raise 401 Unauthorized
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(credentials)

    assert exc_info.value.status_code == 401
    assert "Invalid token" in exc_info.value.detail


# ============================================================================
# Task Access Control Tests
# ============================================================================

def test_unauthorized_task_access(
    session: Session,
    test_user: User,
    other_user: User
):
    """Test that users cannot access tasks they don't own."""
    # Test user creates a task
    task = create_task(
        session,
        test_user.id,
        TaskCreate(title="Private Task", description="Secret")
    )

    # Other user tries to access the task
    with pytest.raises(HTTPException) as exc_info:
        get_task_by_id(session, other_user.id, task.id)

    # Should return 404 (not 403) to prevent information leakage
    assert exc_info.value.status_code == 404
    assert "not found" in exc_info.value.detail.lower()


def test_unauthorized_task_update(
    session: Session,
    test_user: User,
    other_user: User
):
    """Test that users cannot update tasks they don't own."""
    # Test user creates a task
    task = create_task(
        session,
        test_user.id,
        TaskCreate(title="Original Title", description="Original")
    )

    # Other user tries to update the task
    with pytest.raises(HTTPException) as exc_info:
        update_task(
            session,
            other_user.id,
            task.id,
            TaskUpdate(title="Hacked!", description="Unauthorized")
        )

    assert exc_info.value.status_code == 404

    # Verify task was not modified
    task_after = session.get(Task, task.id)
    assert task_after.title == "Original Title"
    assert task_after.description == "Original"


def test_unauthorized_task_deletion(
    session: Session,
    test_user: User,
    other_user: User
):
    """Test that users cannot delete tasks they don't own."""
    # Test user creates a task
    task = create_task(
        session,
        test_user.id,
        TaskCreate(title="Important Task", description="Do not delete")
    )

    # Other user tries to delete the task
    with pytest.raises(HTTPException) as exc_info:
        delete_task(session, other_user.id, task.id)

    assert exc_info.value.status_code == 404

    # Verify task still exists
    task_after = session.get(Task, task.id)
    assert task_after is not None
    assert task_after.title == "Important Task"


# ============================================================================
# Team Access Control Tests
# ============================================================================

def test_non_member_cannot_access_team(
    session: Session,
    test_user: User,
    other_user: User
):
    """Test that non-members cannot access team resources."""
    # Test user creates a team
    team = create_team(session, "Private Team", test_user.id, "Private")

    # Other user tries to access the team
    with pytest.raises(HTTPException) as exc_info:
        require_team_member(session, team.id, other_user.id)

    assert exc_info.value.status_code == 403
    assert "not a member" in exc_info.value.detail.lower()


def test_member_cannot_perform_admin_actions(
    session: Session,
    test_user: User,
    other_user: User
):
    """Test that regular members cannot perform admin actions."""
    # Test user creates a team
    team = create_team(session, "Team", test_user.id, "Description")

    # Add other user as regular member
    member = TeamMember(
        team_id=team.id,
        user_id=other_user.id,
        role=TeamRole.MEMBER
    )
    session.add(member)
    session.commit()

    # Other user tries to perform admin action
    with pytest.raises(HTTPException) as exc_info:
        require_team_admin(session, team.id, other_user.id)

    assert exc_info.value.status_code == 403
    assert "admin" in exc_info.value.detail.lower()


def test_admin_cannot_perform_owner_actions(
    session: Session,
    test_user: User,
    other_user: User
):
    """Test that admins cannot perform owner-only actions."""
    # Test user creates a team
    team = create_team(session, "Team", test_user.id, "Description")

    # Add other user as admin
    admin = TeamMember(
        team_id=team.id,
        user_id=other_user.id,
        role=TeamRole.ADMIN
    )
    session.add(admin)
    session.commit()

    # Admin tries to perform owner action
    with pytest.raises(HTTPException) as exc_info:
        require_team_owner(session, team.id, other_user.id)

    assert exc_info.value.status_code == 403
    assert "owner" in exc_info.value.detail.lower()


def test_viewer_cannot_create_team_tasks(
    session: Session,
    test_user: User,
    other_user: User
):
    """Test that viewers cannot create team tasks."""
    # Test user creates a team
    team = create_team(session, "Team", test_user.id, "Description")

    # Add other user as viewer
    viewer = TeamMember(
        team_id=team.id,
        user_id=other_user.id,
        role=TeamRole.VIEWER
    )
    session.add(viewer)
    session.commit()

    # Viewer tries to create a team task
    with pytest.raises(HTTPException) as exc_info:
        create_task(
            session,
            other_user.id,
            TaskCreate(title="Team Task", description="Test", team_id=team.id)
        )

    assert exc_info.value.status_code == 403
    assert "viewer" in exc_info.value.detail.lower()


# ============================================================================
# Permission Check Tests
# ============================================================================

def test_can_access_task_permissions(
    session: Session,
    test_user: User,
    other_user: User
):
    """Test can_access_task permission checking."""
    # Test user creates a task
    task = create_task(
        session,
        test_user.id,
        TaskCreate(title="Task", description="Test")
    )

    # Owner can access
    can_access, access_type = can_access_task(session, task, test_user.id)
    assert can_access is True
    assert access_type == "owner"

    # Other user cannot access
    can_access, access_type = can_access_task(session, task, other_user.id)
    assert can_access is False
    assert access_type is None


def test_can_edit_task_permissions(
    session: Session,
    test_user: User,
    other_user: User
):
    """Test can_edit_task permission checking."""
    # Test user creates a task
    task = create_task(
        session,
        test_user.id,
        TaskCreate(title="Task", description="Test")
    )

    # Owner can edit
    assert can_edit_task(session, task, test_user.id) is True

    # Other user cannot edit
    assert can_edit_task(session, task, other_user.id) is False


def test_can_delete_task_permissions(
    session: Session,
    test_user: User,
    other_user: User
):
    """Test can_delete_task permission checking."""
    # Test user creates a task
    task = create_task(
        session,
        test_user.id,
        TaskCreate(title="Task", description="Test")
    )

    # Owner can delete
    assert can_delete_task(session, task, test_user.id) is True

    # Other user cannot delete
    assert can_delete_task(session, task, other_user.id) is False


# ============================================================================
# SQL Injection Protection Tests
# ============================================================================

def test_sql_injection_in_task_title(session: Session, test_user: User):
    """Test that SQL injection attempts in task title are handled safely."""
    # Attempt SQL injection in title
    malicious_title = "'; DROP TABLE tasks; --"

    # Should create task safely without executing SQL
    task = create_task(
        session,
        test_user.id,
        TaskCreate(title=malicious_title, description="Test")
    )

    # Task should be created with the malicious string as literal text
    assert task.title == malicious_title

    # Verify tasks table still exists
    tasks = session.query(Task).all()
    assert len(tasks) >= 1


def test_sql_injection_in_task_description(session: Session, test_user: User):
    """Test that SQL injection attempts in task description are handled safely."""
    # Attempt SQL injection in description
    malicious_desc = "Test'; DELETE FROM tasks WHERE '1'='1"

    # Should create task safely
    task = create_task(
        session,
        test_user.id,
        TaskCreate(title="Test", description=malicious_desc)
    )

    # Description should be stored as literal text
    assert task.description == malicious_desc

    # Verify no tasks were deleted
    tasks = session.query(Task).all()
    assert len(tasks) >= 1


# ============================================================================
# Cross-User Access Tests
# ============================================================================

def test_cannot_access_task_with_wrong_user_id(
    session: Session,
    test_user: User,
    other_user: User
):
    """Test that providing wrong user_id in query doesn't bypass security."""
    # Test user creates a task
    task = create_task(
        session,
        test_user.id,
        TaskCreate(title="Private", description="Secret")
    )

    # Other user tries to access using their own user_id
    with pytest.raises(HTTPException) as exc_info:
        get_task_by_id(session, other_user.id, task.id)

    assert exc_info.value.status_code == 404


def test_cannot_modify_task_by_changing_user_id(
    session: Session,
    test_user: User,
    other_user: User
):
    """Test that modifying user_id in request doesn't bypass security."""
    # Test user creates a task
    task = create_task(
        session,
        test_user.id,
        TaskCreate(title="Original", description="Original")
    )

    # Other user tries to update by providing test_user's ID
    # (This should still fail because authentication is separate)
    with pytest.raises(HTTPException) as exc_info:
        update_task(
            session,
            other_user.id,  # Authenticated user
            task.id,
            TaskUpdate(title="Hacked", description="Hacked")
        )

    assert exc_info.value.status_code == 404

    # Verify task unchanged
    task_after = session.get(Task, task.id)
    assert task_after.title == "Original"


# ============================================================================
# Information Leakage Prevention Tests
# ============================================================================

def test_404_instead_of_403_for_unauthorized_access(
    session: Session,
    test_user: User,
    other_user: User
):
    """Test that 404 is returned instead of 403 to prevent information leakage."""
    # Test user creates a task
    task = create_task(
        session,
        test_user.id,
        TaskCreate(title="Secret", description="Confidential")
    )

    # Other user tries to access
    with pytest.raises(HTTPException) as exc_info:
        get_task_by_id(session, other_user.id, task.id)

    # Should return 404, not 403
    # This prevents attackers from knowing if a task exists
    assert exc_info.value.status_code == 404
    assert "not found" in exc_info.value.detail.lower()
    assert "forbidden" not in exc_info.value.detail.lower()


def test_nonexistent_task_returns_404(
    session: Session,
    test_user: User
):
    """Test that accessing non-existent task returns 404."""
    # Try to access task that doesn't exist
    with pytest.raises(HTTPException) as exc_info:
        get_task_by_id(session, test_user.id, 99999)

    assert exc_info.value.status_code == 404
    assert "not found" in exc_info.value.detail.lower()


# ============================================================================
# Edge Case Security Tests
# ============================================================================

def test_empty_user_id_rejected(session: Session):
    """Test that empty user_id is rejected."""
    with pytest.raises(Exception):
        create_task(
            session,
            "",  # Empty user_id
            TaskCreate(title="Test", description="Test")
        )


def test_null_user_id_rejected(session: Session):
    """Test that null user_id is rejected."""
    with pytest.raises(Exception):
        create_task(
            session,
            None,  # Null user_id
            TaskCreate(title="Test", description="Test")
        )


def test_malformed_task_id_handled_safely(
    session: Session,
    test_user: User
):
    """Test that malformed task IDs are handled safely."""
    # Try to access task with invalid ID type
    with pytest.raises((HTTPException, ValueError, TypeError)):
        get_task_by_id(session, test_user.id, "invalid-id")


def test_negative_task_id_handled_safely(
    session: Session,
    test_user: User
):
    """Test that negative task IDs are handled safely."""
    with pytest.raises(HTTPException) as exc_info:
        get_task_by_id(session, test_user.id, -1)

    assert exc_info.value.status_code == 404
