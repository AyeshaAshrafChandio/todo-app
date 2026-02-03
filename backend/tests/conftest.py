"""
Pytest configuration and fixtures for testing.

This module provides shared fixtures and configuration for all tests.
"""

import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.main import app
from app.database.connection import get_db
from app.models import Task


# Create in-memory SQLite database for testing
@pytest.fixture(name="session", scope="function")
def session_fixture() -> Generator[Session, None, None]:
    """
    Create a fresh database session for each test.

    This fixture creates an in-memory SQLite database for testing,
    ensuring test isolation and fast execution.

    Yields:
        Session: SQLModel database session for testing
    """
    # Create in-memory SQLite engine for testing
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Create all tables
    SQLModel.metadata.create_all(engine)

    # Create session
    with Session(engine) as session:
        yield session

    # Cleanup: drop all tables after test
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="client", scope="function")
def client_fixture(session: Session) -> Generator[TestClient, None, None]:
    """
    Create a FastAPI test client with database session override.

    This fixture provides a test client that uses the test database
    session instead of the production database.

    Args:
        session: Test database session

    Yields:
        TestClient: FastAPI test client
    """
    def get_session_override():
        return session

    # Override the get_db dependency
    app.dependency_overrides[get_db] = get_session_override

    # Create test client
    client = TestClient(app)
    yield client

    # Cleanup: remove dependency override
    app.dependency_overrides.clear()


@pytest.fixture(name="sample_task", scope="function")
def sample_task_fixture() -> dict:
    """
    Provide sample task data for testing.

    Returns:
        dict: Sample task data
    """
    return {
        "title": "Test Task",
        "description": "This is a test task",
        "user_id": "test_user_123"
    }


@pytest.fixture(name="sample_tasks", scope="function")
def sample_tasks_fixture() -> list[dict]:
    """
    Provide multiple sample tasks for testing.

    Returns:
        list[dict]: List of sample task data
    """
    return [
        {
            "title": "Task 1",
            "description": "First test task",
            "user_id": "test_user_123"
        },
        {
            "title": "Task 2",
            "description": "Second test task",
            "user_id": "test_user_123"
        },
        {
            "title": "Task 3",
            "description": None,
            "user_id": "test_user_456"
        }
    ]
