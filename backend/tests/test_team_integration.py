"""
Integration test for team functionality against PostgreSQL database.

This test verifies that the team tables, constraints, and relationships
work correctly in the actual PostgreSQL database (not SQLite).
"""

import pytest
from sqlmodel import Session, create_engine, select
from sqlalchemy.exc import IntegrityError

from app.config import settings
from app.models.user import User
from app.models.team import Team
from app.models.team_member import TeamMember, TeamRole
from app.models.task import Task
from app.models.task_share import TaskShare, SharePermission
from app.services.team_service import create_team, get_user_teams


@pytest.mark.skipif(
    not settings.DATABASE_URL.startswith("postgresql"),
    reason="Integration tests require PostgreSQL database"
)
class TestTeamIntegrationPostgreSQL:
    """Integration tests for team functionality with PostgreSQL."""

    def test_team_unique_constraint_enforced(self):
        """Test that team name unique constraint is enforced in PostgreSQL."""
        engine = create_engine(
            settings.DATABASE_URL.replace("postgresql://", "postgresql+psycopg://")
        )

        with Session(engine) as db:
            # Create test user
            user = User(email=f"test_unique_{id(self)}@example.com", password_hash="hashed")
            db.add(user)
            db.commit()
            db.refresh(user)

            # Create first team
            team1 = Team(name=f"UniqueTeam_{id(self)}", owner_id=user.id)
            db.add(team1)
            db.commit()

            # Try to create duplicate team name
            team2 = Team(name=f"UniqueTeam_{id(self)}", owner_id=user.id)
            db.add(team2)

            with pytest.raises(IntegrityError):
                db.commit()
            db.rollback()

            # Cleanup
            db.delete(team1)
            db.delete(user)
            db.commit()

    def test_team_member_unique_constraint_enforced(self):
        """Test that team member unique constraint is enforced in PostgreSQL."""
        engine = create_engine(
            settings.DATABASE_URL.replace("postgresql://", "postgresql+psycopg://")
        )

        with Session(engine) as db:
            # Create test user
            user = User(email=f"test_member_{id(self)}@example.com", password_hash="hashed")
            db.add(user)
            db.commit()
            db.refresh(user)

            # Create team
            team = Team(name=f"TestTeam_{id(self)}", owner_id=user.id)
            db.add(team)
            db.commit()
            db.refresh(team)

            # Create first membership
            member1 = TeamMember(team_id=team.id, user_id=user.id, role=TeamRole.OWNER)
            db.add(member1)
            db.commit()

            # Try to create duplicate membership
            member2 = TeamMember(team_id=team.id, user_id=user.id, role=TeamRole.ADMIN)
            db.add(member2)

            with pytest.raises(IntegrityError):
                db.commit()
            db.rollback()

            # Cleanup
            db.delete(member1)
            db.delete(team)
            db.delete(user)
            db.commit()

    def test_task_share_unique_constraint_enforced(self):
        """Test that task share unique constraint is enforced in PostgreSQL."""
        engine = create_engine(
            settings.DATABASE_URL.replace("postgresql://", "postgresql+psycopg://")
        )

        with Session(engine) as db:
            # Create test users
            user1 = User(email=f"test_share1_{id(self)}@example.com", password_hash="hashed")
            user2 = User(email=f"test_share2_{id(self)}@example.com", password_hash="hashed")
            db.add(user1)
            db.add(user2)
            db.commit()
            db.refresh(user1)
            db.refresh(user2)

            # Create task
            task = Task(title=f"TestTask_{id(self)}", user_id=user1.id, status="pending")
            db.add(task)
            db.commit()
            db.refresh(task)

            # Create first share
            share1 = TaskShare(
                task_id=task.id,
                shared_with_user_id=user2.id,
                shared_by_user_id=user1.id,
                permission=SharePermission.VIEW
            )
            db.add(share1)
            db.commit()

            # Try to create duplicate share
            share2 = TaskShare(
                task_id=task.id,
                shared_with_user_id=user2.id,
                shared_by_user_id=user1.id,
                permission=SharePermission.EDIT
            )
            db.add(share2)

            with pytest.raises(IntegrityError):
                db.commit()
            db.rollback()

            # Cleanup
            db.delete(share1)
            db.delete(task)
            db.delete(user1)
            db.delete(user2)
            db.commit()

    def test_team_service_integration(self):
        """Test team service functions work correctly with PostgreSQL."""
        engine = create_engine(
            settings.DATABASE_URL.replace("postgresql://", "postgresql+psycopg://")
        )

        with Session(engine) as db:
            # Create test user
            user = User(email=f"test_service_{id(self)}@example.com", password_hash="hashed")
            db.add(user)
            db.commit()
            db.refresh(user)

            # Create team using service
            team = create_team(
                db=db,
                name=f"ServiceTeam_{id(self)}",
                owner_id=user.id,
                description="Test team"
            )

            assert team.id is not None
            assert team.name == f"ServiceTeam_{id(self)}"

            # Verify owner membership was created
            statement = select(TeamMember).where(
                TeamMember.team_id == team.id,
                TeamMember.user_id == user.id
            )
            membership = db.exec(statement).first()
            assert membership is not None
            assert membership.role == TeamRole.OWNER

            # Get user teams
            teams = get_user_teams(db, user.id)
            assert len(teams) >= 1
            assert any(t["name"] == f"ServiceTeam_{id(self)}" for t in teams)

            # Cleanup
            db.delete(membership)
            db.delete(team)
            db.delete(user)
            db.commit()

    def test_cascade_delete_behavior(self):
        """Test that cascade deletes work correctly in PostgreSQL."""
        engine = create_engine(
            settings.DATABASE_URL.replace("postgresql://", "postgresql+psycopg://")
        )

        with Session(engine) as db:
            # Create test user
            user = User(email=f"test_cascade_{id(self)}@example.com", password_hash="hashed")
            db.add(user)
            db.commit()
            db.refresh(user)

            # Create team
            team = Team(name=f"CascadeTeam_{id(self)}", owner_id=user.id)
            db.add(team)
            db.commit()
            db.refresh(team)

            # Create membership
            member = TeamMember(team_id=team.id, user_id=user.id, role=TeamRole.OWNER)
            db.add(member)
            db.commit()
            member_id = member.id

            # Delete team
            db.delete(team)
            db.commit()

            # Verify membership was cascade deleted
            deleted_member = db.get(TeamMember, member_id)
            assert deleted_member is None

            # Cleanup
            db.delete(user)
            db.commit()
