"""
Database connection and session management for Neon Serverless PostgreSQL.

This module provides:
- SQLModel engine configuration with connection pooling
- Session factory for database operations
- FastAPI dependency function for dependency injection
- Proper async-compatible connection handling
"""

from typing import Generator
from sqlmodel import Session, create_engine
from sqlalchemy.pool import QueuePool
from app.config import settings


# Create SQLModel engine with connection pooling
# Connection pooling configuration:
# - pool_size: Maximum number of connections to maintain (5 for serverless)
# - pool_recycle: Recycle connections after 3600 seconds (1 hour) to prevent stale connections
# - poolclass: QueuePool for thread-safe connection pooling
# - echo: Log SQL statements (enabled in development via DATABASE_ECHO env var)

# Determine if using PostgreSQL or SQLite
is_postgres = settings.DATABASE_URL.startswith("postgresql://") or settings.DATABASE_URL.startswith("postgresql+psycopg://")

# Configure engine based on database type
if is_postgres:
    # PostgreSQL-specific configuration for Neon Serverless
    # Note: psycopg3 (postgresql+psycopg://) uses different connection parameters than psycopg2
    if settings.DATABASE_URL.startswith("postgresql+psycopg://"):
        # psycopg3 driver configuration
        engine = create_engine(
            settings.DATABASE_URL,
            echo=settings.DATABASE_ECHO,
            pool_size=settings.DATABASE_POOL_SIZE,
            pool_recycle=settings.DATABASE_POOL_RECYCLE,
            poolclass=QueuePool,
            pool_pre_ping=True,  # Verify connections before using them
            # psycopg3 uses connection string parameters, not connect_args
        )
    else:
        # psycopg2 driver configuration (legacy)
        engine = create_engine(
            settings.DATABASE_URL,
            echo=settings.DATABASE_ECHO,
            pool_size=settings.DATABASE_POOL_SIZE,
            pool_recycle=settings.DATABASE_POOL_RECYCLE,
            poolclass=QueuePool,
            pool_pre_ping=True,  # Verify connections before using them
            connect_args={
                "sslmode": "require",  # Neon requires SSL connections
                "connect_timeout": 10,  # Connection timeout in seconds
            }
        )
else:
    # SQLite configuration (for local development/testing)
    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DATABASE_ECHO,
        connect_args={"check_same_thread": False}  # Allow SQLite to work with FastAPI
    )


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency function that provides database sessions.

    This function creates a new SQLModel session for each request and ensures
    proper cleanup after the request completes. It follows the dependency
    injection pattern recommended by FastAPI.

    Usage in FastAPI routes:
        @app.get("/api/tasks")
        def get_tasks(db: Session = Depends(get_db)):
            # Use db session here
            pass

    Yields:
        Session: SQLModel database session

    Example:
        ```python
        from fastapi import Depends
        from sqlmodel import Session, select
        from app.database import get_db
        from app.models import Task

        @app.get("/tasks")
        def list_tasks(db: Session = Depends(get_db)):
            statement = select(Task)
            tasks = db.exec(statement).all()
            return tasks
        ```
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
        session.close()


def init_db() -> None:
    """
    Initialize the database by creating all tables.

    This function should be called during application startup to ensure
    all database tables are created. It uses SQLModel's metadata to
    create tables based on the defined models.

    Note: This is a simple approach suitable for development. For production,
    consider using a migration tool like Alembic for schema versioning.
    """
    from sqlmodel import SQLModel
    from app.models import Task  # Import all models to register them

    # Create all tables defined in SQLModel models
    SQLModel.metadata.create_all(engine)


def close_db() -> None:
    """
    Close all database connections and dispose of the connection pool.

    This function should be called during application shutdown to ensure
    graceful cleanup of database resources.
    """
    engine.dispose()
