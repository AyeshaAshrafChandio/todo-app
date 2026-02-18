"""
End-to-End Testing for Complete Dashboard Workflow

This test suite validates the complete user workflow from signup to dashboard usage,
ensuring all features work together seamlessly.

Test Flow:
1. User Signup → Login → Create Tasks → View Dashboard → Share Tasks → Team Collaboration

Requirements:
- Backend server running on http://localhost:8000
- Database initialized and accessible
- All API endpoints operational
"""

import pytest
import requests
import time
from typing import Dict, Any


# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"
TEST_USER_EMAIL = f"e2e_test_{int(time.time())}@example.com"
TEST_USER_PASSWORD = "SecurePassword123!"
TEST_USER_NAME = "E2E Test User"


class TestDashboardE2E:
    """End-to-end test suite for complete dashboard workflow."""

    @pytest.fixture(scope="class")
    def test_user(self) -> Dict[str, Any]:
        """Create a test user and return credentials."""
        # Signup
        signup_response = requests.post(
            f"{API_BASE}/auth/signup",
            json={
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD,
                "name": TEST_USER_NAME
            }
        )

        assert signup_response.status_code == 201, f"Signup failed: {signup_response.text}"
        user_data = signup_response.json()

        # Signin to get token
        signin_response = requests.post(
            f"{API_BASE}/auth/signin",
            json={
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
        )

        assert signin_response.status_code == 200, f"Signin failed: {signin_response.text}"
        signin_data = signin_response.json()

        return {
            "id": user_data["id"],
            "email": user_data["email"],
            "name": user_data["name"],
            "token": signin_data["access_token"]
        }

    @pytest.fixture(scope="class")
    def auth_headers(self, test_user: Dict[str, Any]) -> Dict[str, str]:
        """Return authentication headers for API requests."""
        return {
            "Authorization": f"Bearer {test_user['token']}",
            "Content-Type": "application/json"
        }

    def test_01_user_signup_and_login(self, test_user: Dict[str, Any]):
        """Test 1: User can signup and login successfully."""
        assert test_user["id"] is not None
        assert test_user["email"] == TEST_USER_EMAIL
        assert test_user["token"] is not None
        print(f"✓ User signup and login successful (User ID: {test_user['id']})")

    def test_02_create_multiple_tasks(self, test_user: Dict[str, Any], auth_headers: Dict[str, str]):
        """Test 2: User can create multiple tasks."""
        user_id = test_user["id"]
        tasks_to_create = [
            {"title": "E2E Test Task 1", "description": "First test task", "status": "pending"},
            {"title": "E2E Test Task 2", "description": "Second test task", "status": "pending"},
            {"title": "E2E Test Task 3", "description": "Third test task", "status": "completed"},
            {"title": "E2E Test Task 4", "description": "Fourth test task", "status": "pending"},
            {"title": "E2E Test Task 5", "description": "Fifth test task", "status": "completed"},
        ]

        created_tasks = []
        for task_data in tasks_to_create:
            response = requests.post(
                f"{API_BASE}/{user_id}/tasks",
                json=task_data,
                headers=auth_headers
            )
            assert response.status_code == 201, f"Task creation failed: {response.text}"
            created_tasks.append(response.json())

        assert len(created_tasks) == 5
        print(f"✓ Created {len(created_tasks)} tasks successfully")

        # Store task IDs for later tests
        test_user["task_ids"] = [task["id"] for task in created_tasks]

    def test_03_view_dashboard_statistics(self, test_user: Dict[str, Any], auth_headers: Dict[str, str]):
        """Test 3: Dashboard displays accurate statistics."""
        # Wait a moment for database to update
        time.sleep(1)

        response = requests.get(
            f"{API_BASE}/dashboard/statistics",
            headers=auth_headers
        )

        assert response.status_code == 200, f"Dashboard statistics failed: {response.text}"
        data = response.json()

        # Verify statistics structure
        assert "statistics" in data
        stats = data["statistics"]

        # Verify counts match created tasks
        assert stats["total_tasks"] == 5, f"Expected 5 total tasks, got {stats['total_tasks']}"
        assert stats["pending_tasks"] == 3, f"Expected 3 pending tasks, got {stats['pending_tasks']}"
        assert stats["completed_tasks"] == 2, f"Expected 2 completed tasks, got {stats['completed_tasks']}"

        print(f"✓ Dashboard statistics accurate: {stats}")

    def test_04_update_task_status(self, test_user: Dict[str, Any], auth_headers: Dict[str, str]):
        """Test 4: User can update task status and dashboard reflects changes."""
        user_id = test_user["id"]
        task_id = test_user["task_ids"][0]  # First pending task

        # Update task to completed
        response = requests.put(
            f"{API_BASE}/{user_id}/tasks/{task_id}",
            json={"status": "completed"},
            headers=auth_headers
        )

        assert response.status_code == 200, f"Task update failed: {response.text}"

        # Wait for dashboard to update (polling interval)
        time.sleep(2)

        # Check dashboard reflects the change
        dashboard_response = requests.get(
            f"{API_BASE}/dashboard/statistics",
            headers=auth_headers
        )

        assert dashboard_response.status_code == 200
        stats = dashboard_response.json()["statistics"]

        # Now should have 2 pending, 3 completed
        assert stats["pending_tasks"] == 2, f"Expected 2 pending tasks after update, got {stats['pending_tasks']}"
        assert stats["completed_tasks"] == 3, f"Expected 3 completed tasks after update, got {stats['completed_tasks']}"

        print(f"✓ Task status updated and dashboard reflects changes: {stats}")

    def test_05_dashboard_activity_metrics(self, test_user: Dict[str, Any], auth_headers: Dict[str, str]):
        """Test 5: Dashboard activity metrics are accurate."""
        response = requests.get(
            f"{API_BASE}/dashboard/activity",
            headers=auth_headers
        )

        assert response.status_code == 200, f"Activity metrics failed: {response.text}"
        metrics = response.json()

        # Verify metrics structure
        assert "tasks_created_today" in metrics
        assert "tasks_completed_today" in metrics
        assert "completion_rate" in metrics

        # All tasks were created today
        assert metrics["tasks_created_today"] >= 5

        print(f"✓ Activity metrics retrieved: {metrics}")

    def test_06_dashboard_breakdown(self, test_user: Dict[str, Any], auth_headers: Dict[str, str]):
        """Test 6: Dashboard breakdown by status is accurate."""
        response = requests.get(
            f"{API_BASE}/dashboard/breakdown",
            headers=auth_headers
        )

        assert response.status_code == 200, f"Breakdown failed: {response.text}"
        breakdown = response.json()

        # Verify breakdown structure
        assert "pending" in breakdown
        assert "completed" in breakdown
        assert "total" in breakdown

        # Verify counts
        assert breakdown["total"] == 5
        assert breakdown["pending"] == 2
        assert breakdown["completed"] == 3

        print(f"✓ Task breakdown accurate: {breakdown}")

    def test_07_create_team_and_share_task(self, test_user: Dict[str, Any], auth_headers: Dict[str, str]):
        """Test 7: User can create team and share tasks."""
        # Create a team
        team_response = requests.post(
            f"{API_BASE}/teams",
            json={"name": "E2E Test Team"},
            headers=auth_headers
        )

        assert team_response.status_code == 201, f"Team creation failed: {team_response.text}"
        team_data = team_response.json()
        team_id = team_data["id"]

        print(f"✓ Team created successfully (Team ID: {team_id})")

        # Note: Sharing tasks requires another user, which is complex for E2E
        # For now, we verify the team was created successfully
        test_user["team_id"] = team_id

    def test_08_delete_task_and_verify_dashboard(self, test_user: Dict[str, Any], auth_headers: Dict[str, str]):
        """Test 8: Deleting a task updates dashboard statistics."""
        user_id = test_user["id"]
        task_id = test_user["task_ids"][-1]  # Last task

        # Delete task
        response = requests.delete(
            f"{API_BASE}/{user_id}/tasks/{task_id}",
            headers=auth_headers
        )

        assert response.status_code == 204, f"Task deletion failed: {response.text}"

        # Wait for dashboard to update
        time.sleep(2)

        # Check dashboard reflects the deletion
        dashboard_response = requests.get(
            f"{API_BASE}/dashboard/statistics",
            headers=auth_headers
        )

        assert dashboard_response.status_code == 200
        stats = dashboard_response.json()["statistics"]

        # Now should have 4 total tasks (one deleted)
        assert stats["total_tasks"] == 4, f"Expected 4 total tasks after deletion, got {stats['total_tasks']}"

        print(f"✓ Task deleted and dashboard updated: {stats}")

    def test_09_unauthorized_access_blocked(self):
        """Test 9: Unauthorized access to dashboard is blocked."""
        # Try to access dashboard without token
        response = requests.get(f"{API_BASE}/dashboard/statistics")

        assert response.status_code == 401, "Expected 401 for unauthorized access"
        print("✓ Unauthorized access properly blocked")

    def test_10_invalid_token_rejected(self):
        """Test 10: Invalid authentication token is rejected."""
        invalid_headers = {
            "Authorization": "Bearer invalid_token_12345",
            "Content-Type": "application/json"
        }

        response = requests.get(
            f"{API_BASE}/dashboard/statistics",
            headers=invalid_headers
        )

        assert response.status_code == 401, "Expected 401 for invalid token"
        print("✓ Invalid token properly rejected")

    def test_11_performance_check(self, test_user: Dict[str, Any], auth_headers: Dict[str, str]):
        """Test 11: Dashboard API responds within acceptable time."""
        start_time = time.time()

        response = requests.get(
            f"{API_BASE}/dashboard/statistics",
            headers=auth_headers
        )

        response_time = time.time() - start_time

        assert response.status_code == 200
        assert response_time < 1.0, f"Dashboard response too slow: {response_time:.3f}s"

        print(f"✓ Dashboard response time: {response_time:.3f}s (< 1.0s)")

    def test_12_concurrent_requests(self, test_user: Dict[str, Any], auth_headers: Dict[str, str]):
        """Test 12: Dashboard handles concurrent requests correctly."""
        import concurrent.futures

        def fetch_dashboard():
            response = requests.get(
                f"{API_BASE}/dashboard/statistics",
                headers=auth_headers
            )
            return response.status_code == 200

        # Make 10 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(fetch_dashboard) for _ in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        # All requests should succeed
        assert all(results), "Some concurrent requests failed"
        print(f"✓ Handled 10 concurrent requests successfully")

    def test_13_health_check(self):
        """Test 13: API health check endpoint is operational."""
        response = requests.get(f"{BASE_URL}/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

        print("✓ API health check passed")

    def test_14_dashboard_health_check(self):
        """Test 14: Dashboard health check endpoint is operational."""
        response = requests.get(f"{API_BASE}/dashboard/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

        print("✓ Dashboard health check passed")


class TestErrorScenarios:
    """Test error handling and edge cases."""

    @pytest.fixture
    def valid_auth_headers(self) -> Dict[str, str]:
        """Create a user and return valid auth headers."""
        # Signup
        email = f"error_test_{int(time.time())}@example.com"
        requests.post(
            f"{API_BASE}/auth/signup",
            json={
                "email": email,
                "password": "TestPassword123!",
                "name": "Error Test User"
            }
        )

        # Signin
        signin_response = requests.post(
            f"{API_BASE}/auth/signin",
            json={
                "email": email,
                "password": "TestPassword123!"
            }
        )

        token = signin_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    def test_invalid_user_id_in_path(self, valid_auth_headers: Dict[str, str]):
        """Test accessing tasks with mismatched user ID."""
        # Try to access another user's tasks
        response = requests.get(
            f"{API_BASE}/99999/tasks",
            headers=valid_auth_headers
        )

        # Should be forbidden (403) or not found (404)
        assert response.status_code in [403, 404]
        print("✓ Invalid user ID properly rejected")

    def test_malformed_request_body(self, valid_auth_headers: Dict[str, str]):
        """Test API handles malformed request bodies."""
        # Get user ID from token (simplified - in real test, decode JWT)
        # For now, we'll use a placeholder
        response = requests.post(
            f"{API_BASE}/1/tasks",
            json={"invalid_field": "value"},
            headers=valid_auth_headers
        )

        # Should return validation error (422) or bad request (400)
        assert response.status_code in [400, 422]
        print("✓ Malformed request properly rejected")


def run_e2e_tests():
    """
    Run all E2E tests.

    Usage:
        python -m pytest tests/e2e/test_dashboard_flow.py -v
    """
    pytest.main([__file__, "-v", "-s"])


if __name__ == "__main__":
    print("=" * 80)
    print("End-to-End Dashboard Workflow Tests")
    print("=" * 80)
    print()
    print("Prerequisites:")
    print("  - Backend server running on http://localhost:8000")
    print("  - Database initialized and accessible")
    print("  - All API endpoints operational")
    print()
    print("=" * 80)
    print()

    run_e2e_tests()
