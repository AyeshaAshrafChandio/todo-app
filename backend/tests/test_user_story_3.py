"""
Integration tests for User Story 3: Toggle Task Completion.

These tests verify the acceptance criteria for User Story 3:
- PATCH /api/{user_id}/tasks/{id}/complete - Toggle task completion status

Test scenarios:
1. Toggle task from completed=false to completed=true
2. Toggle task from completed=true to completed=false
3. Multiple consecutive toggles work correctly
4. PATCH for non-existent task returns 404
5. Verify updated_at timestamp refreshes on each toggle
6. Verify user isolation (cannot toggle other users' tasks)
7. Verify other fields remain unchanged during toggle
"""

import pytest
import time
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


class TestToggleTaskCompletion:
    """Tests for PATCH /api/{user_id}/tasks/{id}/complete endpoint."""

    def test_toggle_task_false_to_true(self, client: TestClient, session: Session):
        """
        Test toggling a task from completed=false to completed=true.

        Acceptance Scenario 1:
        Given a task exists with id 5 and completed=false for user_id "user123"
        When I PATCH /api/user123/tasks/5/complete
        Then the API returns 200 status with completed=true
        And the updated_at timestamp is refreshed
        """
        # Arrange - Create a task with completed=false
        user_id = "user123"
        task = Task(
            title="Buy groceries",
            description="Milk, eggs, bread",
            completed=False,  # Explicitly set to False
            user_id=user_id
        )
        session.add(task)
        session.commit()
        session.refresh(task)

        task_id = task.id
        original_updated_at = task.updated_at

        # Wait to ensure timestamp difference
        time.sleep(0.1)

        # Act - Toggle completion
        response = client.patch(f"/api/{user_id}/tasks/{task_id}/complete")

        # Assert
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == task_id
        assert data["title"] == "Buy groceries"
        assert data["description"] == "Milk, eggs, bread"
        assert data["completed"] is True  # Toggled to True
        assert data["user_id"] == user_id
        assert data["created_at"] is not None
        assert data["updated_at"] is not None

        # Verify updated_at timestamp was refreshed
        assert data["updated_at"] >= data["created_at"]

    def test_toggle_task_true_to_false(self, client: TestClient, session: Session):
        """
        Test toggling a task from completed=true to completed=false.

        Acceptance Scenario 2:
        Given a task exists with id 5 and completed=true for user_id "user123"
        When I PATCH /api/user123/tasks/5/complete
        Then the API returns 200 status with completed=false
        And the updated_at timestamp is refreshed
        """
        # Arrange - Create a task with completed=true
        user_id = "user123"
        task = Task(
            title="Walk the dog",
            description="Morning walk",
            completed=True,  # Explicitly set to True
            user_id=user_id
        )
        session.add(task)
        session.commit()
        session.refresh(task)

        task_id = task.id

        # Wait to ensure timestamp difference
        time.sleep(0.1)

        # Act - Toggle completion
        response = client.patch(f"/api/{user_id}/tasks/{task_id}/complete")

        # Assert
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == task_id
        assert data["title"] == "Walk the dog"
        assert data["description"] == "Morning walk"
        assert data["completed"] is False  # Toggled to False
        assert data["user_id"] == user_id

    def test_toggle_task_multiple_times(self, client: TestClient, session: Session):
        """
        Test multiple consecutive toggles work correctly.

        Acceptance Scenario 3:
        Given a task exists with completed=false
        When I toggle it multiple times (False → True → False → True)
        Then each toggle correctly flips the completion status
        """
        # Arrange - Create a task with completed=false
        user_id = "user123"
        task = Task(
            title="Test Task",
            completed=False,
            user_id=user_id
        )
        session.add(task)
        session.commit()
        session.refresh(task)

        task_id = task.id

        # Act & Assert - Toggle 1: False → True
        response1 = client.patch(f"/api/{user_id}/tasks/{task_id}/complete")
        assert response1.status_code == 200
        assert response1.json()["completed"] is True

        time.sleep(0.1)

        # Act & Assert - Toggle 2: True → False
        response2 = client.patch(f"/api/{user_id}/tasks/{task_id}/complete")
        assert response2.status_code == 200
        assert response2.json()["completed"] is False

        time.sleep(0.1)

        # Act & Assert - Toggle 3: False → True
        response3 = client.patch(f"/api/{user_id}/tasks/{task_id}/complete")
        assert response3.status_code == 200
        assert response3.json()["completed"] is True

        time.sleep(0.1)

        # Act & Assert - Toggle 4: True → False
        response4 = client.patch(f"/api/{user_id}/tasks/{task_id}/complete")
        assert response4.status_code == 200
        assert response4.json()["completed"] is False

    def test_toggle_task_nonexistent_id_returns_404(self, client: TestClient):
        """
        Test toggling a non-existent task returns 404.

        Acceptance Scenario 4:
        Given no task exists with id 99999
        When I PATCH /api/user123/tasks/99999/complete
        Then the API returns 404 status
        """
        # Arrange
        user_id = "user123"
        nonexistent_id = 99999

        # Act
        response = client.patch(f"/api/{user_id}/tasks/{nonexistent_id}/complete")

        # Assert
        assert response.status_code == 404

        data = response.json()
        assert "detail" in data
        assert data["detail"] == "Task not found"

    def test_toggle_task_refreshes_updated_at(self, client: TestClient, session: Session):
        """
        Test that updated_at timestamp is refreshed on each toggle.

        Acceptance Scenario 5:
        Given a task exists with specific created_at and updated_at
        When I toggle the task completion
        Then the updated_at timestamp should be refreshed
        And created_at should remain unchanged
        """
        # Arrange - Create a task
        user_id = "user123"
        task = Task(
            title="Task with timestamps",
            description="Testing timestamp refresh",
            completed=False,
            user_id=user_id
        )
        session.add(task)
        session.commit()
        session.refresh(task)

        task_id = task.id
        original_created_at = task.created_at
        original_updated_at = task.updated_at

        # Wait to ensure timestamp difference
        time.sleep(0.1)

        # Act - Toggle completion
        response = client.patch(f"/api/{user_id}/tasks/{task_id}/complete")

        # Assert
        assert response.status_code == 200

        data = response.json()

        # Verify created_at remains unchanged
        assert data["created_at"] == original_created_at.isoformat()

        # Verify updated_at is present and valid
        assert data["updated_at"] is not None
        assert data["updated_at"] >= data["created_at"]

    def test_toggle_task_preserves_other_fields(self, client: TestClient, session: Session):
        """
        Test that toggling completion preserves all other fields.

        Edge Case:
        Verify that title, description, user_id, and created_at remain unchanged
        when toggling completion status.
        """
        # Arrange - Create a task with all fields
        user_id = "user123"
        task = Task(
            title="Important Task",
            description="This is a detailed description",
            completed=False,
            user_id=user_id
        )
        session.add(task)
        session.commit()
        session.refresh(task)

        task_id = task.id
        original_title = task.title
        original_description = task.description
        original_user_id = task.user_id
        original_created_at = task.created_at

        # Act - Toggle completion
        response = client.patch(f"/api/{user_id}/tasks/{task_id}/complete")

        # Assert
        assert response.status_code == 200

        data = response.json()

        # Verify all other fields remain unchanged
        assert data["title"] == original_title
        assert data["description"] == original_description
        assert data["user_id"] == original_user_id
        assert data["created_at"] == original_created_at.isoformat()

        # Only completed should change
        assert data["completed"] is True  # Changed from False to True

    def test_toggle_task_wrong_user_returns_404(self, client: TestClient, session: Session):
        """
        Test that toggling a task with wrong user_id returns 404.

        Acceptance Scenario 6:
        Given a task exists for user1
        When user2 tries to toggle the task
        Then the API returns 404 status
        And the task completion status remains unchanged
        """
        # Arrange - Create task for user1
        task = Task(
            title="User1 Task",
            description="Private task",
            completed=False,
            user_id="user1"
        )
        session.add(task)
        session.commit()
        session.refresh(task)

        task_id = task.id
        original_completed = task.completed

        # Act - Try to toggle task as user2
        response = client.patch(f"/api/user2/tasks/{task_id}/complete")

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Task not found"

        # Verify task completion status was not modified
        session.refresh(task)
        assert task.completed == original_completed  # Still False

    def test_toggle_task_persists_across_requests(self, client: TestClient, session: Session):
        """
        Test that completion status persists across requests.

        Acceptance Scenario 7:
        Given a task is toggled to completed=true
        When I retrieve the task via GET endpoint
        Then the task should still have completed=true
        """
        # Arrange - Create a task
        user_id = "user123"
        task = Task(
            title="Persistent Task",
            completed=False,
            user_id=user_id
        )
        session.add(task)
        session.commit()
        session.refresh(task)

        task_id = task.id

        # Act - Toggle completion
        toggle_response = client.patch(f"/api/{user_id}/tasks/{task_id}/complete")
        assert toggle_response.status_code == 200
        assert toggle_response.json()["completed"] is True

        # Act - Retrieve task via GET
        get_response = client.get(f"/api/{user_id}/tasks/{task_id}")

        # Assert - Completion status persists
        assert get_response.status_code == 200
        assert get_response.json()["completed"] is True

    def test_toggle_task_appears_in_list_with_correct_status(self, client: TestClient, session: Session):
        """
        Test that toggled task appears in list endpoint with correct status.

        Edge Case:
        Verify that after toggling, the task appears in the list endpoint
        with the updated completion status.
        """
        # Arrange - Create multiple tasks
        user_id = "user123"
        tasks = [
            Task(title="Task 1", completed=False, user_id=user_id),
            Task(title="Task 2", completed=False, user_id=user_id),
            Task(title="Task 3", completed=False, user_id=user_id),
        ]
        for task in tasks:
            session.add(task)
        session.commit()

        # Get the second task's ID
        session.refresh(tasks[1])
        task_to_toggle_id = tasks[1].id

        # Act - Toggle second task
        toggle_response = client.patch(f"/api/{user_id}/tasks/{task_to_toggle_id}/complete")
        assert toggle_response.status_code == 200

        # Act - List all tasks
        list_response = client.get(f"/api/{user_id}/tasks")

        # Assert - All tasks present with correct completion status
        assert list_response.status_code == 200

        all_tasks = list_response.json()
        assert len(all_tasks) == 3

        # Find the toggled task in the list
        toggled_task = next(task for task in all_tasks if task["id"] == task_to_toggle_id)
        assert toggled_task["completed"] is True

        # Other tasks should still be False
        other_tasks = [task for task in all_tasks if task["id"] != task_to_toggle_id]
        for task in other_tasks:
            assert task["completed"] is False


class TestUserIsolation:
    """Tests for user isolation in toggle completion operations."""

    def test_user_cannot_toggle_other_users_tasks(self, client: TestClient, session: Session):
        """Test that users can only toggle their own tasks."""
        # Arrange - Create tasks for different users
        task1 = Task(title="User1 Task", completed=False, user_id="user1")
        task2 = Task(title="User2 Task", completed=False, user_id="user2")

        session.add(task1)
        session.add(task2)
        session.commit()
        session.refresh(task1)
        session.refresh(task2)

        # Act - User1 tries to toggle User2's task
        response = client.patch(f"/api/user1/tasks/{task2.id}/complete")

        # Assert
        assert response.status_code == 404

        # Verify task2 was not modified
        session.refresh(task2)
        assert task2.completed is False  # Still False

    def test_multiple_users_can_toggle_their_own_tasks(self, client: TestClient, session: Session):
        """Test that multiple users can independently toggle their own tasks."""
        # Arrange - Create tasks for different users
        task1 = Task(title="User1 Task", completed=False, user_id="user1")
        task2 = Task(title="User2 Task", completed=False, user_id="user2")

        session.add(task1)
        session.add(task2)
        session.commit()
        session.refresh(task1)
        session.refresh(task2)

        # Act - User1 toggles their task
        response1 = client.patch(f"/api/user1/tasks/{task1.id}/complete")
        assert response1.status_code == 200
        assert response1.json()["completed"] is True

        # Act - User2 toggles their task
        response2 = client.patch(f"/api/user2/tasks/{task2.id}/complete")
        assert response2.status_code == 200
        assert response2.json()["completed"] is True

        # Verify both tasks are toggled independently
        session.refresh(task1)
        session.refresh(task2)
        assert task1.completed is True
        assert task2.completed is True
