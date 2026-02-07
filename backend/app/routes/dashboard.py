"""
Dashboard API routes for task statistics and analytics.

This module provides REST API endpoints for dashboard-related operations,
including task statistics, activity metrics, and dashboard data retrieval.

All endpoints require JWT authentication and filter data by authenticated user.
"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.database.session import get_db
from app.services.dashboard_service import DashboardService, get_dashboard_service
from app.schemas.dashboard import (
    TaskStatistics,
    DashboardStatisticsResponse,
    ActivityMetrics,
    DashboardError
)
from app.middleware.auth import get_current_user
from app.middleware.authorization import get_authenticated_user
from app.models.user import User


# Create router for dashboard endpoints
router = APIRouter(
    prefix="/api/dashboard",
    tags=["dashboard"],
    responses={
        401: {
            "model": DashboardError,
            "description": "Unauthorized - Invalid or missing authentication token"
        },
        500: {
            "model": DashboardError,
            "description": "Internal Server Error"
        }
    }
)


@router.get(
    "/statistics",
    response_model=DashboardStatisticsResponse,
    summary="Get task statistics",
    description="""
    Get aggregated task statistics for the authenticated user.

    Returns:
    - Total tasks owned by the user
    - Pending (incomplete) tasks
    - Completed tasks
    - Tasks shared with the user by others

    The response includes metadata about when the statistics were computed
    and whether the response was served from cache.

    Authentication: Required (JWT token in Authorization header)

    Performance: Optimized with COUNT queries and database indexes.
    Expected response time: <50ms for typical datasets.
    """,
    responses={
        200: {
            "description": "Task statistics retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "statistics": {
                            "total_tasks": 15,
                            "pending_tasks": 8,
                            "completed_tasks": 7,
                            "shared_tasks": 3
                        },
                        "computed_at": "2026-02-07T20:30:00Z",
                        "cached": False
                    }
                }
            }
        }
    }
)
async def get_statistics(
    current_user: User = Depends(get_authenticated_user),
    service: DashboardService = Depends(get_dashboard_service)
) -> DashboardStatisticsResponse:
    """
    Get task statistics for the authenticated user.

    This endpoint computes and returns aggregated task counts for the
    authenticated user. All data is filtered by user_id to ensure
    data isolation and security.

    Args:
        current_user: Authenticated user (injected by auth middleware)
        db: Database session (injected by dependency)
        service: Dashboard service instance (injected by dependency)

    Returns:
        DashboardStatisticsResponse: Task statistics with metadata

    Raises:
        HTTPException: 401 if authentication fails
        HTTPException: 500 if database error occurs

    Example:
        ```bash
        curl -H "Authorization: Bearer <token>" \\
             http://localhost:8000/api/dashboard/statistics
        ```
    """
    try:
        # Compute task statistics for authenticated user
        statistics = service.get_task_statistics(current_user.id)

        # Return response with metadata
        return DashboardStatisticsResponse(
            statistics=statistics,
            computed_at=datetime.utcnow(),
            cached=False
        )

    except Exception as e:
        # Log error (in production, use proper logging)
        print(f"Error computing dashboard statistics: {e}")

        # Return 500 error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal Server Error",
                "detail": "Failed to compute dashboard statistics",
                "code": "DASHBOARD_COMPUTE_ERROR"
            }
        )


@router.get(
    "/activity",
    response_model=ActivityMetrics,
    summary="Get activity metrics",
    description="""
    Get user activity metrics including task creation and completion rates.

    Returns:
    - Tasks created today
    - Tasks completed today
    - Tasks created this week
    - Tasks completed this week
    - Overall completion rate (percentage)

    Authentication: Required (JWT token in Authorization header)

    Performance: Optimized with COUNT queries and date filtering.
    Expected response time: <100ms for typical datasets.
    """,
    responses={
        200: {
            "description": "Activity metrics retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "tasks_created_today": 2,
                        "tasks_completed_today": 3,
                        "tasks_created_this_week": 8,
                        "tasks_completed_this_week": 12,
                        "completion_rate": 60.5
                    }
                }
            }
        }
    }
)
async def get_activity(
    current_user: User = Depends(get_authenticated_user),
    service: DashboardService = Depends(get_dashboard_service)
) -> ActivityMetrics:
    """
    Get activity metrics for the authenticated user.

    This endpoint computes and returns activity-based metrics including
    task creation and completion rates over different time periods.

    Args:
        current_user: Authenticated user (injected by auth middleware)
        db: Database session (injected by dependency)
        service: Dashboard service instance (injected by dependency)

    Returns:
        ActivityMetrics: User activity metrics

    Raises:
        HTTPException: 401 if authentication fails
        HTTPException: 500 if database error occurs

    Example:
        ```bash
        curl -H "Authorization: Bearer <token>" \\
             http://localhost:8000/api/dashboard/activity
        ```
    """
    try:
        # Compute activity metrics for authenticated user
        metrics = service.get_activity_metrics(current_user.id)

        return metrics

    except Exception as e:
        # Log error (in production, use proper logging)
        print(f"Error computing activity metrics: {e}")

        # Return 500 error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal Server Error",
                "detail": "Failed to compute activity metrics",
                "code": "ACTIVITY_COMPUTE_ERROR"
            }
        )


@router.get(
    "/breakdown",
    summary="Get task breakdown by status",
    description="""
    Get task breakdown by completion status.

    Returns a simple breakdown of tasks by status (pending, completed, total).

    Authentication: Required (JWT token in Authorization header)
    """,
    responses={
        200: {
            "description": "Task breakdown retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "pending": 8,
                        "completed": 7,
                        "total": 15
                    }
                }
            }
        }
    }
)
async def get_breakdown(
    current_user: User = Depends(get_authenticated_user),
    service: DashboardService = Depends(get_dashboard_service)
) -> dict:
    """
    Get task breakdown by status for the authenticated user.

    Args:
        current_user: Authenticated user (injected by auth middleware)
        db: Database session (injected by dependency)
        service: Dashboard service instance (injected by dependency)

    Returns:
        dict: Task counts by status

    Raises:
        HTTPException: 401 if authentication fails
        HTTPException: 500 if database error occurs
    """
    try:
        breakdown = service.get_task_breakdown_by_status(current_user.id)
        return breakdown

    except Exception as e:
        print(f"Error computing task breakdown: {e}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal Server Error",
                "detail": "Failed to compute task breakdown",
                "code": "BREAKDOWN_COMPUTE_ERROR"
            }
        )


@router.get(
    "/shared",
    summary="Get shared task details",
    description="""
    Get details about tasks shared with the authenticated user.

    Returns:
    - Total shared tasks
    - View-only shared tasks
    - Editable shared tasks

    Authentication: Required (JWT token in Authorization header)
    """,
    responses={
        200: {
            "description": "Shared task details retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "total_shared": 5,
                        "view_only": 3,
                        "can_edit": 2
                    }
                }
            }
        }
    }
)
async def get_shared_details(
    current_user: User = Depends(get_authenticated_user),
    service: DashboardService = Depends(get_dashboard_service)
) -> dict:
    """
    Get shared task details for the authenticated user.

    Args:
        current_user: Authenticated user (injected by auth middleware)
        db: Database session (injected by dependency)
        service: Dashboard service instance (injected by dependency)

    Returns:
        dict: Shared task details

    Raises:
        HTTPException: 401 if authentication fails
        HTTPException: 500 if database error occurs
    """
    try:
        details = service.get_shared_task_details(current_user.id)
        return details

    except Exception as e:
        print(f"Error computing shared task details: {e}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal Server Error",
                "detail": "Failed to compute shared task details",
                "code": "SHARED_DETAILS_ERROR"
            }
        )


@router.get(
    "/health",
    summary="Dashboard API health check",
    description="Check if the dashboard API is operational",
    responses={
        200: {
            "description": "Dashboard API is healthy",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "timestamp": "2026-02-07T20:30:00Z"
                    }
                }
            }
        }
    }
)
async def health_check() -> dict:
    """
    Health check endpoint for dashboard API.

    This endpoint does not require authentication and can be used
    for monitoring and health checks.

    Returns:
        dict: Health status
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }
