"""
Dashboard service for computing task statistics and analytics.

This module provides business logic for dashboard-related operations,
including task statistics computation, activity metrics, and data aggregation.
"""

from datetime import datetime, timedelta
from typing import Optional
from sqlmodel import Session, select, func
from sqlalchemy import and_, or_
from fastapi import Depends
from app.models.task import Task
from app.models.task_share import TaskShare
from app.schemas.dashboard import TaskStatistics, ActivityMetrics
from app.database.session import get_db


class DashboardService:
    """
    Service class for dashboard operations.

    This service provides methods to compute task statistics and activity
    metrics for users. All queries are filtered by user_id to ensure
    data isolation and security.
    """

    def __init__(self, db: Session):
        """
        Initialize dashboard service.

        Args:
            db: SQLModel database session
        """
        self.db = db

    def get_task_statistics(self, user_id: str) -> TaskStatistics:
        """
        Get task statistics for a user.

        This method computes aggregated task counts for a user, including:
        - Total tasks owned by the user
        - Pending (incomplete) tasks
        - Completed tasks
        - Tasks shared with the user by others

        All queries are optimized with COUNT operations and proper indexing.
        Data is filtered by user_id to ensure security and isolation.

        Args:
            user_id: User identifier (UUID string)

        Returns:
            TaskStatistics: Aggregated task counts

        Example:
            ```python
            service = DashboardService(db)
            stats = service.get_task_statistics("user-123")
            print(f"Total tasks: {stats.total_tasks}")
            print(f"Pending: {stats.pending_tasks}")
            print(f"Completed: {stats.completed_tasks}")
            print(f"Shared: {stats.shared_tasks}")
            ```

        Performance:
            - Uses COUNT queries (no data transfer, computed in database)
            - Leverages indexes on user_id and completed columns
            - Expected query time: <50ms for typical datasets
        """
        # Query 1: Total tasks owned by user
        # Uses index: idx_tasks_user_id
        total_tasks = self.db.exec(
            select(func.count(Task.id))
            .where(Task.user_id == user_id)
        ).one()

        # Query 2: Pending tasks (not completed)
        # Uses index: idx_tasks_user_id
        # Could benefit from partial index: idx_tasks_user_id_where_active
        pending_tasks = self.db.exec(
            select(func.count(Task.id))
            .where(
                and_(
                    Task.user_id == user_id,
                    Task.completed == False
                )
            )
        ).one()

        # Query 3: Completed tasks
        # Uses index: idx_tasks_user_id
        completed_tasks = self.db.exec(
            select(func.count(Task.id))
            .where(
                and_(
                    Task.user_id == user_id,
                    Task.completed == True
                )
            )
        ).one()

        # Query 4: Tasks shared with user by others
        # Uses index: idx_task_shares_shared_with_user_id
        shared_tasks = self.db.exec(
            select(func.count(TaskShare.id))
            .where(TaskShare.shared_with_user_id == user_id)
        ).one()

        return TaskStatistics(
            total_tasks=total_tasks,
            pending_tasks=pending_tasks,
            completed_tasks=completed_tasks,
            shared_tasks=shared_tasks
        )

    def get_activity_metrics(self, user_id: str) -> ActivityMetrics:
        """
        Get activity metrics for a user.

        This method computes activity-based metrics including task creation
        and completion rates over different time periods.

        Args:
            user_id: User identifier (UUID string)

        Returns:
            ActivityMetrics: User activity metrics

        Example:
            ```python
            service = DashboardService(db)
            metrics = service.get_activity_metrics("user-123")
            print(f"Created today: {metrics.tasks_created_today}")
            print(f"Completion rate: {metrics.completion_rate}%")
            ```

        Performance:
            - Uses COUNT queries with date filtering
            - Leverages composite index: idx_tasks_user_id_created_at
            - Expected query time: <100ms for typical datasets
        """
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=today_start.weekday())

        # Tasks created today
        tasks_created_today = self.db.exec(
            select(func.count(Task.id))
            .where(
                and_(
                    Task.user_id == user_id,
                    Task.created_at >= today_start
                )
            )
        ).one()

        # Tasks completed today
        tasks_completed_today = self.db.exec(
            select(func.count(Task.id))
            .where(
                and_(
                    Task.user_id == user_id,
                    Task.completed == True,
                    Task.updated_at >= today_start
                )
            )
        ).one()

        # Tasks created this week
        tasks_created_this_week = self.db.exec(
            select(func.count(Task.id))
            .where(
                and_(
                    Task.user_id == user_id,
                    Task.created_at >= week_start
                )
            )
        ).one()

        # Tasks completed this week
        tasks_completed_this_week = self.db.exec(
            select(func.count(Task.id))
            .where(
                and_(
                    Task.user_id == user_id,
                    Task.completed == True,
                    Task.updated_at >= week_start
                )
            )
        ).one()

        # Calculate completion rate
        total_tasks = self.db.exec(
            select(func.count(Task.id))
            .where(Task.user_id == user_id)
        ).one()

        completed_tasks = self.db.exec(
            select(func.count(Task.id))
            .where(
                and_(
                    Task.user_id == user_id,
                    Task.completed == True
                )
            )
        ).one()

        completion_rate = (
            (completed_tasks / total_tasks * 100.0)
            if total_tasks > 0
            else 0.0
        )

        return ActivityMetrics(
            tasks_created_today=tasks_created_today,
            tasks_completed_today=tasks_completed_today,
            tasks_created_this_week=tasks_created_this_week,
            tasks_completed_this_week=tasks_completed_this_week,
            completion_rate=round(completion_rate, 1)
        )

    def get_task_breakdown_by_status(self, user_id: str) -> dict:
        """
        Get task breakdown by completion status.

        Args:
            user_id: User identifier

        Returns:
            dict: Task counts by status
        """
        stats = self.get_task_statistics(user_id)

        return {
            "pending": stats.pending_tasks,
            "completed": stats.completed_tasks,
            "total": stats.total_tasks
        }

    def get_shared_task_details(self, user_id: str) -> dict:
        """
        Get details about shared tasks.

        Args:
            user_id: User identifier

        Returns:
            dict: Shared task details including count and permissions
        """
        # Count tasks shared with user (view permission)
        view_only = self.db.exec(
            select(func.count(TaskShare.id))
            .where(
                and_(
                    TaskShare.shared_with_user_id == user_id,
                    TaskShare.permission == "view"
                )
            )
        ).one()

        # Count tasks shared with user (edit permission)
        can_edit = self.db.exec(
            select(func.count(TaskShare.id))
            .where(
                and_(
                    TaskShare.shared_with_user_id == user_id,
                    TaskShare.permission == "edit"
                )
            )
        ).one()

        return {
            "total_shared": view_only + can_edit,
            "view_only": view_only,
            "can_edit": can_edit
        }


def get_dashboard_service(db: Session = Depends(get_db)) -> DashboardService:
    """
    Factory function to create dashboard service instance.

    This function provides a convenient way to instantiate the dashboard
    service with a database session via FastAPI dependency injection.

    Args:
        db: SQLModel database session (injected by FastAPI)

    Returns:
        DashboardService: Dashboard service instance

    Example:
        ```python
        from fastapi import Depends
        from app.database.session import get_db

        @app.get("/api/dashboard/statistics")
        def get_statistics(
            current_user: User = Depends(get_current_user),
            service: DashboardService = Depends(get_dashboard_service)
        ):
            stats = service.get_task_statistics(current_user.id)
            return stats
        ```
    """
    return DashboardService(db)
