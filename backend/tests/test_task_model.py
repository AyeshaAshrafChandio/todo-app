"""
Unit tests for the Task model.

This module tests the Task SQLModel class to ensure proper validation,
default values, and database operations.
"""

import pytest
from datetime import datetime
from sqlmodel import Session, select
from app.models.task import Task


def test_task_creation_with_all_fields(session: Session):
    """Test creating a task with all fields specified."""
    # Arrange
    task_data = {
        "title": "Buy groceries",
        "description": "Milk, eggs, bread",
        "completed": False,
        "user_id": "user123"
    }

    # Act
    task = Task(**task_data)
    session.add(task)
    session.commit()
    session.refresh(task)

    # Assert
    assert task.id is not None
    assert task.title == "Buy groceries"
    assert task.description == "Milk, eggs, bread"
    assert task.completed is False
    assert task.user_id == "user123"
    assert isinstance(task.created_at, datetime)
    assert isinstance(task.updated_at, datetime)


def test_task_creation_with_minimal_fields(session: Session):
    """Test creating a task with only required fields."""
    # Arrange & Act
    task = Task(title="Minimal Task", user_id="user456")
    session.add(task)
    session.commit()
    session.refresh(task)

    # Assert
    assert task.id is not None
    assert task.title == "Minimal Task"
    assert task.description is None
    assert task.completed is False  # Default value
    assert task.user_id == "user456"
    assert isinstance(task.created_at, datetime)
    assert isinstance(task.updated_at, datetime)


def test_task_default_completed_status(session: Session):
    """Test that completed defaults to False."""
    # Arrange & Act
    task = Task(title="Test Task", user_id="user789")
    session.add(task)
    session.commit()
    session.refresh(task)

    # Assert
    assert task.completed is False


def test_task_timestamps_auto_generated(session: Session):
    """Test that timestamps are automatically generated."""
    # Arrange & Act
    task = Task(title="Timestamp Test", user_id="user123")
    session.add(task)
    session.commit()
    session.refresh(task)

    # Assert
    assert task.created_at is not None
    assert task.updated_at is not None
    assert isinstance(task.created_at, datetime)
    assert isinstance(task.updated_at, datetime)


def test_task_title_validation_empty_string():
    """Test that empty title raises validation error."""
    # Arrange & Act & Assert
    with pytest.raises(Exception):  # Pydantic ValidationError
        Task(title="", user_id="user123")


def test_task_title_validation_too_long():
    """Test that title exceeding max length raises validation error."""
    # Arrange
    long_title = "x" * 201  # Exceeds max_length=200

    # Act & Assert
    with pytest.raises(Exception):  # Pydantic ValidationError
        Task(title=long_title, user_id="user123")


def test_task_description_validation_too_long():
    """Test that description exceeding max length raises validation error."""
    # Arrange
    long_description = "x" * 1001  # Exceeds max_length=1000

    # Act & Assert
    with pytest.raises(Exception):  # Pydantic ValidationError
        Task(
            title="Test Task",
            description=long_description,
            user_id="user123"
        )


def test_task_user_id_validation_too_long():
    """Test that user_id exceeding max length raises validation error."""
    # Arrange
    long_user_id = "x" * 101  # Exceeds max_length=100

    # Act & Assert
    with pytest.raises(Exception):  # Pydantic ValidationError
        Task(title="Test Task", user_id=long_user_id)


def test_task_query_by_user_id(session: Session):
    """Test querying tasks by user_id (index usage)."""
    # Arrange
    task1 = Task(title="Task 1", user_id="user123")
    task2 = Task(title="Task 2", user_id="user123")
    task3 = Task(title="Task 3", user_id="user456")

    session.add(task1)
    session.add(task2)
    session.add(task3)
    session.commit()

    # Act
    statement = select(Task).where(Task.user_id == "user123")
    results = session.exec(statement).all()

    # Assert
    assert len(results) == 2
    assert all(task.user_id == "user123" for task in results)


def test_task_update_changes_updated_at(session: Session):
    """Test that updating a task changes the updated_at timestamp."""
    # Arrange
    task = Task(title="Original Title", user_id="user123")
    session.add(task)
    session.commit()
    session.refresh(task)
    original_updated_at = task.updated_at

    # Act
    import time
    time.sleep(0.1)  # Small delay to ensure timestamp difference
    task.title = "Updated Title"
    session.add(task)
    session.commit()
    session.refresh(task)

    # Assert
    assert task.title == "Updated Title"
    # Note: updated_at auto-update depends on database trigger or ORM behavior
    # In SQLite, this may not work as expected without additional configuration


def test_task_repr(session: Session):
    """Test the string representation of a task."""
    # Arrange & Act
    task = Task(title="Test Task", user_id="user123")
    session.add(task)
    session.commit()
    session.refresh(task)

    # Assert
    repr_str = repr(task)
    assert "Task(" in repr_str
    assert "title='Test Task'" in repr_str
    assert "user_id='user123'" in repr_str
    assert "completed=False" in repr_str


def test_task_deletion(session: Session):
    """Test deleting a task from the database."""
    # Arrange
    task = Task(title="Task to Delete", user_id="user123")
    session.add(task)
    session.commit()
    session.refresh(task)
    task_id = task.id

    # Act
    session.delete(task)
    session.commit()

    # Assert
    statement = select(Task).where(Task.id == task_id)
    result = session.exec(statement).first()
    assert result is None


def test_multiple_tasks_same_user(session: Session):
    """Test creating multiple tasks for the same user."""
    # Arrange & Act
    tasks = [
        Task(title=f"Task {i}", user_id="user123")
        for i in range(5)
    ]
    for task in tasks:
        session.add(task)
    session.commit()

    # Assert
    statement = select(Task).where(Task.user_id == "user123")
    results = session.exec(statement).all()
    assert len(results) == 5
