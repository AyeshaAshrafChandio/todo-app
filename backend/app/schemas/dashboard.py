"""
Dashboard schemas for task statistics and analytics.

This module defines Pydantic schemas for dashboard-related API endpoints,
including task statistics, activity metrics, and dashboard data responses.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class TaskStatistics(BaseModel):
    """
    Task statistics for dashboard display.

    This schema represents aggregated task counts for a user, providing
    a quick overview of their task management status.

    Attributes:
        total_tasks: Total number of tasks owned by the user
        pending_tasks: Number of incomplete tasks
        completed_tasks: Number of completed tasks
        shared_tasks: Number of tasks shared with the user by others

    Example:
        ```json
        {
            "total_tasks": 15,
            "pending_tasks": 8,
            "completed_tasks": 7,
            "shared_tasks": 3
        }
        ```
    """

    total_tasks: int = Field(
        ge=0,
        description="Total number of tasks owned by the user"
    )

    pending_tasks: int = Field(
        ge=0,
        description="Number of incomplete tasks"
    )

    completed_tasks: int = Field(
        ge=0,
        description="Number of completed tasks"
    )

    shared_tasks: int = Field(
        ge=0,
        description="Number of tasks shared with the user by others"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_tasks": 15,
                "pending_tasks": 8,
                "completed_tasks": 7,
                "shared_tasks": 3
            }
        }
    )


class DashboardStatisticsResponse(BaseModel):
    """
    Complete dashboard statistics response.

    This schema wraps task statistics with metadata about when the
    statistics were computed and cached.

    Attributes:
        statistics: Task statistics data
        computed_at: Timestamp when statistics were computed (UTC)
        cached: Whether the response was served from cache

    Example:
        ```json
        {
            "statistics": {
                "total_tasks": 15,
                "pending_tasks": 8,
                "completed_tasks": 7,
                "shared_tasks": 3
            },
            "computed_at": "2026-02-07T20:30:00Z",
            "cached": false
        }
        ```
    """

    statistics: TaskStatistics = Field(
        description="Task statistics data"
    )

    computed_at: datetime = Field(
        description="Timestamp when statistics were computed (UTC)"
    )

    cached: bool = Field(
        default=False,
        description="Whether the response was served from cache"
    )

    model_config = ConfigDict(
        json_schema_extra={
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
    )


class ActivityMetrics(BaseModel):
    """
    User activity metrics for dashboard analytics.

    This schema provides insights into user activity patterns,
    including task creation and completion rates.

    Attributes:
        tasks_created_today: Number of tasks created today
        tasks_completed_today: Number of tasks completed today
        tasks_created_this_week: Number of tasks created this week
        tasks_completed_this_week: Number of tasks completed this week
        completion_rate: Percentage of tasks completed (0-100)

    Example:
        ```json
        {
            "tasks_created_today": 2,
            "tasks_completed_today": 3,
            "tasks_created_this_week": 8,
            "tasks_completed_this_week": 12,
            "completion_rate": 60.5
        }
        ```
    """

    tasks_created_today: int = Field(
        ge=0,
        description="Number of tasks created today"
    )

    tasks_completed_today: int = Field(
        ge=0,
        description="Number of tasks completed today"
    )

    tasks_created_this_week: int = Field(
        ge=0,
        description="Number of tasks created this week"
    )

    tasks_completed_this_week: int = Field(
        ge=0,
        description="Number of tasks completed this week"
    )

    completion_rate: float = Field(
        ge=0.0,
        le=100.0,
        description="Percentage of tasks completed (0-100)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "tasks_created_today": 2,
                "tasks_completed_today": 3,
                "tasks_created_this_week": 8,
                "tasks_completed_this_week": 12,
                "completion_rate": 60.5
            }
        }
    )


class DashboardError(BaseModel):
    """
    Error response for dashboard API endpoints.

    Attributes:
        error: Error message
        detail: Optional detailed error information
        code: Optional error code

    Example:
        ```json
        {
            "error": "Unauthorized",
            "detail": "Invalid or expired authentication token",
            "code": "AUTH_INVALID_TOKEN"
        }
        ```
    """

    error: str = Field(
        description="Error message"
    )

    detail: Optional[str] = Field(
        default=None,
        description="Optional detailed error information"
    )

    code: Optional[str] = Field(
        default=None,
        description="Optional error code"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error": "Unauthorized",
                "detail": "Invalid or expired authentication token",
                "code": "AUTH_INVALID_TOKEN"
            }
        }
    )
