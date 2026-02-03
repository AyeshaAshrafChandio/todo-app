"""
Integration tests for User Story 1: Create and Retrieve Tasks.

These tests verify the acceptance criteria for User Story 1:
- POST /api/{user_id}/tasks - Create new task
- GET /api/{user_id}/tasks - List all tasks for user
- GET /api/{user_id}/tasks/{id} - Get single task by ID

Test scenarios:
1. Create task returns 201 with auto-generated id and timestamps
2. List tasks returns 200 with array of all tasks for user
3. Get single task returns 200 with complete task details or 404 if not found
4. POST with empty title returns 422 validation error
5. GET for non-existent user returns 200 with empty array
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from app.main import app
from app.database.connection import get_db
from app.models.task import Task


# Create in-memory SQLite database for testing
@pytest.fixture(name="session")
def session_fixture():
    """
    Create a fresh database session for each test.

    Uses in-memory SQLite database to avoid affecting production data.
    """
    # Create in-memory SQLite engine
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


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """
    Create FastAPI test client with overridden database dependency.

    This ensures tests use the in-memory test database instead of
    the production database.
    """
    def get_session_override():
        return session

    # Override the get_db dependency
    app.dependency_overrides[get_db] = get_session_override

    # Create test client
    client = TestClient(app)
    yield client

    # Clear dependency overrides after test
    app.dependency_overrides.clear()


class TestCreateTask:
    """Tests for POST /api/{user_id}/tasks endpoint."""

    def test_create_task_success(self, client: TestClient):
        """
        Test creating a new task returns 201 with auto-generated id and timestamps.

        Acceptance Scenario 1:
        Given no existing tasks for user_id "user123"
        When I POST a new task with title "Buy groceries"
        Then the API returns 201 status with the created task including
        auto-generated id and timestamps
        """
        # Arrange
        user_id = "user123"
        task_data = {
            "title": "Buy groceries",
            "description": "Milk, eggs, bread"
        }

        # Act
        response = client.post(f"/api/{user_id}/tasks", json=task_data)

        # Assert
        assert response.status_code == 201

        data = response.json()
        assert data["id"] is not None  # Auto-generated ID
        assert data["title"] == "Buy groceries"
        assert data["description"] == "Milk, eggs, bread"
        assert data["completed"] is False  # Default value
        assert data["user_id"] == user_id
        assert data["created_at"] is not None  # Auto-generated timestamp
        assert data["updated_at"] is not None  # Auto-generated timestamp

    def test_create_task_without_description(self, client: TestClient):
        """Test creating a task without description (optional field)."""
        # Arrange
        user_id = "user456"
        task_data = {
            "title": "Walk the dog"
        }

        # Act
        response = client.post(f"/api/{user_id}/tasks", json=task_data)

        # Assert
        assert response.status_code == 201

        data = response.json()
        assert data["title"] == "Walk the dog"
        assert data["description"] is None  # Optional field
        assert data["completed"] is False

    def test_create_task_empty_title_returns_422(self, client: TestClient):
        """
        Test creating a task with empty title returns 422 validation error.

        Edge Case:
        What happens when a client tries to create a task with an empty title?
        Expected: 422 validation error
        """
        # Arrange
        user_id = "user123"
        task_data = {
            "title": "",  # Empty title
            "description": "This should fail"
        }

        # Act
        response = client.post(f"/api/{user_id}/tasks", json=task_data)

        # Assert
        assert response.status_code == 422

        data = response.json()
        assert "detail" in data
        # Pydantic validation error format
        assert isinstance(data["detail"], list)

    def test_create_task_missing_title_returns_422(self, client: TestClient):
        """Test creating a task without title returns 422 validation error."""
        # Arrange
        user_id = "user123"
        task_data = {
            "description": "Missing title"
        }

        # Act
        response = client.post(f"/api/{user_id}/tasks", json=task_data)

        # Assert
        assert response.status_code == 422

        data = response.json()
        assert "detail" in data


class TestListTasks:
    """Tests for GET /api/{user_id}/tasks endpoint."""

    def test_list_tasks_returns_all_user_tasks(self, client: TestClient, session: Session):
        """
        Test listing tasks returns 200 with array of all tasks for user.

        Acceptance Scenario 2:
        Given three tasks exist for user_id "user123"
        When I GET /api/user123/tasks
        Then the API returns 200 status with an array of all three tasks
        """
        # Arrange - Create three tasks for user123
        user_id = "user123"
        tasks = [
            Task(title="Task 1", description="First task", user_id=user_id),
            Task(title="Task 2", description="Second task", user_id=user_id),
            Task(title="Task 3", description="Third task", user_id=user_id),
        ]
        for task in tasks:
            session.add(task)
        session.commit()

        # Act
        response = client.get(f"/api/{user_id}/tasks")

        # Assert
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3

        # Verify all tasks are returned
        titles = [task["title"] for task in data]
        assert "Task 1" in titles
        assert "Task 2" in titles
        assert "Task 3" in titles

    def test_list_tasks_empty_array_for_nonexistent_user(self, client: TestClient):
        """
        Test listing tasks for non-existent user returns 200 with empty array.

        Edge Case:
        What happens when a client requests tasks for a user_id that has no tasks?
        Expected: 200 OK with empty array
        """
        # Arrange
        user_id = "nonexistent_user"

        # Act
        response = client.get(f"/api/{user_id}/tasks")

        # Assert
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0  # Empty array

    def test_list_tasks_filters_by_user_id(self, client: TestClient, session: Session):
        """Test that listing tasks only returns tasks for the specified user."""
        # Arrange - Create tasks for different users
        task1 = Task(title="User1 Task", user_id="user1")
        task2 = Task(title="User2 Task", user_id="user2")
        task3 = Task(title="User1 Another Task", user_id="user1")

        session.add(task1)
        session.add(task2)
        session.add(task3)
        session.commit()

        # Act - Get tasks for user1
        response = client.get("/api/user1/tasks")

        # Assert
        assert response.status_code == 200

        data = response.json()
        assert len(data) == 2  # Only user1's tasks

        titles = [task["title"] for task in data]
        assert "User1 Task" in titles
        assert "User1 Another Task" in titles
        assert "User2 Task" not in titles  # user2's task not included


class TestGetSingleTask:
    """Tests for GET /api/{user_id}/tasks/{id} endpoint."""

    def test_get_task_by_id_success(self, client: TestClient, session: Session):
        """
        Test getting a single task returns 200 with complete task details.

        Acceptance Scenario 3:
        Given a task exists with id 5 for user_id "user123"
        When I GET /api/user123/tasks/5
        Then the API returns 200 status with the complete task details
        """
        # Arrange - Create a task
        user_id = "user123"
        task = Task(
            title="Buy groceries",
            description="Milk, eggs, bread",
            user_id=user_id
        )
        session.add(task)
        session.commit()
        session.refresh(task)

        task_id = task.id

        # Act
        response = client.get(f"/api/{user_id}/tasks/{task_id}")

        # Assert
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == task_id
        assert data["title"] == "Buy groceries"
        assert data["description"] == "Milk, eggs, bread"
        assert data["completed"] is False
        assert data["user_id"] == user_id
        assert data["created_at"] is not None
        assert data["updated_at"] is not None

    def test_get_task_nonexistent_id_returns_404(self, client: TestClient):
        """
        Test getting a non-existent task returns 404.

        Edge Case:
        What happens when a client requests a task ID that doesn't exist?
        Expected: 404 Not Found
        """
        # Arrange
        user_id = "user123"
        nonexistent_id = 99999

        # Act
        response = client.get(f"/api/{user_id}/tasks/{nonexistent_id}")

        # Assert
        assert response.status_code == 404

        data = response.json()
        assert "detail" in data
        assert data["detail"] == "Task not found"

    def test_get_task_wrong_user_returns_404(self, client: TestClient, session: Session):
        """Test that getting a task with wrong user_id returns 404."""
        # Arrange - Create task for user1
        task = Task(title="User1 Task", user_id="user1")
        session.add(task)
        session.commit()
        session.refresh(task)

        task_id = task.id

        # Act - Try to get task as user2
        response = client.get(f"/api/user2/tasks/{task_id}")

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Task not found"


class TestDataPersistence:
    """Tests for data persistence across requests."""

    def test_created_task_persists_across_requests(self, client: TestClient):
        """Test that created tasks persist and can be retrieved."""
        # Arrange
        user_id = "user123"
        task_data = {
            "title": "Persistent Task",
            "description": "This should persist"
        }

        # Act - Create task
        create_response = client.post(f"/api/{user_id}/tasks", json=task_data)
        assert create_response.status_code == 201

        created_task = create_response.json()
        task_id = created_task["id"]

        # Act - Retrieve task
        get_response = client.get(f"/api/{user_id}/tasks/{task_id}")

        # Assert
        assert get_response.status_code == 200

        retrieved_task = get_response.json()
        assert retrieved_task["id"] == task_id
        assert retrieved_task["title"] == "Persistent Task"
        assert retrieved_task["description"] == "This should persist"

    def test_multiple_tasks_persist_in_list(self, client: TestClient):
        """Test that multiple created tasks all appear in list endpoint."""
        # Arrange
        user_id = "user123"

        # Act - Create three tasks
        for i in range(1, 4):
            task_data = {"title": f"Task {i}"}
            response = client.post(f"/api/{user_id}/tasks", json=task_data)
            assert response.status_code == 201

        # Act - List all tasks
        list_response = client.get(f"/api/{user_id}/tasks")

        # Assert
        assert list_response.status_code == 200

        tasks = list_response.json()
        assert len(tasks) == 3

        titles = [task["title"] for task in tasks]
        assert "Task 1" in titles
        assert "Task 2" in titles
        assert "Task 3" in titles
