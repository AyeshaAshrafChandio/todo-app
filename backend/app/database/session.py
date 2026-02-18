"""
Database session management and dependency injection for FastAPI.

This module provides session management utilities for database operations,
including the FastAPI dependency function for dependency injection pattern.
"""

from typing import Generator
from contextlib import contextmanager
from sqlmodel import Session
from app.database.connection import engine


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency function that provides database sessions.

    This function creates a new SQLModel session for each request and ensures
    proper cleanup after the request completes. It follows the dependency
    injection pattern recommended by FastAPI.

    The session lifecycle:
    1. Create new session from engine
    2. Yield session to route handler
    3. Commit transaction if successful
    4. Rollback transaction if error occurs
    5. Always close session to release connection

    Usage in FastAPI routes:
        ```python
        from fastapi import Depends
        from sqlmodel import Session, select
        from app.database.session import get_db
        from app.models.task import Task

        @app.get("/api/tasks")
        def get_tasks(db: Session = Depends(get_db)):
            statement = select(Task)
            tasks = db.exec(statement).all()
            return tasks
        ```

    Yields:
        Session: SQLModel database session

    Note:
        - Each request gets its own session
        - Sessions are automatically committed on success
        - Sessions are automatically rolled back on error
        - Connections are returned to pool (or closed for NullPool) after use
        - This pattern ensures proper transaction management and resource cleanup
    """
    # Create a new session for this request
    session = Session(engine)
    try:
        # Yield the session to the route handler
        yield session
        # Commit any pending transactions if the request was successful
        session.commit()
    except Exception:
        # Rollback the transaction if an error occurred
        session.rollback()
        raise
    finally:
        # Always close the session to return the connection to the pool
        # For NullPool (Neon Serverless), this closes the connection immediately
        session.close()


from contextlib import contextmanager


@contextmanager
def get_db_context():
    """
    Context manager for database sessions outside of FastAPI routes.

    This function provides a context manager for database operations that
    occur outside of FastAPI request handlers (e.g., background tasks,
    CLI scripts, database initialization).

    Usage:
        ```python
        from app.database.session import get_db_context
        from app.models.task import Task

        with get_db_context() as db:
            task = Task(title="Example", user_id="user123")
            db.add(task)
            db.commit()
        ```

    Returns:
        Session: SQLModel database session (via context manager)

    Note:
        - Use this for non-request operations (scripts, background tasks)
        - Use get_db() for FastAPI route handlers
        - Session is automatically committed and closed on context exit
    """
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
