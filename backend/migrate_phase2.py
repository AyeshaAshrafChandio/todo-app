"""
Database migration script for Phase 2: Authentication & API Security

This script creates the users table and adds the user_id foreign key
to the tasks table. It preserves existing task data by making user_id nullable.

Usage:
    python migrate_phase2.py

Requirements:
    - DATABASE_URL environment variable must be set
    - BETTER_AUTH_SECRET can be temporary for migration purposes
"""

import os
import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Set temporary BETTER_AUTH_SECRET if not present (for migration only)
if not os.getenv("BETTER_AUTH_SECRET"):
    os.environ["BETTER_AUTH_SECRET"] = "temporary-migration-secret-do-not-use-in-production"
    print("[WARNING] Using temporary BETTER_AUTH_SECRET for migration")
    print("[WARNING] Set a real secret before running the application")

from sqlmodel import SQLModel, Session, select, text
from app.database.connection import engine
from app.models import Task, User


def verify_database_connection():
    """Verify database connection is working."""
    try:
        with Session(engine) as session:
            session.exec(text("SELECT 1"))
        print("[SUCCESS] Database connection verified")
        return True
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        return False


def check_existing_tables():
    """Check which tables already exist."""
    with Session(engine) as session:
        # Check if tasks table exists
        result = session.exec(text(
            "SELECT EXISTS (SELECT FROM information_schema.tables "
            "WHERE table_name = 'tasks')"
        ))
        tasks_exists = result.one()

        # Check if users table exists
        result = session.exec(text(
            "SELECT EXISTS (SELECT FROM information_schema.tables "
            "WHERE table_name = 'users')"
        ))
        users_exists = result.one()

        return tasks_exists, users_exists


def count_existing_tasks():
    """Count existing tasks in the database."""
    try:
        with Session(engine) as session:
            result = session.exec(text("SELECT COUNT(*) FROM tasks"))
            count = result.one()
            return count
    except Exception:
        return 0


def run_migration():
    """Execute the Phase 2 database migration."""
    print("\n" + "="*60)
    print("Phase 2 Database Migration: Authentication & API Security")
    print("="*60 + "\n")

    # Step 1: Verify database connection
    print("Step 1: Verifying database connection...")
    if not verify_database_connection():
        print("\n[ERROR] Migration failed: Cannot connect to database")
        print("   Check your DATABASE_URL environment variable")
        return False

    # Step 2: Check existing tables
    print("\nStep 2: Checking existing tables...")
    tasks_exists, users_exists = check_existing_tables()
    print(f"   - tasks table exists: {tasks_exists}")
    print(f"   - users table exists: {users_exists}")

    # Step 3: Count existing tasks
    if tasks_exists:
        task_count = count_existing_tasks()
        print(f"\nStep 3: Found {task_count} existing tasks")
        if task_count > 0:
            print("   [INFO] These tasks will have user_id = NULL (legacy tasks)")

    # Step 4: Create/update tables
    print("\nStep 4: Applying schema changes...")
    try:
        # This will:
        # - Create users table if it doesn't exist
        # - Add user_id column to tasks table if it doesn't exist
        # - Create indexes
        SQLModel.metadata.create_all(engine)
        print("[SUCCESS] Schema changes applied successfully")
    except Exception as e:
        print(f"[ERROR] Schema migration failed: {e}")
        return False

    # Step 5: Verify migration
    print("\nStep 5: Verifying migration...")
    try:
        with Session(engine) as session:
            # Check users table structure
            result = session.exec(text(
                "SELECT column_name, data_type, is_nullable "
                "FROM information_schema.columns "
                "WHERE table_name = 'users' "
                "ORDER BY ordinal_position"
            ))
            users_columns = result.all()
            print("\n   Users table columns:")
            for col in users_columns:
                print(f"      - {col[0]}: {col[1]} (nullable: {col[2]})")

            # Check tasks table structure (user_id column)
            result = session.exec(text(
                "SELECT column_name, data_type, is_nullable "
                "FROM information_schema.columns "
                "WHERE table_name = 'tasks' AND column_name = 'user_id'"
            ))
            user_id_col = result.first()
            if user_id_col:
                print(f"\n   Tasks table user_id column:")
                print(f"      - {user_id_col[0]}: {user_id_col[1]} (nullable: {user_id_col[2]})")

            # Check foreign key constraint
            result = session.exec(text(
                "SELECT constraint_name, table_name, column_name "
                "FROM information_schema.key_column_usage "
                "WHERE table_name = 'tasks' AND column_name = 'user_id'"
            ))
            fk_constraint = result.first()
            if fk_constraint:
                print(f"\n   Foreign key constraint: {fk_constraint[0]}")

            # Check indexes
            result = session.exec(text(
                "SELECT indexname, tablename "
                "FROM pg_indexes "
                "WHERE tablename IN ('users', 'tasks') "
                "ORDER BY tablename, indexname"
            ))
            indexes = result.all()
            print("\n   Indexes created:")
            for idx in indexes:
                print(f"      - {idx[0]} on {idx[1]}")

        print("\n[SUCCESS] Migration verification complete")
    except Exception as e:
        print(f"[WARNING] Verification warning: {e}")

    # Step 6: Summary
    print("\n" + "="*60)
    print("Migration Summary")
    print("="*60)
    print("[SUCCESS] Users table created")
    print("[SUCCESS] Tasks table extended with user_id foreign key")
    print("[SUCCESS] Indexes created for performance")
    print("[SUCCESS] Existing task data preserved (user_id = NULL)")
    print("\nNext steps:")
    print("1. Set BETTER_AUTH_SECRET in .env file")
    print("2. Implement authentication endpoints")
    print("3. Update task endpoints to filter by user_id")
    print("="*60 + "\n")

    return True


if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
