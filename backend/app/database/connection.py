"""
Database connection and session management for Neon Serverless PostgreSQL.

This module provides:
- SQLModel engine configuration with connection pooling
- Session factory for database operations
- FastAPI dependency function for dependency injection
- Proper async-compatible connection handling
- Robust error handling with retry logic
- Connection failure recovery
"""

import time
import logging
from typing import Generator, Optional
from sqlmodel import Session, create_engine
from sqlalchemy import text
from sqlalchemy.pool import NullPool, StaticPool
from sqlalchemy.exc import OperationalError, DatabaseError, DisconnectionError
from app.config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Connection retry configuration
MAX_RETRIES = 3
RETRY_DELAY = 1.0  # seconds
RETRY_BACKOFF = 2.0  # exponential backoff multiplier


# Create SQLModel engine with Neon Serverless optimized configuration
#
# Neon Serverless Connection Strategy:
# - NullPool: No connection pooling (Neon handles pooling at infrastructure level)
# - This prevents connection exhaustion in serverless environments
# - Each request gets a fresh connection that's immediately closed
# - Neon's built-in pooler (pgbouncer) handles actual connection pooling
#
# Connection string should include: ?sslmode=require&channel_binding=require
# For pooled connections, use Neon's pooler endpoint with ?pgbouncer=true

# Determine if using PostgreSQL or SQLite
is_postgres = settings.DATABASE_URL.startswith("postgresql://") or settings.DATABASE_URL.startswith("postgresql+psycopg://")

# Configure engine based on database type
if is_postgres:
    # Convert postgresql:// to postgresql+psycopg:// for psycopg3 driver
    # psycopg[binary] (psycopg3) is installed, not psycopg2
    database_url = settings.DATABASE_URL
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)

    # PostgreSQL-specific configuration for Neon Serverless
    # Use NullPool for serverless environments (no connection pooling)
    # Neon's infrastructure handles connection pooling via pgbouncer
    engine = create_engine(
        database_url,
        echo=settings.DATABASE_ECHO,
        poolclass=NullPool,  # No connection pooling for Neon Serverless
        # psycopg3 uses connection string parameters, not connect_args
        # SSL and timeout are specified in the connection string
    )
else:
    # SQLite configuration (for local development/testing)
    from sqlalchemy import event

    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DATABASE_ECHO,
        poolclass=StaticPool,  # Use StaticPool for SQLite in testing
        connect_args={"check_same_thread": False}  # Allow SQLite to work with FastAPI
    )

    # Enable foreign key constraints for SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency function that provides database sessions with error handling.

    This function creates a new SQLModel session for each request and ensures
    proper cleanup after the request completes. It includes retry logic for
    connection failures and proper error handling.

    Usage in FastAPI routes:
        @app.get("/api/tasks")
        def get_tasks(db: Session = Depends(get_db)):
            # Use db session here
            pass

    Yields:
        Session: SQLModel database session

    Raises:
        DatabaseConnectionError: If unable to establish database connection after retries
        DatabaseError: For other database-related errors

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
    session: Optional[Session] = None
    retry_count = 0

    while retry_count < MAX_RETRIES:
        try:
            # Create a new session for this request
            session = Session(engine)

            # Test the connection (SQLAlchemy 2.0 requires text() wrapper)
            session.execute(text("SELECT 1"))

            # Yield the session to the route handler
            yield session

            # Commit any pending transactions if the request was successful
            session.commit()
            break  # Success, exit retry loop

        except (OperationalError, DisconnectionError) as e:
            # Connection-related errors - retry with exponential backoff
            retry_count += 1

            if session:
                try:
                    session.rollback()
                except Exception:
                    pass  # Ignore rollback errors during connection failure

            if retry_count < MAX_RETRIES:
                delay = RETRY_DELAY * (RETRY_BACKOFF ** (retry_count - 1))
                logger.warning(
                    f"Database connection failed (attempt {retry_count}/{MAX_RETRIES}). "
                    f"Retrying in {delay}s... Error: {str(e)}"
                )
                time.sleep(delay)
            else:
                logger.error(
                    f"Database connection failed after {MAX_RETRIES} attempts. "
                    f"Error: {str(e)}"
                )
                raise DatabaseConnectionError(
                    f"Unable to connect to database after {MAX_RETRIES} attempts"
                ) from e

        except DatabaseError as e:
            # Database-level errors (constraint violations, etc.)
            if session:
                session.rollback()

            logger.error(f"Database error occurred: {str(e)}")
            raise

        except Exception as e:
            # Unexpected errors
            if session:
                try:
                    session.rollback()
                except Exception:
                    pass  # Ignore rollback errors

            logger.error(f"Unexpected error in database session: {str(e)}")
            raise

        finally:
            # Always close the session to return the connection to the pool
            if session:
                try:
                    session.close()
                except Exception as e:
                    logger.error(f"Error closing database session: {str(e)}")


def init_db() -> None:
    """
    Initialize the database by creating all tables with retry logic.

    This function should be called during application startup to ensure
    all database tables are created. It uses SQLModel's metadata to
    create tables based on the defined models.

    Includes retry logic for connection failures during startup.

    Note: This is a simple approach suitable for development. For production,
    consider using a migration tool like Alembic for schema versioning.

    Raises:
        DatabaseConnectionError: If unable to connect after retries
    """
    from sqlmodel import SQLModel
    from app.models import Task, User  # Import all models to register them

    retry_count = 0
    while retry_count < MAX_RETRIES:
        try:
            # Create all tables defined in SQLModel models
            SQLModel.metadata.create_all(engine)
            logger.info("Database tables created successfully")
            return

        except (OperationalError, DisconnectionError) as e:
            retry_count += 1

            if retry_count < MAX_RETRIES:
                delay = RETRY_DELAY * (RETRY_BACKOFF ** (retry_count - 1))
                logger.warning(
                    f"Failed to initialize database (attempt {retry_count}/{MAX_RETRIES}). "
                    f"Retrying in {delay}s... Error: {str(e)}"
                )
                time.sleep(delay)
            else:
                logger.error(
                    f"Failed to initialize database after {MAX_RETRIES} attempts. "
                    f"Error: {str(e)}"
                )
                raise DatabaseConnectionError(
                    f"Unable to initialize database after {MAX_RETRIES} attempts"
                ) from e

        except Exception as e:
            logger.error(f"Unexpected error during database initialization: {str(e)}")
            raise


def close_db() -> None:
    """
    Close all database connections and dispose of the connection pool.

    This function should be called during application shutdown to ensure
    graceful cleanup of database resources.
    """
    try:
        engine.dispose()
        logger.info("Database connections closed successfully")
    except Exception as e:
        logger.error(f"Error closing database connections: {str(e)}")
        # Don't raise - we're shutting down anyway


class DatabaseConnectionError(Exception):
    """
    Custom exception for database connection failures.

    Raised when unable to establish a database connection after multiple retries.
    """
    pass


def test_connection() -> bool:
    """
    Test database connection.

    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        with Session(engine) as session:
            session.execute(text("SELECT 1"))
        logger.info("Database connection test successful")
        return True
    except Exception as e:
        logger.error(f"Database connection test failed: {str(e)}")
        return False


def get_connection_info() -> dict:
    """
    Get database connection information (without sensitive data).

    Returns:
        dict: Connection information including pool status
    """
    try:
        # Get pool status
        pool = engine.pool
        pool_status = {
            "pool_class": pool.__class__.__name__,
            "size": getattr(pool, "size", lambda: "N/A")(),
            "checked_in": getattr(pool, "checkedin", lambda: "N/A")(),
            "checked_out": getattr(pool, "checkedout", lambda: "N/A")(),
            "overflow": getattr(pool, "overflow", lambda: "N/A")(),
        }

        return {
            "database_type": "PostgreSQL" if is_postgres else "SQLite",
            "pool_status": pool_status,
            "echo": settings.DATABASE_ECHO
        }
    except Exception as e:
        logger.error(f"Error getting connection info: {str(e)}")
        return {"error": str(e)}
