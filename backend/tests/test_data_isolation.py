"""
Test data isolation between users and teams.

This module tests that users can only access their own data and data
explicitly shared with them. It verifies that data isolation is enforced
at the database and service layer level.

Test Scenarios:
- User A cannot see User B's tasks
- User A cannot access User B's teams
- User A cannot modify User B's data
- Shared tasks are visible to both users
- Team members can see team tasks
- Non-team members cannot see team tasks
"""

import pytest
from sqlmodel import Session, select
from fastapi import HTTPException

from app.models.user import User
from app.models.task import Task
from app.models.team import Team
from app.models.team_member import TeamMember, TeamRole
from app.models.task_share import TaskShare, SharePermission
from app.services.task_service import (
    create_task,
    get_tasks_by_user,
    get_task_by_id,
    update_task,
    delete_task
)
from app.services.team_service import (
    create_team,
    get_user_teams,
    get_team_details
)
from app.schemas.task import TaskCreate, TaskUpdate


@pytest.fixture
def user_a(session: Session) -> User:
    """Create test user A."""
    user = User(
        email="user_a@example.com",
        password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqJfitzXCO"
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def user_b(session: Session) -> User:
    """Create test user B."""
    user = User(
        email="user_b@example.com",
        password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqJfitzXCO"
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def user_c(session: Session) -> User:
    """Create test user C."""
    user = User(
        email="user_c@example.com",
        password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqJfitzXCO"
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


# ============================================================================
# Task Data Isolation Tests
# ============================================================================

def test_user_cannot_see_other_users_tasks(
    session: Session,
    user_a: User,
    user_b: User
):
    """Test that User A cannot see User B's tasks."""
    # User A creates a task
    task_a = create_task(
        session,
        user_a.id,
        TaskCreate(title="User A's Task", description="Private task")
    )

    # User B creates a task
    task_b = create_task(
        session,
        user_b.id,
        TaskCreate(title="User B's Task", description="Private task")
    )

    # User A queries their tasks
    user_a_tasks = get_tasks_by_user(session, user_a.id)

    # User A should only see their own task
    assert len(user_a_tasks) == 1
    assert user_a_tasks[0].id == task_a.id
    assert user_a_tasks[0].title == "User A's Task"

    # User B queries their tasks
    user_b_tasks = get_tasks_by_user(session, user_b.id)

    # User B should only see their own task
    assert len(user_b_tasks) == 1
    assert user_b_tasks[0].id == task_b.id
    assert user_b_tasks[0].title == "User B's Task"


def test_user_cannot_access_other_users_task_by_id(
    session: Session,
    user_a: User,
    user_b: User
):
    """Test that User A cannot access User B's task by ID."""
    # User B creates a task
    task_b = create_task(
        session,
        user_b.id,
        TaskCreate(title="User B's Task", description="Private task")
    )

    # User A tries to access User B's task by ID
    with pytest.raises(HTTPException) as exc_info:
        get_task_by_id(session, user_a.id, task_b.id)

    # Should return 404 (not 403) to prevent information leakage
    assert exc_info.value.status_code == 404
    assert "not found" in exc_info.value.detail.lower()


def test_user_cannot_modify_other_users_task(
    session: Session,
    user_a: User,
    user_b: User
):
    """Test that User A cannot modify User B's task."""
    # User B creates a task
    task_b = create_task(
        session,
        user_b.id,
        TaskCreate(title="User B's Task", description="Private task")
    )

    # User A tries to update User B's task
    with pytest.raises(HTTPException) as exc_info:
        update_task(
            session,
            user_a.id,
            task_b.id,
            TaskUpdate(title="Hacked!", description="Unauthorized change")
        )

    # Should return 404 (not 403) to prevent information leakage
    assert exc_info.value.status_code == 404

    # Verify task was not modified
    task_b_after = session.get(Task, task_b.id)
    assert task_b_after.title == "User B's Task"
    assert task_b_after.description == "Private task"


def test_user_cannot_delete_other_users_task(
    session: Session,
    user_a: User,
    user_b: User
):
    """Test that User A cannot delete User B's task."""
    # User B creates a task
    task_b = create_task(
        session,
        user_b.id,
        TaskCreate(title="User B's Task", description="Private task")
    )

    # User A tries to delete User B's task
    with pytest.raises(HTTPException) as exc_info:
        delete_task(session, user_a.id, task_b.id)

    # Should return 404 (not 403) to prevent information leakage
    assert exc_info.value.status_code == 404

    # Verify task still exists
    task_b_after = session.get(Task, task_b.id)
    assert task_b_after is not None
    assert task_b_after.title == "User B's Task"


# ============================================================================
# Task Sharing Tests
# ============================================================================

def test_shared_tasks_visible_to_both_users(
    session: Session,
    user_a: User,
    user_b: User
):
    """Test that shared tasks are visible to both users."""
    # User A creates a task
    task_a = create_task(
        session,
        user_a.id,
        TaskCreate(title="Shared Task", description="Shared with User B")
    )

    # User A shares task with User B (view permission)
    share = TaskShare(
        task_id=task_a.id,
        shared_with_user_id=user_b.id,
        shared_by_user_id=user_a.id,
        permission=SharePermission.VIEW
    )
    session.add(share)
    session.commit()

    # User A can see the task
    user_a_tasks = get_tasks_by_user(session, user_a.id)
    assert len(user_a_tasks) == 1
    assert user_a_tasks[0].id == task_a.id

    # User B can also see the shared task
    user_b_tasks = get_tasks_by_user(session, user_b.id)
    assert len(user_b_tasks) == 1
    assert user_b_tasks[0].id == task_a.id

    # User B can access the task by ID
    task_for_b = get_task_by_id(session, user_b.id, task_a.id)
    assert task_for_b.id == task_a.id
    assert task_for_b.title == "Shared Task"


def test_shared_task_edit_permission(
    session: Session,
    user_a: User,
    user_b: User
):
    """Test that shared tasks with edit permission can be modified."""
    # User A creates a task
    task_a = create_task(
        session,
        user_a.id,
        TaskCreate(title="Editable Task", description="Shared with edit")
    )

    # User A shares task with User B (edit permission)
    share = TaskShare(
        task_id=task_a.id,
        shared_with_user_id=user_b.id,
        shared_by_user_id=user_a.id,
        permission=SharePermission.EDIT
    )
    session.add(share)
    session.commit()

    # User B can edit the task
    updated_task = update_task(
        session,
        user_b.id,
        task_a.id,
        TaskUpdate(title="Updated by User B", description="Modified")
    )

    assert updated_task.title == "Updated by User B"
    assert updated_task.description == "Modified"


def test_shared_task_view_only_cannot_edit(
    session: Session,
    user_a: User,
    user_b: User
):
    """Test that shared tasks with view-only permission cannot be edited."""
    # User A creates a task
    task_a = create_task(
        session,
        user_a.id,
        TaskCreate(title="View Only Task", description="Cannot edit")
    )

    # User A shares task with User B (view permission only)
    share = TaskShare(
        task_id=task_a.id,
        shared_with_user_id=user_b.id,
        shared_by_user_id=user_a.id,
        permission=SharePermission.VIEW
    )
    session.add(share)
    session.commit()

    # User B tries to edit the task
    with pytest.raises(HTTPException) as exc_info:
        update_task(
            session,
            user_b.id,
            task_a.id,
            TaskUpdate(title="Hacked!", description="Unauthorized")
        )

    # Should return 404 (not 403) to prevent information leakage
    assert exc_info.value.status_code == 404

    # Verify task was not modified
    task_after = session.get(Task, task_a.id)
    assert task_after.title == "View Only Task"


def test_shared_user_cannot_delete_task(
    session: Session,
    user_a: User,
    user_b: User
):
    """Test that shared users cannot delete tasks even with edit permission."""
    # User A creates a task
    task_a = create_task(
        session,
        user_a.id,
        TaskCreate(title="Shared Task", description="Cannot delete")
    )

    # User A shares task with User B (edit permission)
    share = TaskShare(
        task_id=task_a.id,
        shared_with_user_id=user_b.id,
        shared_by_user_id=user_a.id,
        permission=SharePermission.EDIT
    )
    session.add(share)
    session.commit()

    # User B tries to delete the task
    with pytest.raises(HTTPException) as exc_info:
        delete_task(session, user_b.id, task_a.id)

    # Should return 404 (not 403)
    assert exc_info.value.status_code == 404

    # Verify task still exists
    task_after = session.get(Task, task_a.id)
    assert task_after is not None


# ============================================================================
# Team Data Isolation Tests
# ============================================================================

def test_user_cannot_see_other_users_teams(
    session: Session,
    user_a: User,
    user_b: User
):
    """Test that User A cannot see User B's teams."""
    # User A creates a team
    team_a = create_team(session, "Team A", user_a.id, "User A's team")

    # User B creates a team
    team_b = create_team(session, "Team B", user_b.id, "User B's team")

    # User A queries their teams
    user_a_teams = get_user_teams(session, user_a.id)

    # User A should only see their own team
    assert len(user_a_teams) == 1
    assert user_a_teams[0]["id"] == team_a.id
    assert user_a_teams[0]["name"] == "Team A"

    # User B queries their teams
    user_b_teams = get_user_teams(session, user_b.id)

    # User B should only see their own team
    assert len(user_b_teams) == 1
    assert user_b_teams[0]["id"] == team_b.id
    assert user_b_teams[0]["name"] == "Team B"


def test_team_members_can_see_team_tasks(
    session: Session,
    user_a: User,
    user_b: User,
    user_c: User
):
    """Test that team members can see team tasks."""
    # User A creates a team
    team = create_team(session, "Engineering", user_a.id, "Engineering team")

    # Add User B as team member
    member_b = TeamMember(
        team_id=team.id,
        user_id=user_b.id,
        role=TeamRole.MEMBER
    )
    session.add(member_b)
    session.commit()

    # User A creates a team task
    team_task = create_task(
        session,
        user_a.id,
        TaskCreate(title="Team Task", description="For the team", team_id=team.id)
    )

    # User A can see the team task
    user_a_tasks = get_tasks_by_user(session, user_a.id)
    assert len(user_a_tasks) == 1
    assert user_a_tasks[0].id == team_task.id

    # User B (team member) can also see the team task
    user_b_tasks = get_tasks_by_user(session, user_b.id)
    assert len(user_b_tasks) == 1
    assert user_b_tasks[0].id == team_task.id

    # User C (not a team member) cannot see the team task
    user_c_tasks = get_tasks_by_user(session, user_c.id)
    assert len(user_c_tasks) == 0


def test_non_team_members_cannot_access_team_tasks(
    session: Session,
    user_a: User,
    user_b: User
):
    """Test that non-team members cannot access team tasks."""
    # User A creates a team
    team = create_team(session, "Private Team", user_a.id, "Private")

    # User A creates a team task
    team_task = create_task(
        session,
        user_a.id,
        TaskCreate(title="Team Task", description="Private", team_id=team.id)
    )

    # User B (not a team member) tries to access the task
    with pytest.raises(HTTPException) as exc_info:
        get_task_by_id(session, user_b.id, team_task.id)

    # Should return 404 (not 403)
    assert exc_info.value.status_code == 404


def test_team_filter_enforces_membership(
    session: Session,
    user_a: User,
    user_b: User
):
    """Test that team filter enforces team membership."""
    # User A creates a team
    team = create_team(session, "Team A", user_a.id, "User A's team")

    # User A creates a team task
    create_task(
        session,
        user_a.id,
        TaskCreate(title="Team Task", description="For team", team_id=team.id)
    )

    # User B tries to query tasks for User A's team
    with pytest.raises(HTTPException) as exc_info:
        get_tasks_by_user(session, user_b.id, team_id=team.id)

    # Should return 403 (user is not a team member)
    assert exc_info.value.status_code == 403
    assert "not a member" in exc_info.value.detail.lower()


# ============================================================================
# Complex Isolation Scenarios
# ============================================================================

def test_multiple_users_with_mixed_access(
    session: Session,
    user_a: User,
    user_b: User,
    user_c: User
):
    """Test complex scenario with multiple users and mixed access."""
    # User A creates personal task
    task_a_personal = create_task(
        session,
        user_a.id,
        TaskCreate(title="A Personal", description="Private")
    )

    # User B creates personal task
    task_b_personal = create_task(
        session,
        user_b.id,
        TaskCreate(title="B Personal", description="Private")
    )

    # User A creates a team
    team = create_team(session, "Shared Team", user_a.id, "Shared")

    # Add User B to team
    member_b = TeamMember(
        team_id=team.id,
        user_id=user_b.id,
        role=TeamRole.MEMBER
    )
    session.add(member_b)
    session.commit()

    # User A creates team task
    task_team = create_task(
        session,
        user_a.id,
        TaskCreate(title="Team Task", description="Shared", team_id=team.id)
    )

    # User A shares personal task with User C
    share = TaskShare(
        task_id=task_a_personal.id,
        shared_with_user_id=user_c.id,
        shared_by_user_id=user_a.id,
        permission=SharePermission.VIEW
    )
    session.add(share)
    session.commit()

    # Verify User A sees: personal + team = 2 tasks
    user_a_tasks = get_tasks_by_user(session, user_a.id)
    assert len(user_a_tasks) == 2
    task_ids_a = {t.id for t in user_a_tasks}
    assert task_a_personal.id in task_ids_a
    assert task_team.id in task_ids_a

    # Verify User B sees: personal + team = 2 tasks
    user_b_tasks = get_tasks_by_user(session, user_b.id)
    assert len(user_b_tasks) == 2
    task_ids_b = {t.id for t in user_b_tasks}
    assert task_b_personal.id in task_ids_b
    assert task_team.id in task_ids_b

    # Verify User C sees: shared task only = 1 task
    user_c_tasks = get_tasks_by_user(session, user_c.id)
    assert len(user_c_tasks) == 1
    assert user_c_tasks[0].id == task_a_personal.id


def test_data_isolation_after_team_removal(
    session: Session,
    user_a: User,
    user_b: User
):
    """Test that data isolation is maintained after removing user from team."""
    # User A creates a team
    team = create_team(session, "Temp Team", user_a.id, "Temporary")

    # Add User B to team
    member_b = TeamMember(
        team_id=team.id,
        user_id=user_b.id,
        role=TeamRole.MEMBER
    )
    session.add(member_b)
    session.commit()

    # User A creates team task
    team_task = create_task(
        session,
        user_a.id,
        TaskCreate(title="Team Task", description="Shared", team_id=team.id)
    )

    # User B can see the team task
    user_b_tasks_before = get_tasks_by_user(session, user_b.id)
    assert len(user_b_tasks_before) == 1

    # Remove User B from team
    session.delete(member_b)
    session.commit()

    # User B can no longer see the team task
    user_b_tasks_after = get_tasks_by_user(session, user_b.id)
    assert len(user_b_tasks_after) == 0

    # User B cannot access the task by ID
    with pytest.raises(HTTPException) as exc_info:
        get_task_by_id(session, user_b.id, team_task.id)

    assert exc_info.value.status_code == 404
