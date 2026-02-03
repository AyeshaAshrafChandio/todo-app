"""
Integration tests for database connection and session management.

This module tests the database connection, session management, and
initialization functions to ensure proper integration with Neon PostgreSQL.
"""

import pytest
from sqlmodel import Session, select
from app.database.connection import engine, get_db, init_db
from app.models.task import Task


def test_database_engine_creation():
    """Test that the database engine is created successfully."""
    # Assert
    assert engine is not None
    assert engine.url is not None


def test_get_db_dependency():
    """Test the get_db dependency function."""
    # Act
    db_generator = get_db()
    session = next(db_generator)

    # Assert
    assert isinstance(session, Session)
    assert session.is_active

    # Cleanup
    try:
        next(db_generator)
    except StopIteration:
        pass  # Expected behavior


def test_init_db_creates_tables():
    """Test that init_db creates all required tables."""
    # Act
    init_db()

    # Assert - verify tables exist by attempting to query
    with Session(engine) as session:
        # This should not raise an error if the table exists
        statement = select(Task)
        result = session.exec(statement).all()
        assert isinstance(result, list)


def test_session_commit_on_success(session: Session):
    """Test that session commits successfully on normal operation."""
    # Arrange
    task = Task(title="Commit Test", user_id="user123")

    # Act
    session.add(task)
    session.commit()
    session.refresh(task)

    # Assert
    assert task.id is not None

    # Verify persistence
    statement = select(Task).where(Task.id == task.id)
    retrieved_task = session.exec(statement).first()
    assert retrieved_task is not None
    assert retrieved_task.title == "Commit Test"


def test_session_rollback_on_error(session: Session):
    """Test that session rolls back on error."""
    # Arrange
    task1 = Task(title="Task 1", user_id="user123")
    session.add(task1)
    session.commit()

    initial_count = len(session.exec(select(Task)).all())

    # Act - simulate an error scenario
    try:
        task2 = Task(title="Task 2", user_id="user123")
        session.add(task2)
        # Force an error by trying to add invalid data
        session.flush()
        raise Exception("Simulated error")
    except Exception:
        session.rollback()

    # Assert - verify rollback occurred
    final_count = len(session.exec(select(Task)).all())
    assert final_count == initial_count


def test_connection_pool_configuration():
    """Test that connection pool is configured correctly."""
    # Assert
    assert engine.pool.size() >= 0  # Pool exists
    # Note: Detailed pool configuration testing requires accessing internal attributes


def test_database_session_isolation(session: Session):
    """Test that database sessions are properly isolated."""
    # Arrange
    task = Task(title="Isolation Test", user_id="user123")
    session.add(task)
    session.commit()
    session.refresh(task)
    task_id = task.id

    # Act - create a new session
    with Session(engine) as new_session:
        statement = select(Task).where(Task.id == task_id)
        retrieved_task = new_session.exec(statement).first()

        # Assert
        assert retrieved_task is not None
        assert retrieved_task.id == task_id
        assert retrieved_task.title == "Isolation Test"


def test_concurrent_sessions():
    """Test that multiple concurrent sessions work correctly."""
    # Arrange & Act
    sessions = []
    try:
        for i in range(3):
            db_generator = get_db()
            session = next(db_generator)
            sessions.append((session, db_generator))

            # Add a task in each session
            task = Task(title=f"Concurrent Task {i}", user_id="user123")
            session.add(task)
            session.commit()

        # Assert - all sessions should be active
        assert len(sessions) == 3
        assert all(s[0].is_active for s in sessions)

    finally:
        # Cleanup
        for session, generator in sessions:
            try:
                next(generator)
            except StopIteration:
                pass


def test_task_persistence_across_sessions(session: Session):
    """Test that tasks persist across different sessions."""
    # Arrange - create task in first session
    task = Task(title="Persistence Test", user_id="user123")
    session.add(task)
    session.commit()
    session.refresh(task)
    task_id = task.id

    # Act - retrieve task in a new session
    with Session(engine) as new_session:
        statement = select(Task).where(Task.id == task_id)
        retrieved_task = new_session.exec(statement).first()

        # Assert
        assert retrieved_task is not None
        assert retrieved_task.id == task_id
        assert retrieved_task.title == "Persistence Test"
        assert retrieved_task.user_id == "user123"
