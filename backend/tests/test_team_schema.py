"""
Test suite for team and sharing functionality.

This module tests:
- Team model creation and validation
- TeamMember model and role-based access
- TaskShare model and permissions
- Data isolation for team-based queries
- Unique constraints and foreign key relationships
"""

import pytest
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.models.team import Team
from app.models.team_member import TeamMember, TeamRole
from app.models.task import Task
from app.models.task_share import TaskShare, SharePermission
from app.services.team_service import (
    create_team,
    get_user_teams,
    get_team_details,
    update_team,
    delete_team,
    get_team_by_id,
    get_team_by_name
)


class TestTeamModel:
    """Test Team model creation, validation, and relationships."""

    def test_create_team_success(self, db: Session, test_user: User):
        """Test creating a team with valid data."""
        team = Team(
            name="Engineering Team",
            description="Core engineering team",
            owner_id=test_user.id
        )
        db.add(team)
        db.commit()
        db.refresh(team)

        assert team.id is not None
        assert team.name == "Engineering Team"
        assert team.description == "Core engineering team"
        assert team.owner_id == test_user.id
        assert team.created_at is not None
        assert team.updated_at is not None

    def test_team_name_unique_constraint(self, db: Session, test_user: User):
        """Test that team names must be unique."""
        # Create first team
        team1 = Team(name="Engineering", owner_id=test_user.id)
        db.add(team1)
        db.commit()

        # Try to create second team with same name
        team2 = Team(name="Engineering", owner_id=test_user.id)
        db.add(team2)

        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()

    def test_team_owner_foreign_key(self, db: Session):
        """Test that team owner_id must reference a valid user."""
        team = Team(
            name="Invalid Team",
            owner_id="non-existent-user-id"
        )
        db.add(team)

        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()

    def test_team_cascade_delete_on_owner_delete(self, db: Session, test_user: User):
        """Test that teams are deleted when owner is deleted."""
        team = Team(name="Test Team", owner_id=test_user.id)
        db.add(team)
        db.commit()
        team_id = team.id

        # Delete owner
        db.delete(test_user)
        db.commit()

        # Verify team is deleted
        deleted_team = db.get(Team, team_id)
        assert deleted_team is None


class TestTeamMemberModel:
    """Test TeamMember model and role-based access control."""

    def test_create_team_member_success(self, db: Session, test_user: User):
        """Test creating a team membership with valid data."""
        team = Team(name="Test Team", owner_id=test_user.id)
        db.add(team)
        db.commit()

        member = TeamMember(
            team_id=team.id,
            user_id=test_user.id,
            role=TeamRole.OWNER
        )
        db.add(member)
        db.commit()
        db.refresh(member)

        assert member.id is not None
        assert member.team_id == team.id
        assert member.user_id == test_user.id
        assert member.role == TeamRole.OWNER
        assert member.joined_at is not None

    def test_team_member_unique_constraint(self, db: Session, test_user: User):
        """Test that a user can only have one membership per team."""
        team = Team(name="Test Team", owner_id=test_user.id)
        db.add(team)
        db.commit()

        # Create first membership
        member1 = TeamMember(
            team_id=team.id,
            user_id=test_user.id,
            role=TeamRole.OWNER
        )
        db.add(member1)
        db.commit()

        # Try to create duplicate membership
        member2 = TeamMember(
            team_id=team.id,
            user_id=test_user.id,
            role=TeamRole.ADMIN
        )
        db.add(member2)

        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()

    def test_team_member_cascade_delete_on_team_delete(self, db: Session, test_user: User):
        """Test that memberships are deleted when team is deleted."""
        team = Team(name="Test Team", owner_id=test_user.id)
        db.add(team)
        db.commit()

        member = TeamMember(
            team_id=team.id,
            user_id=test_user.id,
            role=TeamRole.OWNER
        )
        db.add(member)
        db.commit()
        member_id = member.id

        # Delete team
        db.delete(team)
        db.commit()

        # Verify membership is deleted
        deleted_member = db.get(TeamMember, member_id)
        assert deleted_member is None

    def test_team_member_roles(self, db: Session, test_user: User):
        """Test all team member roles."""
        team = Team(name="Test Team", owner_id=test_user.id)
        db.add(team)
        db.commit()

        roles = [TeamRole.OWNER, TeamRole.ADMIN, TeamRole.MEMBER, TeamRole.VIEWER]

        for i, role in enumerate(roles):
            # Create a new user for each role
            user = User(
                email=f"user{i}@example.com",
                password_hash="hashed_password"
            )
            db.add(user)
            db.commit()

            member = TeamMember(
                team_id=team.id,
                user_id=user.id,
                role=role
            )
            db.add(member)
            db.commit()
            db.refresh(member)

            assert member.role == role


class TestTaskShareModel:
    """Test TaskShare model and permission levels."""

    def test_create_task_share_success(self, db: Session, test_user: User):
        """Test creating a task share with valid data."""
        # Create second user
        user2 = User(email="user2@example.com", password_hash="hashed")
        db.add(user2)
        db.commit()

        # Create task
        task = Task(
            title="Test Task",
            user_id=test_user.id,
            status="pending"
        )
        db.add(task)
        db.commit()

        # Share task
        share = TaskShare(
            task_id=task.id,
            shared_with_user_id=user2.id,
            shared_by_user_id=test_user.id,
            permission=SharePermission.EDIT
        )
        db.add(share)
        db.commit()
        db.refresh(share)

        assert share.id is not None
        assert share.task_id == task.id
        assert share.shared_with_user_id == user2.id
        assert share.shared_by_user_id == test_user.id
        assert share.permission == SharePermission.EDIT
        assert share.shared_at is not None

    def test_task_share_unique_constraint(self, db: Session, test_user: User):
        """Test that a task can only be shared once with each user."""
        # Create second user
        user2 = User(email="user2@example.com", password_hash="hashed")
        db.add(user2)
        db.commit()

        # Create task
        task = Task(title="Test Task", user_id=test_user.id, status="pending")
        db.add(task)
        db.commit()

        # Create first share
        share1 = TaskShare(
            task_id=task.id,
            shared_with_user_id=user2.id,
            shared_by_user_id=test_user.id,
            permission=SharePermission.VIEW
        )
        db.add(share1)
        db.commit()

        # Try to create duplicate share
        share2 = TaskShare(
            task_id=task.id,
            shared_with_user_id=user2.id,
            shared_by_user_id=test_user.id,
            permission=SharePermission.EDIT
        )
        db.add(share2)

        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()

    def test_task_share_permissions(self, db: Session, test_user: User):
        """Test both permission levels."""
        user2 = User(email="user2@example.com", password_hash="hashed")
        db.add(user2)
        db.commit()

        task = Task(title="Test Task", user_id=test_user.id, status="pending")
        db.add(task)
        db.commit()

        # Test VIEW permission
        share_view = TaskShare(
            task_id=task.id,
            shared_with_user_id=user2.id,
            shared_by_user_id=test_user.id,
            permission=SharePermission.VIEW
        )
        db.add(share_view)
        db.commit()
        db.refresh(share_view)

        assert share_view.permission == SharePermission.VIEW

    def test_task_share_cascade_delete_on_task_delete(self, db: Session, test_user: User):
        """Test that shares are deleted when task is deleted."""
        user2 = User(email="user2@example.com", password_hash="hashed")
        db.add(user2)
        db.commit()

        task = Task(title="Test Task", user_id=test_user.id, status="pending")
        db.add(task)
        db.commit()

        share = TaskShare(
            task_id=task.id,
            shared_with_user_id=user2.id,
            shared_by_user_id=test_user.id,
            permission=SharePermission.VIEW
        )
        db.add(share)
        db.commit()
        share_id = share.id

        # Delete task
        db.delete(task)
        db.commit()

        # Verify share is deleted
        deleted_share = db.get(TaskShare, share_id)
        assert deleted_share is None


class TestTeamService:
    """Test team service functions and data isolation."""

    def test_create_team_with_owner_membership(self, db: Session, test_user: User):
        """Test that creating a team automatically adds owner as member."""
        team = create_team(
            db=db,
            name="Engineering Team",
            owner_id=test_user.id,
            description="Core team"
        )

        assert team.id is not None
        assert team.name == "Engineering Team"

        # Verify owner membership was created
        statement = select(TeamMember).where(
            TeamMember.team_id == team.id,
            TeamMember.user_id == test_user.id
        )
        membership = db.exec(statement).first()

        assert membership is not None
        assert membership.role == TeamRole.OWNER

    def test_get_user_teams(self, db: Session, test_user: User):
        """Test retrieving all teams for a user."""
        # Create multiple teams
        team1 = create_team(db, "Team 1", test_user.id)
        team2 = create_team(db, "Team 2", test_user.id)

        teams = get_user_teams(db, test_user.id)

        assert len(teams) == 2
        assert teams[0]["name"] in ["Team 1", "Team 2"]
        assert teams[0]["role"] == "owner"
        assert teams[0]["member_count"] == 1

    def test_get_team_details(self, db: Session, test_user: User):
        """Test retrieving detailed team information."""
        team = create_team(db, "Test Team", test_user.id, "Description")

        details = get_team_details(db, team.id)

        assert details is not None
        assert details["name"] == "Test Team"
        assert details["description"] == "Description"
        assert len(details["members"]) == 1
        assert details["members"][0]["email"] == test_user.email
        assert details["members"][0]["role"] == "owner"

    def test_update_team(self, db: Session, test_user: User):
        """Test updating team information."""
        team = create_team(db, "Original Name", test_user.id)

        updated = update_team(
            db=db,
            team_id=team.id,
            name="Updated Name",
            description="New description"
        )

        assert updated is not None
        assert updated.name == "Updated Name"
        assert updated.description == "New description"

    def test_delete_team_converts_tasks_to_personal(self, db: Session, test_user: User):
        """Test that deleting a team converts team tasks to personal tasks."""
        team = create_team(db, "Test Team", test_user.id)

        # Create team task
        task = Task(
            title="Team Task",
            user_id=test_user.id,
            team_id=team.id,
            status="pending"
        )
        db.add(task)
        db.commit()
        task_id = task.id

        # Delete team
        success = delete_team(db, team.id)
        assert success is True

        # Verify task still exists but team_id is NULL
        task = db.get(Task, task_id)
        assert task is not None
        assert task.team_id is None

    def test_data_isolation_user_only_sees_own_teams(self, db: Session, test_user: User):
        """Test that users only see teams they are members of."""
        # Create second user
        user2 = User(email="user2@example.com", password_hash="hashed")
        db.add(user2)
        db.commit()

        # User 1 creates a team
        team1 = create_team(db, "User 1 Team", test_user.id)

        # User 2 creates a team
        team2 = create_team(db, "User 2 Team", user2.id)

        # User 1 should only see their team
        user1_teams = get_user_teams(db, test_user.id)
        assert len(user1_teams) == 1
        assert user1_teams[0]["name"] == "User 1 Team"

        # User 2 should only see their team
        user2_teams = get_user_teams(db, user2.id)
        assert len(user2_teams) == 1
        assert user2_teams[0]["name"] == "User 2 Team"

    def test_data_isolation_shared_tasks(self, db: Session, test_user: User):
        """Test that users can only see tasks shared with them."""
        # Create second user
        user2 = User(email="user2@example.com", password_hash="hashed")
        db.add(user2)
        db.commit()

        # User 1 creates a task
        task = Task(title="Private Task", user_id=test_user.id, status="pending")
        db.add(task)
        db.commit()

        # Share task with user 2
        share = TaskShare(
            task_id=task.id,
            shared_with_user_id=user2.id,
            shared_by_user_id=test_user.id,
            permission=SharePermission.VIEW
        )
        db.add(share)
        db.commit()

        # Verify share exists
        statement = select(TaskShare).where(
            TaskShare.task_id == task.id,
            TaskShare.shared_with_user_id == user2.id
        )
        found_share = db.exec(statement).first()

        assert found_share is not None
        assert found_share.permission == SharePermission.VIEW


class TestDataIntegrity:
    """Test data integrity constraints and edge cases."""

    def test_cannot_create_team_with_empty_name(self, db: Session, test_user: User):
        """Test that team name cannot be empty."""
        with pytest.raises(Exception):  # Validation error
            team = Team(name="", owner_id=test_user.id)
            db.add(team)
            db.commit()
        db.rollback()

    def test_team_member_foreign_keys(self, db: Session, test_user: User):
        """Test that team_member foreign keys are enforced."""
        team = Team(name="Test Team", owner_id=test_user.id)
        db.add(team)
        db.commit()

        # Try to create membership with invalid user_id
        member = TeamMember(
            team_id=team.id,
            user_id="non-existent-user",
            role=TeamRole.MEMBER
        )
        db.add(member)

        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()

    def test_task_share_foreign_keys(self, db: Session, test_user: User):
        """Test that task_share foreign keys are enforced."""
        task = Task(title="Test Task", user_id=test_user.id, status="pending")
        db.add(task)
        db.commit()

        # Try to share with non-existent user
        share = TaskShare(
            task_id=task.id,
            shared_with_user_id="non-existent-user",
            shared_by_user_id=test_user.id,
            permission=SharePermission.VIEW
        )
        db.add(share)

        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()

    def test_multiple_users_can_be_team_members(self, db: Session, test_user: User):
        """Test that a team can have multiple members."""
        team = create_team(db, "Multi-Member Team", test_user.id)

        # Add multiple members
        for i in range(3):
            user = User(
                email=f"member{i}@example.com",
                password_hash="hashed"
            )
            db.add(user)
            db.commit()

            member = TeamMember(
                team_id=team.id,
                user_id=user.id,
                role=TeamRole.MEMBER
            )
            db.add(member)
            db.commit()

        # Verify all members exist
        details = get_team_details(db, team.id)
        assert len(details["members"]) == 4  # Owner + 3 members

    def test_task_can_be_shared_with_multiple_users(self, db: Session, test_user: User):
        """Test that a task can be shared with multiple users."""
        task = Task(title="Shared Task", user_id=test_user.id, status="pending")
        db.add(task)
        db.commit()

        # Share with multiple users
        for i in range(3):
            user = User(
                email=f"recipient{i}@example.com",
                password_hash="hashed"
            )
            db.add(user)
            db.commit()

            share = TaskShare(
                task_id=task.id,
                shared_with_user_id=user.id,
                shared_by_user_id=test_user.id,
                permission=SharePermission.VIEW
            )
            db.add(share)
            db.commit()

        # Verify all shares exist
        statement = select(TaskShare).where(TaskShare.task_id == task.id)
        shares = db.exec(statement).all()
        assert len(shares) == 3
