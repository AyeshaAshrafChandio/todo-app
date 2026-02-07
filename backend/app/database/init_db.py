"""
Database initialization script for creating tables and seeding initial data.

This module provides functions to initialize the database schema and optionally
seed it with initial data. It should be called during application startup or
via CLI commands.
"""

from sqlmodel import SQLModel
from app.database.connection import engine
from app.database.session import get_db_context


def create_db_and_tables() -> None:
    """
    Create all database tables based on SQLModel models.

    This function uses SQLModel's metadata to create all tables defined
    in the application models. It's idempotent - running it multiple times
    won't cause errors if tables already exist.

    Note:
        - This is suitable for development and testing
        - For production, use Alembic migrations instead
        - All models must be imported before calling this function
        - Tables are created based on SQLModel.metadata

    Usage:
        ```python
        from app.database.init_db import create_db_and_tables

        # During application startup
        create_db_and_tables()
        ```

    Example in main.py:
        ```python
        @app.on_event("startup")
        async def startup_event():
            create_db_and_tables()
        ```
    """
    # Import all models to ensure they are registered with SQLModel metadata
    # This is critical for create_all to detect all tables
    from app.models.task import Task
    # Import additional models as they are created:
    # from app.models.conversation import Conversation
    # from app.models.message import Message
    # from app.models.team import Team
    # from app.models.team_member import TeamMember
    # from app.models.task_share import TaskShare

    # Create all tables defined in SQLModel models
    SQLModel.metadata.create_all(engine)
    print("✓ Database tables created successfully")


def drop_db_and_tables() -> None:
    """
    Drop all database tables.

    WARNING: This function will delete all data in the database.
    Use with extreme caution and only in development/testing environments.

    Usage:
        ```python
        from app.database.init_db import drop_db_and_tables

        # Only in development/testing!
        drop_db_and_tables()
        ```
    """
    SQLModel.metadata.drop_all(engine)
    print("✓ Database tables dropped successfully")


def reset_database() -> None:
    """
    Reset the database by dropping and recreating all tables.

    WARNING: This function will delete all data in the database.
    Use only in development/testing environments.

    Usage:
        ```python
        from app.database.init_db import reset_database

        # Only in development/testing!
        reset_database()
        ```
    """
    print("⚠ Resetting database (all data will be lost)...")
    drop_db_and_tables()
    create_db_and_tables()
    print("✓ Database reset complete")


def init_db() -> None:
    """
    Initialize the database with tables and optional seed data.

    This is the main initialization function that should be called
    during application startup or via CLI commands. It creates tables
    and can optionally seed initial data.

    Usage:
        ```python
        from app.database.init_db import init_db

        # During application startup
        init_db()
        ```

    Note:
        - Safe to call multiple times (idempotent)
        - Creates tables if they don't exist
        - Does not drop existing tables or data
        - For seeding data, call seed_data() separately
    """
    print("Initializing database...")
    create_db_and_tables()
    print("✓ Database initialization complete")


def verify_connection() -> bool:
    """
    Verify that the database connection is working.

    This function attempts to connect to the database and execute
    a simple query to verify connectivity.

    Returns:
        bool: True if connection is successful, False otherwise

    Usage:
        ```python
        from app.database.init_db import verify_connection

        if verify_connection():
            print("Database connection OK")
        else:
            print("Database connection failed")
        ```
    """
    try:
        with get_db_context() as db:
            # Execute a simple query to verify connection
            db.exec("SELECT 1")
        print("✓ Database connection verified")
        return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False


if __name__ == "__main__":
    """
    CLI entry point for database initialization.

    Usage:
        python -m app.database.init_db
    """
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "create":
            create_db_and_tables()
        elif command == "drop":
            drop_db_and_tables()
        elif command == "reset":
            reset_database()
        elif command == "verify":
            verify_connection()
        else:
            print(f"Unknown command: {command}")
            print("Available commands: create, drop, reset, verify")
            sys.exit(1)
    else:
        # Default: initialize database
        init_db()
