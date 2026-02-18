"""
Test dashboard API endpoints with various user scenarios.

This module tests the dashboard API endpoints including:
- Task statistics computation
- Activity metrics
- Authentication and authorization
- Data isolation between users
- Error handling
- Cache behavior
"""

import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.main import app
from app.database.session import get_db_context
from app.models.user import User
from app.models.task import Task
from app.models.task_share import TaskShare, SharePermission
from app.services.cache_service import clear_all_cache


class TestDashboardStatistics:
    """Test dashboard statistics endpoint."""

    @pytest.fixture
    def test_users(self):
        """Create test users."""
        with get_db_context() as db:
            user1 = User(
                id="test-dashboard-user-001",
                email="dashboard1@example.com",
                name="Dashboard User 1",
                password_hash="$2b$12$test_hash_1"
            )
            user2 = User(
                id="test-dashboard-user-002",
                email="dashboard2@example.com",
                name="Dashboard User 2",
                password_hash="$2b$12$test_hash_2"
            )
            db.add(user1)
            db.add(user2)
            db.commit()
            db.refresh(user1)
            db.refresh(user2)
            yield (user1, user2)

            # Cleanup
            db.delete(user1)
            db.delete(user2)
            db.commit()

    @pytest.fixture
    def test_tasks(self, test_users):
        """Create test tasks for users."""
        user1, user2 = test_users

        with get_db_context() as db:
            # User 1 tasks
            task1 = Task(
                title="User 1 Task 1",
                description="Pending task",
                completed=False,
                user_id=user1.id
            )
            task2 = Task(
                title="User 1 Task 2",
                description="Completed task",
                completed=True,
                user_id=user1.id
            )
            task3 = Task(
                title="User 1 Task 3",
                description="Another pending task",
                completed=False,
                user_id=user1.id
            )

            # User 2 tasks
            task4 = Task(
                title="User 2 Task 1",
                description="User 2 pending task",
                completed=False,
                user_id=user2.id
            )
            task5 = Task(
                title="User 2 Task 2",
                description="User 2 completed task",
                completed=True,
                user_id=user2.id
            )

            db.add_all([task1, task2, task3, task4, task5])
            db.commit()

            for task in [task1, task2, task3, task4, task5]:
                db.refresh(task)

            yield {
                "user1_tasks": [task1, task2, task3],
                "user2_tasks": [task4, task5]
            }

            # Cleanup
            for task in [task1, task2, task3, task4, task5]:
                db.delete(task)
            db.commit()

    @pytest.fixture
    def test_task_shares(self, test_users, test_tasks):
        """Create test task shares."""
        user1, user2 = test_users
        user1_tasks = test_tasks["user1_tasks"]

        with get_db_context() as db:
            # User 2 shares a task with User 1
            share = TaskShare(
                task_id=test_tasks["user2_tasks"][0].id,
                shared_with_user_id=user1.id,
                shared_by_user_id=user2.id,
                permission=SharePermission.VIEW
            )
            db.add(share)
            db.commit()
            db.refresh(share)

            yield share

            # Cleanup
            db.delete(share)
            db.commit()

    def test_statistics_correct_counts(self, test_users, test_tasks, test_task_shares):
        """Test that statistics return correct counts for user."""
        user1, user2 = test_users

        # Clear cache before test
        clear_all_cache()

        # Import here to avoid circular imports
        from app.services.dashboard_service import DashboardService

        with get_db_context() as db:
            service = DashboardService(db)

            # Test User 1 statistics
            stats1 = service.get_task_statistics(user1.id)
            assert stats1.total_tasks == 3  # User 1 has 3 tasks
            assert stats1.pending_tasks == 2  # 2 pending
            assert stats1.completed_tasks == 1  # 1 completed
            assert stats1.shared_tasks == 1  # 1 task shared with user 1

            # Test User 2 statistics
            stats2 = service.get_task_statistics(user2.id)
            assert stats2.total_tasks == 2  # User 2 has 2 tasks
            assert stats2.pending_tasks == 1  # 1 pending
            assert stats2.completed_tasks == 1  # 1 completed
            assert stats2.shared_tasks == 0  # No tasks shared with user 2

    def test_statistics_data_isolation(self, test_users, test_tasks):
        """Test that users can only see their own task statistics."""
        user1, user2 = test_users

        # Clear cache before test
        clear_all_cache()

        from app.services.dashboard_service import DashboardService

        with get_db_context() as db:
            service = DashboardService(db)

            # User 1 should not see User 2's tasks
            stats1 = service.get_task_statistics(user1.id)
            assert stats1.total_tasks == 3  # Only User 1's tasks

            # User 2 should not see User 1's tasks
            stats2 = service.get_task_statistics(user2.id)
            assert stats2.total_tasks == 2  # Only User 2's tasks

    def test_statistics_empty_user(self):
        """Test statistics for user with no tasks."""
        # Clear cache before test
        clear_all_cache()

        from app.services.dashboard_service import DashboardService

        with get_db_context() as db:
            # Create user with no tasks
            user = User(
                id="test-empty-user",
                email="empty@example.com",
                name="Empty User",
                password_hash="$2b$12$test_hash"
            )
            db.add(user)
            db.commit()
            db.refresh(user)

            service = DashboardService(db)
            stats = service.get_task_statistics(user.id)

            assert stats.total_tasks == 0
            assert stats.pending_tasks == 0
            assert stats.completed_tasks == 0
            assert stats.shared_tasks == 0

            # Cleanup
            db.delete(user)
            db.commit()


class TestDashboardActivity:
    """Test dashboard activity metrics."""

    @pytest.fixture
    def test_user_with_recent_tasks(self):
        """Create user with tasks created at different times."""
        with get_db_context() as db:
            user = User(
                id="test-activity-user",
                email="activity@example.com",
                name="Activity User",
                password_hash="$2b$12$test_hash"
            )
            db.add(user)
            db.commit()
            db.refresh(user)

            now = datetime.utcnow()
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            yesterday = today_start - timedelta(days=1)
            week_start = today_start - timedelta(days=today_start.weekday())

            # Task created today
            task1 = Task(
                title="Today Task",
                completed=False,
                user_id=user.id,
                created_at=now
            )

            # Task created yesterday
            task2 = Task(
                title="Yesterday Task",
                completed=True,
                user_id=user.id,
                created_at=yesterday,
                updated_at=now  # Completed today
            )

            # Task created this week
            task3 = Task(
                title="This Week Task",
                completed=False,
                user_id=user.id,
                created_at=week_start + timedelta(days=1)
            )

            db.add_all([task1, task2, task3])
            db.commit()

            for task in [task1, task2, task3]:
                db.refresh(task)

            yield (user, [task1, task2, task3])

            # Cleanup
            for task in [task1, task2, task3]:
                db.delete(task)
            db.delete(user)
            db.commit()

    def test_activity_metrics_computation(self, test_user_with_recent_tasks):
        """Test that activity metrics are computed correctly."""
        user, tasks = test_user_with_recent_tasks

        # Clear cache before test
        clear_all_cache()

        from app.services.dashboard_service import DashboardService

        with get_db_context() as db:
            service = DashboardService(db)
            metrics = service.get_activity_metrics(user.id)

            # Verify counts
            assert metrics.tasks_created_today >= 1  # At least the today task
            assert metrics.tasks_completed_today >= 1  # At least one completed today
            assert metrics.tasks_created_this_week >= 2  # At least 2 this week

            # Verify completion rate
            assert 0.0 <= metrics.completion_rate <= 100.0


class TestDashboardCache:
    """Test dashboard caching behavior."""

    def test_cache_stores_and_retrieves(self):
        """Test that cache stores and retrieves data correctly."""
        from app.services.cache_service import CacheService

        cache = CacheService(ttl_seconds=5)

        # Store data
        test_data = {"total_tasks": 10, "pending_tasks": 5}
        cache.set("test-user", test_data)

        # Retrieve data
        cached_data = cache.get("test-user")
        assert cached_data == test_data

    def test_cache_expiration(self):
        """Test that cache entries expire after TTL."""
        import time
        from app.services.cache_service import CacheService

        cache = CacheService(ttl_seconds=1)  # 1 second TTL

        # Store data
        cache.set("test-user", {"total_tasks": 10})

        # Immediately retrieve (should hit)
        assert cache.get("test-user") is not None

        # Wait for expiration
        time.sleep(1.1)

        # Should be expired
        assert cache.get("test-user") is None

    def test_cache_invalidation(self):
        """Test that cache can be invalidated."""
        from app.services.cache_service import CacheService

        cache = CacheService(ttl_seconds=10)

        # Store data
        cache.set("test-user", {"total_tasks": 10})

        # Verify stored
        assert cache.get("test-user") is not None

        # Invalidate
        cache.delete("test-user")

        # Should be gone
        assert cache.get("test-user") is None

    def test_cache_cleanup_expired(self):
        """Test that cleanup removes expired entries."""
        import time
        from app.services.cache_service import CacheService

        cache = CacheService(ttl_seconds=1)

        # Store multiple entries
        cache.set("user1", {"data": 1})
        cache.set("user2", {"data": 2})
        cache.set("user3", {"data": 3})

        # Wait for expiration
        time.sleep(1.1)

        # Cleanup
        removed = cache.cleanup_expired()
        assert removed == 3

        # Verify all removed
        assert cache.get("user1") is None
        assert cache.get("user2") is None
        assert cache.get("user3") is None


class TestDashboardBreakdown:
    """Test dashboard task breakdown endpoint."""

    @pytest.fixture
    def test_user_with_tasks(self):
        """Create user with mixed tasks."""
        with get_db_context() as db:
            user = User(
                id="test-breakdown-user",
                email="breakdown@example.com",
                name="Breakdown User",
                password_hash="$2b$12$test_hash"
            )
            db.add(user)
            db.commit()
            db.refresh(user)

            # Create tasks
            tasks = [
                Task(title=f"Task {i}", completed=(i % 2 == 0), user_id=user.id)
                for i in range(10)
            ]
            db.add_all(tasks)
            db.commit()

            for task in tasks:
                db.refresh(task)

            yield (user, tasks)

            # Cleanup
            for task in tasks:
                db.delete(task)
            db.delete(user)
            db.commit()

    def test_breakdown_computation(self, test_user_with_tasks):
        """Test task breakdown by status."""
        user, tasks = test_user_with_tasks

        # Clear cache before test
        clear_all_cache()

        from app.services.dashboard_service import DashboardService

        with get_db_context() as db:
            service = DashboardService(db)
            breakdown = service.get_task_breakdown_by_status(user.id)

            assert breakdown["total"] == 10
            assert breakdown["completed"] == 5  # Even indices (0, 2, 4, 6, 8)
            assert breakdown["pending"] == 5  # Odd indices (1, 3, 5, 7, 9)


class TestDashboardSharedDetails:
    """Test dashboard shared task details."""

    @pytest.fixture
    def test_users_with_shares(self, session: Session):
        """Create users with various task shares using test session."""
        # Use the test session instead of get_db_context()
        user1 = User(
            id="test-share-user-1",
            email="share1@example.com",
            name="Share User 1",
            password_hash="$2b$12$test_hash"
        )
        user2 = User(
            id="test-share-user-2",
            email="share2@example.com",
            name="Share User 2",
            password_hash="$2b$12$test_hash"
        )
        session.add_all([user1, user2])
        session.commit()
        session.refresh(user1)
        session.refresh(user2)

        # Create tasks
        task1 = Task(title="Task 1", user_id=user2.id)
        task2 = Task(title="Task 2", user_id=user2.id)
        task3 = Task(title="Task 3", user_id=user2.id)
        session.add_all([task1, task2, task3])
        session.commit()

        for task in [task1, task2, task3]:
            session.refresh(task)

        # Create shares (User 2 shares with User 1)
        share1 = TaskShare(
            task_id=task1.id,
            shared_with_user_id=user1.id,
            shared_by_user_id=user2.id,
            permission=SharePermission.VIEW
        )
        share2 = TaskShare(
            task_id=task2.id,
            shared_with_user_id=user1.id,
            shared_by_user_id=user2.id,
            permission=SharePermission.VIEW
        )
        share3 = TaskShare(
            task_id=task3.id,
            shared_with_user_id=user1.id,
            shared_by_user_id=user2.id,
            permission=SharePermission.EDIT
        )
        session.add_all([share1, share2, share3])
        session.commit()

        yield (user1, user2, [task1, task2, task3], [share1, share2, share3], session)

        # Cleanup
        for share in [share1, share2, share3]:
            session.delete(share)
        for task in [task1, task2, task3]:
            session.delete(task)
        session.delete(user1)
        session.delete(user2)
        session.commit()

    def test_shared_details_computation(self, test_users_with_shares):
        """Test shared task details computation."""
        user1, user2, tasks, shares, db = test_users_with_shares

        # Clear cache before test
        clear_all_cache()

        from app.services.dashboard_service import DashboardService

        # Use the test session instead of get_db_context()
        service = DashboardService(db)
        details = service.get_shared_task_details(user1.id)

        assert details["total_shared"] == 3
        assert details["view_only"] == 2  # share1 and share2
        assert details["can_edit"] == 1  # share3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
