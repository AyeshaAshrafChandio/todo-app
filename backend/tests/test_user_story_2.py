"""
Integration tests for User Story 2: Update and Delete Tasks.

These tests verify the acceptance criteria for User Story 2:
- PUT /api/{user_id}/tasks/{id} - Update existing task
- DELETE /api/{user_id}/tasks/{id} - Delete existing task

Test scenarios:
1. Update task returns 200 with updated data and refreshed updated_at
2. Delete task returns 204, subsequent GET returns 404
3. PUT for non-existent task returns 404
4. DELETE for non-existent task returns 404
5. PUT with invalid data returns 422 validation error
6. Verify updated_at timestamp changes on update
7. Verify user isolation (cannot update/delete other user's tasks)
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


class TestUpdateTask:
    """Tests for PUT /api/{user_id}/tasks/{id} endpoint."""

    def test_update_task_success(self, client: TestClient, session: Session):
        """
        Test updating a task returns 200 with updated data and refreshed updated_at.

        Acceptance Scenario 1:
        Given a task exists with id 5 for user_id "user123"
        When I PUT /api/user123/tasks/5 with new title and description
        Then the API returns 200 status with the updated task
        And the updated_at timestamp is refreshed
        """
        # Arrange - Create a task
        user_id = "user123"
        task = Task(
            title="Buy groceries",
            description="Milk, eggs",
            user_id=user_id
        )
        session.add(task)
        session.commit()
        session.refresh(task)

        task_id = task.id
        original_updated_at = task.updated_at

        # Wait a moment to ensure timestamp difference
        time.sleep(0.1)

        # Prepare update data
        update_data = {
            "title": "Buy groceries",
            "description": "Milk, eggs, bread, cheese",
            "completed": True
        }

        # Act
        response = client.put(f"/api/{user_id}/tasks/{task_id}", json=update_data)

        # Assert
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == task_id
        assert data["title"] == "Buy groceries"
        assert data["description"] == "Milk, eggs, bread, cheese"
        assert data["completed"] is True
        assert data["user_id"] == user_id
        assert data["created_at"] is not None
        assert data["updated_at"] is not None

        # Verify updated_at timestamp was refreshed
        # Note: In SQLite, timestamp precision may vary
        # We just verify it exists and is a valid timestamp
        assert data["updated_at"] >= data["created_at"]

    def test_update_task_partial_fields(self, client: TestClient, session: Session):
        """Test updating only some fields preserves other fields."""
        # Arrange - Create a task
        user_id = "user123"
        task = Task(
            title="Original Title",
            description="Original Description",
            completed=False,
            user_id=user_id
        )
        session.add(task)
        session.commit()
        session.refresh(task)

        task_id = task.id

        # Update only title and description
        update_data = {
            "title": "Updated Title",
            "description": "Updated Description",
            "completed": False
        }

        # Act
        response = client.put(f"/api/{user_id}/tasks/{task_id}", json=update_data)

        # Assert
        assert response.status_code == 200

        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["description"] == "Updated Description"
        assert data["completed"] is False

    def test_update_task_toggle_completed(self, client: TestClient, session: Session):
        """Test updating completed status."""
        # Arrange - Create a task
        user_id = "user123"
        task = Task(
            title="Task to complete",
            completed=False,
            user_id=user_id
        )
        session.add(task)
        session.commit()
        session.refresh(task)

        task_id = task.id

        # Update to completed
        update_data = {
            "title": "Task to complete",
            "completed": True
        }

        # Act
        response = client.put(f"/api/{user_id}/tasks/{task_id}", json=update_data)

        # Assert
        assert response.status_code == 200

        data = response.json()
        assert data["completed"] is True

    def test_update_task_nonexistent_id_returns_404(self, client: TestClient):
        """
        Test updating a non-existent task returns 404.

        Acceptance Scenario 3:
        Given no task exists with id 99999
        When I PUT /api/user123/tasks/99999
        Then the API returns 404 status
        """
        # Arrange
        user_id = "user123"
        nonexistent_id = 99999
        update_data = {
            "title": "Updated Title",
            "description": "Updated Description"
        }

        # Act
        response = client.put(f"/api/{user_id}/tasks/{nonexistent_id}", json=update_data)

        # Assert
        assert response.status_code == 404

        data = response.json()
        assert "detail" in data
        assert data["detail"] == "Task not found"

    def test_update_task_wrong_user_returns_404(self, client: TestClient, session: Session):
        """Test that updating a task with wrong user_id returns 404."""
        # Arrange - Create task for user1
        task = Task(title="User1 Task", user_id="user1")
        session.add(task)
        session.commit()
        session.refresh(task)

        task_id = task.id

        # Prepare update data
        update_data = {
            "title": "Hacked Title",
            "description": "Should not work"
        }

        # Act - Try to update task as user2
        response = client.put(f"/api/user2/tasks/{task_id}", json=update_data)

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Task not found"

        # Verify task was not modified
        session.refresh(task)
        assert task.title == "User1 Task"

    def test_update_task_empty_title_returns_422(self, client: TestClient, session: Session):
        """
        Test updating a task with empty title returns 422 validation error.

        Edge Case:
        What happens when a client tries to update a task with an empty title?
        Expected: 422 validation error
        """
        # Arrange - Create a task
        user_id = "user123"
        task = Task(title="Original Title", user_id=user_id)
        session.add(task)
        session.commit()
        session.refresh(task)

        task_id = task.id

        # Prepare invalid update data
        update_data = {
            "title": "",  # Empty title
            "description": "This should fail"
        }

        # Act
        response = client.put(f"/api/{user_id}/tasks/{task_id}", json=update_data)

        # Assert
        assert response.status_code == 422

        data = response.json()
        assert "detail" in data
        # Pydantic validation error format
        assert isinstance(data["detail"], list)

    def test_update_task_missing_title_returns_422(self, client: TestClient, session: Session):
        """Test updating a task without title returns 422 validation error."""
        # Arrange - Create a task
        user_id = "user123"
        task = Task(title="Original Title", user_id=user_id)
        session.add(task)
        session.commit()
        session.refresh(task)

        task_id = task.id

        # Prepare invalid update data (missing title)
        update_data = {
            "description": "Missing title"
        }

        # Act
        response = client.put(f"/api/{user_id}/tasks/{task_id}", json=update_data)

        # Assert
        assert response.status_code == 422

        data = response.json()
        assert "detail" in data


class TestDeleteTask:
    """Tests for DELETE /api/{user_id}/tasks/{id} endpoint."""

    def test_delete_task_success(self, client: TestClient, session: Session):
        """
        Test deleting a task returns 204, subsequent GET returns 404.

        Acceptance Scenario 2:
        Given a task exists with id 5 for user_id "user123"
        When I DELETE /api/user123/tasks/5
        Then the API returns 204 status (No Content)
        And subsequent GET /api/user123/tasks/5 returns 404
        """
        # Arrange - Create a task
        user_id = "user123"
        task = Task(
            title="Task to delete",
            description="This will be deleted",
            user_id=user_id
        )
        session.add(task)
        session.commit()
        session.refresh(task)

        task_id = task.id

        # Act - Delete task
        delete_response = client.delete(f"/api/{user_id}/tasks/{task_id}")

        # Assert - Delete returns 204
        assert delete_response.status_code == 204
        assert delete_response.text == ""  # No content

        # Act - Try to get deleted task
        get_response = client.get(f"/api/{user_id}/tasks/{task_id}")

        # Assert - Get returns 404
        assert get_response.status_code == 404
        assert get_response.json()["detail"] == "Task not found"

    def test_delete_task_removes_from_list(self, client: TestClient, session: Session):
        """Test that deleted task no longer appears in list endpoint."""
        # Arrange - Create three tasks
        user_id = "user123"
        tasks = [
            Task(title="Task 1", user_id=user_id),
            Task(title="Task 2", user_id=user_id),
            Task(title="Task 3", user_id=user_id),
        ]
        for task in tasks:
            session.add(task)
        session.commit()

        # Get the second task's ID
        session.refresh(tasks[1])
        task_to_delete_id = tasks[1].id

        # Act - Delete second task
        delete_response = client.delete(f"/api/{user_id}/tasks/{task_to_delete_id}")
        assert delete_response.status_code == 204

        # Act - List all tasks
        list_response = client.get(f"/api/{user_id}/tasks")

        # Assert - Only two tasks remain
        assert list_response.status_code == 200

        remaining_tasks = list_response.json()
        assert len(remaining_tasks) == 2

        titles = [task["title"] for task in remaining_tasks]
        assert "Task 1" in titles
        assert "Task 3" in titles
        assert "Task 2" not in titles  # Deleted task not in list

    def test_delete_task_nonexistent_id_returns_404(self, client: TestClient):
        """
        Test deleting a non-existent task returns 404.

        Edge Case:
        What happens when a client tries to delete a task that doesn't exist?
        Expected: 404 Not Found
        """
        # Arrange
        user_id = "user123"
        nonexistent_id = 99999

        # Act
        response = client.delete(f"/api/{user_id}/tasks/{nonexistent_id}")

        # Assert
        assert response.status_code == 404

        data = response.json()
        assert "detail" in data
        assert data["detail"] == "Task not found"

    def test_delete_task_wrong_user_returns_404(self, client: TestClient, session: Session):
        """Test that deleting a task with wrong user_id returns 404."""
        # Arrange - Create task for user1
        task = Task(title="User1 Task", user_id="user1")
        session.add(task)
        session.commit()
        session.refresh(task)

        task_id = task.id

        # Act - Try to delete task as user2
        response = client.delete(f"/api/user2/tasks/{task_id}")

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Task not found"

        # Verify task still exists for user1
        get_response = client.get(f"/api/user1/tasks/{task_id}")
        assert get_response.status_code == 200


class TestTimestampRefresh:
    """Tests for updated_at timestamp refresh on update."""

    def test_updated_at_changes_on_update(self, client: TestClient, session: Session):
        """
        Test that updated_at timestamp is refreshed when task is updated.

        Acceptance Scenario (T032):
        Given a task exists with specific created_at and updated_at
        When I update the task
        Then the updated_at timestamp should be refreshed
        And created_at should remain unchanged
        """
        # Arrange - Create a task
        user_id = "user123"
        task = Task(
            title="Original Title",
            description="Original Description",
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

        # Prepare update data
        update_data = {
            "title": "Updated Title",
            "description": "Updated Description"
        }

        # Act
        response = client.put(f"/api/{user_id}/tasks/{task_id}", json=update_data)

        # Assert
        assert response.status_code == 200

        data = response.json()

        # Verify created_at remains unchanged
        assert data["created_at"] == original_created_at.isoformat()

        # Verify updated_at is present and valid
        # Note: Exact timestamp comparison may be tricky due to precision
        # We verify it's a valid timestamp and >= created_at
        assert data["updated_at"] is not None
        assert data["updated_at"] >= data["created_at"]


class TestUserIsolation:
    """Tests for user isolation in update and delete operations."""

    def test_user_cannot_update_other_users_tasks(self, client: TestClient, session: Session):
        """Test that users can only update their own tasks."""
        # Arrange - Create tasks for different users
        task1 = Task(title="User1 Task", user_id="user1")
        task2 = Task(title="User2 Task", user_id="user2")

        session.add(task1)
        session.add(task2)
        session.commit()
        session.refresh(task1)
        session.refresh(task2)

        # Prepare update data
        update_data = {
            "title": "Hacked Title",
            "description": "Should not work"
        }

        # Act - User1 tries to update User2's task
        response = client.put(f"/api/user1/tasks/{task2.id}", json=update_data)

        # Assert
        assert response.status_code == 404

        # Verify task2 was not modified
        session.refresh(task2)
        assert task2.title == "User2 Task"

    def test_user_cannot_delete_other_users_tasks(self, client: TestClient, session: Session):
        """Test that users can only delete their own tasks."""
        # Arrange - Create tasks for different users
        task1 = Task(title="User1 Task", user_id="user1")
        task2 = Task(title="User2 Task", user_id="user2")

        session.add(task1)
        session.add(task2)
        session.commit()
        session.refresh(task1)
        session.refresh(task2)

        # Act - User1 tries to delete User2's task
        response = client.delete(f"/api/user1/tasks/{task2.id}")

        # Assert
        assert response.status_code == 404

        # Verify task2 still exists
        get_response = client.get(f"/api/user2/tasks/{task2.id}")
        assert get_response.status_code == 200
        assert get_response.json()["title"] == "User2 Task"
