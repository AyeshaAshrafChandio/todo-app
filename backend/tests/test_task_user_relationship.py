"""
Unit tests for Task model with User foreign key relationship.

Tests cover:
- Task creation with user_id (owned tasks)
- Task creation without user_id (legacy tasks)
- Foreign key constraint validation
- CASCADE delete behavior
- Querying tasks by user_id
"""

import pytest
from datetime import datetime
from sqlmodel import Session, select
from app.models.task import Task
from app.models.user import User
from app.database.connection import engine


@pytest.fixture
def db_session():
    """Create a fresh database session for each test."""
    from sqlmodel import SQLModel
    from sqlalchemy import event

    # Enable foreign key constraints for SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    # Create all tables
    SQLModel.metadata.create_all(engine)

    # Create session
    session = Session(engine)

    yield session

    # Cleanup
    session.close()

    # Drop all tables after test
    SQLModel.metadata.drop_all(engine)


@pytest.fixture
def test_user(db_session):
    """Create a test user for foreign key tests."""
    user = User(
        email="testuser@example.com",
        password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqJfitzXCO"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


class TestTaskUserRelationship:
    """Test suite for Task-User foreign key relationship."""

    def test_create_task_with_user_id(self, db_session, test_user):
        """Test creating a task with valid user_id."""
        # Arrange
        task = Task(
            title="Task with owner",
            description="This task belongs to a user",
            user_id=test_user.id
        )

        # Act
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)

        # Assert
        assert task.id is not None
        assert task.user_id == test_user.id
        assert task.title == "Task with owner"
        assert task.completed is False

    def test_create_task_without_user_id(self, db_session):
        """Test creating a legacy task without user_id (nullable)."""
        # Arrange
        task = Task(
            title="Legacy task",
            description="This task has no owner"
        )

        # Act
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)

        # Assert
        assert task.id is not None
        assert task.user_id is None
        assert task.title == "Legacy task"

    def test_foreign_key_constraint_invalid_user(self, db_session):
        """Test that foreign key constraint rejects invalid user_id."""
        # Arrange
        task = Task(
            title="Task with invalid user",
            user_id="00000000-0000-0000-0000-000000000000"  # Non-existent user
        )

        # Act & Assert
        db_session.add(task)
        with pytest.raises(Exception):  # IntegrityError
            db_session.commit()

    def test_cascade_delete_user_deletes_tasks(self, db_session, test_user):
        """Test that deleting a user cascades to delete their tasks."""
        # Arrange
        task1 = Task(title="Task 1", user_id=test_user.id)
        task2 = Task(title="Task 2", user_id=test_user.id)
        db_session.add(task1)
        db_session.add(task2)
        db_session.commit()

        # Verify tasks exist
        tasks_before = db_session.exec(
            select(Task).where(Task.user_id == test_user.id)
        ).all()
        assert len(tasks_before) == 2

        # Act - Delete user
        db_session.delete(test_user)
        db_session.commit()

        # Assert - Tasks should be deleted
        tasks_after = db_session.exec(
            select(Task).where(Task.user_id == test_user.id)
        ).all()
        assert len(tasks_after) == 0

    def test_query_tasks_by_user_id(self, db_session, test_user):
        """Test querying tasks filtered by user_id."""
        # Arrange
        user2 = User(
            email="user2@example.com",
            password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqJfitzXCO"
        )
        db_session.add(user2)
        db_session.commit()
        db_session.refresh(user2)

        # Create tasks for different users
        task1 = Task(title="User 1 Task 1", user_id=test_user.id)
        task2 = Task(title="User 1 Task 2", user_id=test_user.id)
        task3 = Task(title="User 2 Task 1", user_id=user2.id)
        task4 = Task(title="Legacy Task")  # No user_id

        db_session.add_all([task1, task2, task3, task4])
        db_session.commit()

        # Act - Query tasks for test_user
        user1_tasks = db_session.exec(
            select(Task).where(Task.user_id == test_user.id)
        ).all()

        # Assert
        assert len(user1_tasks) == 2
        assert all(t.user_id == test_user.id for t in user1_tasks)

    def test_query_legacy_tasks_without_user(self, db_session, test_user):
        """Test querying legacy tasks with NULL user_id."""
        # Arrange
        task1 = Task(title="Owned Task", user_id=test_user.id)
        task2 = Task(title="Legacy Task 1")
        task3 = Task(title="Legacy Task 2")

        db_session.add_all([task1, task2, task3])
        db_session.commit()

        # Act - Query tasks without user_id
        legacy_tasks = db_session.exec(
            select(Task).where(Task.user_id == None)
        ).all()

        # Assert
        assert len(legacy_tasks) == 2
        assert all(t.user_id is None for t in legacy_tasks)

    def test_user_id_field_properties(self, db_session, test_user):
        """Test user_id field properties (nullable, indexed, max length)."""
        # Arrange & Act
        task = Task(
            title="Test task",
            user_id=test_user.id
        )
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)

        # Assert
        assert task.user_id is not None
        assert len(task.user_id) <= 36  # Max length constraint
        assert isinstance(task.user_id, str)

    def test_multiple_tasks_same_user(self, db_session, test_user):
        """Test that one user can have multiple tasks."""
        # Arrange
        tasks = [
            Task(title=f"Task {i}", user_id=test_user.id)
            for i in range(10)
        ]

        # Act
        for task in tasks:
            db_session.add(task)
        db_session.commit()

        # Assert
        user_tasks = db_session.exec(
            select(Task).where(Task.user_id == test_user.id)
        ).all()
        assert len(user_tasks) == 10
        assert all(t.user_id == test_user.id for t in user_tasks)

    def test_task_user_id_can_be_updated(self, db_session, test_user):
        """Test that task ownership can be transferred to another user."""
        # Arrange
        user2 = User(
            email="user2@example.com",
            password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqJfitzXCO"
        )
        db_session.add(user2)
        db_session.commit()
        db_session.refresh(user2)

        task = Task(title="Transfer task", user_id=test_user.id)
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)

        # Act - Transfer ownership
        task.user_id = user2.id
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)

        # Assert
        assert task.user_id == user2.id

        # Verify task is now in user2's tasks
        user2_tasks = db_session.exec(
            select(Task).where(Task.user_id == user2.id)
        ).all()
        assert len(user2_tasks) == 1
        assert user2_tasks[0].id == task.id

    def test_task_user_id_can_be_set_to_null(self, db_session, test_user):
        """Test that task can be converted to legacy task (user_id = NULL)."""
        # Arrange
        task = Task(title="Owned task", user_id=test_user.id)
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)

        # Act - Remove ownership
        task.user_id = None
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)

        # Assert
        assert task.user_id is None

        # Verify task is now a legacy task
        legacy_tasks = db_session.exec(
            select(Task).where(Task.user_id == None)
        ).all()
        assert any(t.id == task.id for t in legacy_tasks)

    def test_task_repr_includes_user_id(self, db_session, test_user):
        """Test that Task string representation includes user_id."""
        # Arrange
        task = Task(title="Test task", user_id=test_user.id)
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)

        # Act
        repr_str = repr(task)

        # Assert
        assert "Task(" in repr_str
        assert task.title in repr_str
        assert test_user.id in repr_str
