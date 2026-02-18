"""
Performance monitoring middleware for database queries and API endpoints.

This module provides middleware to track and log:
- Database query execution time
- API endpoint response times
- Slow query detection and logging
- Database connection pool usage

All performance metrics are logged for analysis and optimization.
"""

import time
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy import event
from sqlalchemy.engine import Engine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Performance thresholds (in seconds)
SLOW_QUERY_THRESHOLD = 0.1  # 100ms
SLOW_ENDPOINT_THRESHOLD = 1.0  # 1 second


class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """
    Middleware to monitor API endpoint performance.

    Tracks response time for each request and logs slow endpoints.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and measure response time.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/route handler

        Returns:
            Response: HTTP response with performance headers
        """
        # Record start time
        start_time = time.time()

        # Process request
        response = await call_next(request)

        # Calculate response time
        response_time = time.time() - start_time

        # Add performance header
        response.headers["X-Response-Time"] = f"{response_time:.3f}s"

        # Log slow endpoints
        if response_time > SLOW_ENDPOINT_THRESHOLD:
            logger.warning(
                f"Slow endpoint detected: {request.method} {request.url.path} "
                f"took {response_time:.3f}s (threshold: {SLOW_ENDPOINT_THRESHOLD}s)"
            )

        # Log all requests in debug mode
        logger.info(
            f"{request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Time: {response_time:.3f}s"
        )

        return response


class DatabaseQueryMonitor:
    """
    Monitor database query performance using SQLAlchemy events.

    Tracks query execution time and logs slow queries.
    """

    def __init__(self):
        """Initialize query monitor."""
        self.query_count = 0
        self.total_query_time = 0.0
        self.slow_queries = []

    def setup_monitoring(self, engine: Engine) -> None:
        """
        Setup SQLAlchemy event listeners for query monitoring.

        Args:
            engine: SQLAlchemy engine instance
        """
        @event.listens_for(engine, "before_cursor_execute")
        def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            """Record query start time."""
            conn.info.setdefault("query_start_time", []).append(time.time())

        @event.listens_for(engine, "after_cursor_execute")
        def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            """Calculate and log query execution time."""
            # Get start time
            query_start_times = conn.info.get("query_start_time", [])
            if not query_start_times:
                return

            start_time = query_start_times.pop()
            execution_time = time.time() - start_time

            # Update statistics
            self.query_count += 1
            self.total_query_time += execution_time

            # Log slow queries
            if execution_time > SLOW_QUERY_THRESHOLD:
                logger.warning(
                    f"Slow query detected (took {execution_time:.3f}s):\n"
                    f"{statement}\n"
                    f"Parameters: {parameters}"
                )

                # Store slow query for analysis
                self.slow_queries.append({
                    "statement": statement,
                    "parameters": parameters,
                    "execution_time": execution_time,
                    "timestamp": time.time()
                })

                # Keep only last 100 slow queries
                if len(self.slow_queries) > 100:
                    self.slow_queries.pop(0)

            # Log all queries in debug mode
            logger.debug(
                f"Query executed in {execution_time:.3f}s: "
                f"{statement[:100]}..."
            )

    def get_statistics(self) -> dict:
        """
        Get query performance statistics.

        Returns:
            dict: Performance statistics including query count, average time, slow queries
        """
        avg_query_time = (
            self.total_query_time / self.query_count
            if self.query_count > 0
            else 0.0
        )

        return {
            "total_queries": self.query_count,
            "total_query_time": self.total_query_time,
            "average_query_time": avg_query_time,
            "slow_queries_count": len(self.slow_queries),
            "slow_query_threshold": SLOW_QUERY_THRESHOLD
        }

    def get_slow_queries(self, limit: int = 10) -> list:
        """
        Get recent slow queries.

        Args:
            limit: Maximum number of slow queries to return

        Returns:
            list: Recent slow queries sorted by execution time
        """
        # Sort by execution time (slowest first)
        sorted_queries = sorted(
            self.slow_queries,
            key=lambda q: q["execution_time"],
            reverse=True
        )

        return sorted_queries[:limit]

    def reset_statistics(self) -> None:
        """Reset all performance statistics."""
        self.query_count = 0
        self.total_query_time = 0.0
        self.slow_queries = []


# Global query monitor instance
query_monitor = DatabaseQueryMonitor()


def setup_performance_monitoring(engine: Engine) -> None:
    """
    Setup performance monitoring for the application.

    This function should be called during application startup to enable
    query performance monitoring.

    Args:
        engine: SQLAlchemy engine instance

    Example:
        ```python
        from app.database.connection import engine
        from app.middleware.performance import setup_performance_monitoring

        setup_performance_monitoring(engine)
        ```
    """
    query_monitor.setup_monitoring(engine)
    logger.info("Performance monitoring enabled")


def get_performance_statistics() -> dict:
    """
    Get current performance statistics.

    Returns:
        dict: Performance statistics for queries and endpoints
    """
    return query_monitor.get_statistics()


def get_slow_queries(limit: int = 10) -> list:
    """
    Get recent slow queries.

    Args:
        limit: Maximum number of slow queries to return

    Returns:
        list: Recent slow queries
    """
    return query_monitor.get_slow_queries(limit)
