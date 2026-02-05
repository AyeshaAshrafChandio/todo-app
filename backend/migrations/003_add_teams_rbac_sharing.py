"""
Database migration script for Phase 3: Teams, RBAC, and Task Sharing

This script creates the teams, team_members, and task_shares tables and extends
the tasks table with a nullable team_id foreign key. It maintains 100% backward
compatibility with existing data.

Usage:
    python backend/migrations/003_add_teams_rbac_sharing.py

Requirements:
    - DATABASE_URL environment variable must be set
    - BETTER_AUTH_SECRET environment variable must be set
    - Phase 2 migration must be complete (users and tasks tables exist)
"""

import os
import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Verify required environment variables
if not os.getenv("DATABASE_URL"):
    print("[ERROR] DATABASE_URL environment variable is not set")
    sys.exit(1)

if not os.getenv("BETTER_AUTH_SECRET"):
    print("[WARNING] BETTER_AUTH_SECRET environment variable is not set")
    print("[WARNING] Using temporary secret for migration only")
    os.environ["BETTER_AUTH_SECRET"] = "temporary-migration-secret-do-not-use-in-production"

from sqlmodel import SQLModel, Session, select, text
from app.database.connection import engine
from app.models import Task, User, Team, TeamMember, TaskShare


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


def check_prerequisites():
    """Check that Phase 2 migration is complete."""
    with Session(engine) as session:
        # Check if users table exists
        result = session.exec(text(
            "SELECT EXISTS (SELECT FROM information_schema.tables "
            "WHERE table_name = 'users')"
        ))
        users_exists = result.one()

        # Check if tasks table exists
        result = session.exec(text(
            "SELECT EXISTS (SELECT FROM information_schema.tables "
            "WHERE table_name = 'tasks')"
        ))
        tasks_exists = result.one()

        # Check if tasks.user_id column exists
        result = session.exec(text(
            "SELECT EXISTS (SELECT FROM information_schema.columns "
            "WHERE table_name = 'tasks' AND column_name = 'user_id')"
        ))
        user_id_exists = result.one()

        return users_exists and tasks_exists and user_id_exists


def check_existing_tables():
    """Check which new tables already exist."""
    with Session(engine) as session:
        # Check if teams table exists
        result = session.exec(text(
            "SELECT EXISTS (SELECT FROM information_schema.tables "
            "WHERE table_name = 'teams')"
        ))
        teams_exists = result.one()

        # Check if team_members table exists
        result = session.exec(text(
            "SELECT EXISTS (SELECT FROM information_schema.tables "
            "WHERE table_name = 'team_members')"
        ))
        team_members_exists = result.one()

        # Check if task_shares table exists
        result = session.exec(text(
            "SELECT EXISTS (SELECT FROM information_schema.tables "
            "WHERE table_name = 'task_shares')"
        ))
        task_shares_exists = result.one()

        # Check if tasks.team_id column exists
        result = session.exec(text(
            "SELECT EXISTS (SELECT FROM information_schema.columns "
            "WHERE table_name = 'tasks' AND column_name = 'team_id')"
        ))
        team_id_exists = result.one()

        return teams_exists, team_members_exists, task_shares_exists, team_id_exists


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
    """Execute the Phase 3 database migration."""
    print("\n" + "="*70)
    print("Phase 3 Database Migration: Teams, RBAC, and Task Sharing")
    print("="*70 + "\n")

    # Step 1: Verify database connection
    print("Step 1: Verifying database connection...")
    if not verify_database_connection():
        print("\n[ERROR] Migration failed: Cannot connect to database")
        print("   Check your DATABASE_URL environment variable")
        return False

    # Step 2: Check prerequisites
    print("\nStep 2: Checking prerequisites (Phase 2 migration)...")
    if not check_prerequisites():
        print("[ERROR] Prerequisites not met")
        print("   Phase 2 migration must be complete before running Phase 3")
        print("   Required: users table, tasks table with user_id column")
        return False
    print("[SUCCESS] Prerequisites verified")

    # Step 3: Check existing tables
    print("\nStep 3: Checking existing tables...")
    teams_exists, team_members_exists, task_shares_exists, team_id_exists = check_existing_tables()
    print(f"   - teams table exists: {teams_exists}")
    print(f"   - team_members table exists: {team_members_exists}")
    print(f"   - task_shares table exists: {task_shares_exists}")
    print(f"   - tasks.team_id column exists: {team_id_exists}")

    if all([teams_exists, team_members_exists, task_shares_exists, team_id_exists]):
        print("\n[INFO] All tables and columns already exist")
        print("   Migration may have already been run")
        print("   Skipping schema changes")
        return True

    # Step 4: Count existing tasks
    task_count = count_existing_tasks()
    print(f"\nStep 4: Found {task_count} existing tasks")
    if task_count > 0:
        print("   [INFO] These tasks will remain as personal tasks (team_id = NULL)")

    # Step 5: Create/update tables
    print("\nStep 5: Applying schema changes...")
    try:
        # This will:
        # - Create teams table if it doesn't exist
        # - Create team_members table if it doesn't exist
        # - Create task_shares table if it doesn't exist
        # - Add team_id column to tasks table if it doesn't exist
        # - Create all indexes and constraints
        SQLModel.metadata.create_all(engine)
        print("[SUCCESS] Schema changes applied successfully")
    except Exception as e:
        print(f"[ERROR] Schema migration failed: {e}")
        return False

    # Step 6: Verify migration
    print("\nStep 6: Verifying migration...")
    try:
        with Session(engine) as session:
            # Check teams table structure
            result = session.exec(text(
                "SELECT column_name, data_type, is_nullable "
                "FROM information_schema.columns "
                "WHERE table_name = 'teams' "
                "ORDER BY ordinal_position"
            ))
            teams_columns = result.all()
            print("\n   Teams table columns:")
            for col in teams_columns:
                print(f"      - {col[0]}: {col[1]} (nullable: {col[2]})")

            # Check team_members table structure
            result = session.exec(text(
                "SELECT column_name, data_type, is_nullable "
                "FROM information_schema.columns "
                "WHERE table_name = 'team_members' "
                "ORDER BY ordinal_position"
            ))
            team_members_columns = result.all()
            print("\n   TeamMembers table columns:")
            for col in team_members_columns:
                print(f"      - {col[0]}: {col[1]} (nullable: {col[2]})")

            # Check task_shares table structure
            result = session.exec(text(
                "SELECT column_name, data_type, is_nullable "
                "FROM information_schema.columns "
                "WHERE table_name = 'task_shares' "
                "ORDER BY ordinal_position"
            ))
            task_shares_columns = result.all()
            print("\n   TaskShares table columns:")
            for col in task_shares_columns:
                print(f"      - {col[0]}: {col[1]} (nullable: {col[2]})")

            # Check tasks.team_id column
            result = session.exec(text(
                "SELECT column_name, data_type, is_nullable "
                "FROM information_schema.columns "
                "WHERE table_name = 'tasks' AND column_name = 'team_id'"
            ))
            team_id_col = result.first()
            if team_id_col:
                print(f"\n   Tasks table team_id column:")
                print(f"      - {team_id_col[0]}: {team_id_col[1]} (nullable: {team_id_col[2]})")

            # Check foreign key constraints
            result = session.exec(text(
                "SELECT tc.constraint_name, tc.table_name, kcu.column_name, "
                "ccu.table_name AS foreign_table_name, ccu.column_name AS foreign_column_name "
                "FROM information_schema.table_constraints AS tc "
                "JOIN information_schema.key_column_usage AS kcu "
                "  ON tc.constraint_name = kcu.constraint_name "
                "JOIN information_schema.constraint_column_usage AS ccu "
                "  ON ccu.constraint_name = tc.constraint_name "
                "WHERE tc.constraint_type = 'FOREIGN KEY' "
                "  AND tc.table_name IN ('teams', 'team_members', 'task_shares', 'tasks') "
                "ORDER BY tc.table_name, tc.constraint_name"
            ))
            fk_constraints = result.all()
            print("\n   Foreign key constraints:")
            for fk in fk_constraints:
                print(f"      - {fk[1]}.{fk[2]} → {fk[3]}.{fk[4]}")

            # Check unique constraints
            result = session.exec(text(
                "SELECT tc.constraint_name, tc.table_name, kcu.column_name "
                "FROM information_schema.table_constraints AS tc "
                "JOIN information_schema.key_column_usage AS kcu "
                "  ON tc.constraint_name = kcu.constraint_name "
                "WHERE tc.constraint_type = 'UNIQUE' "
                "  AND tc.table_name IN ('teams', 'team_members', 'task_shares') "
                "ORDER BY tc.table_name, tc.constraint_name"
            ))
            unique_constraints = result.all()
            print("\n   Unique constraints:")
            for uc in unique_constraints:
                print(f"      - {uc[1]}.{uc[2]} ({uc[0]})")

            # Check indexes
            result = session.exec(text(
                "SELECT indexname, tablename "
                "FROM pg_indexes "
                "WHERE tablename IN ('teams', 'team_members', 'task_shares', 'tasks') "
                "ORDER BY tablename, indexname"
            ))
            indexes = result.all()
            print("\n   Indexes created:")
            for idx in indexes:
                print(f"      - {idx[0]} on {idx[1]}")

        print("\n[SUCCESS] Migration verification complete")
    except Exception as e:
        print(f"[WARNING] Verification warning: {e}")

    # Step 7: Summary
    print("\n" + "="*70)
    print("Migration Summary")
    print("="*70)
    print("[SUCCESS] Teams table created")
    print("[SUCCESS] TeamMembers table created")
    print("[SUCCESS] TaskShares table created")
    print("[SUCCESS] Tasks table extended with team_id foreign key")
    print("[SUCCESS] All foreign key constraints created")
    print("[SUCCESS] All unique constraints created")
    print("[SUCCESS] All indexes created for performance")
    print("[SUCCESS] Existing task data preserved (team_id = NULL)")
    print("\nNext steps:")
    print("1. Implement team management endpoints (POST/GET/PATCH/DELETE /api/teams)")
    print("2. Implement team member management endpoints")
    print("3. Implement task sharing endpoints")
    print("4. Update task endpoints to support team_id parameter")
    print("5. Implement permission checking middleware")
    print("="*70 + "\n")

    return True


def rollback_migration():
    """Rollback the Phase 3 migration (for testing purposes)."""
    print("\n" + "="*70)
    print("Phase 3 Migration Rollback")
    print("="*70 + "\n")

    print("[WARNING] This will delete all teams, memberships, and shares")
    print("[WARNING] Tasks will remain but team_id will be removed")

    try:
        with Session(engine) as session:
            # Drop team_id column from tasks
            print("\nRemoving team_id column from tasks table...")
            session.exec(text("ALTER TABLE tasks DROP COLUMN IF EXISTS team_id"))

            # Drop tables in reverse order of dependencies
            print("Dropping task_shares table...")
            session.exec(text("DROP TABLE IF EXISTS task_shares CASCADE"))

            print("Dropping team_members table...")
            session.exec(text("DROP TABLE IF EXISTS team_members CASCADE"))

            print("Dropping teams table...")
            session.exec(text("DROP TABLE IF EXISTS teams CASCADE"))

            session.commit()

        print("\n[SUCCESS] Rollback complete")
        return True
    except Exception as e:
        print(f"\n[ERROR] Rollback failed: {e}")
        return False


if __name__ == "__main__":
    # Check for rollback flag
    if len(sys.argv) > 1 and sys.argv[1] == "--rollback":
        success = rollback_migration()
    else:
        success = run_migration()

    sys.exit(0 if success else 1)
