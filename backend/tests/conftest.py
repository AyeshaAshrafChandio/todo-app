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
from app.middleware.auth import get_current_user
from app.models import Task, User, Team, TeamMember, TaskShare


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
    session instead of the production database, and bypasses authentication
    for testing purposes. The mock user_id is extracted from the URL path.

    Args:
        session: Test database session

    Yields:
        TestClient: FastAPI test client
    """
    def get_session_override():
        return session

    # Create a dependency that extracts user_id from path parameters
    def get_current_user_override(request: Request = None):
        """
        Mock authentication - returns a test user matching the URL path.
        Extracts user_id from the request URL path (e.g., /api/{user_id}/tasks).
        """
        # Import Request from fastapi
        from fastapi import Request

        # Create a new dependency function that accepts Request
        async def _get_user(request: Request):
            # Extract user_id from path parameters
            user_id = request.path_params.get('user_id', 'user123')
            return {
                "user_id": user_id,
                "email": f"{user_id}@example.com"
            }

        return _get_user

    # Override dependencies
    app.dependency_overrides[get_db] = get_session_override

    # Create a proper async dependency for authentication
    from fastapi import Request
    async def mock_get_current_user(request: Request):
        user_id = request.path_params.get('user_id', 'user123')
        return {
            "user_id": user_id,
            "email": f"{user_id}@example.com"
        }

    app.dependency_overrides[get_current_user] = mock_get_current_user

    # Create test client
    client = TestClient(app)
    yield client

    # Cleanup: remove dependency overrides
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


@pytest.fixture(name="db", scope="function")
def db_fixture(session: Session) -> Session:
    """
    Alias for session fixture to match common test naming conventions.

    Args:
        session: Test database session

    Returns:
        Session: SQLModel database session for testing
    """
    return session


@pytest.fixture(name="test_user", scope="function")
def test_user_fixture(db: Session) -> User:
    """
    Create a test user for testing.

    Args:
        db: Test database session

    Returns:
        User: Test user object
    """
    user = User(
        email="testuser@example.com",
        password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqJfitzXCO"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
