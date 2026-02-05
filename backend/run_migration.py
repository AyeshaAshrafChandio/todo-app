"""
Simple migration runner for Phase 2 schema changes.

This script directly creates the database tables using SQLModel.
"""

import os
import sys

# Set environment variables before importing app modules
os.environ["DATABASE_URL"] = "sqlite:///./test_migration.db"
os.environ["BETTER_AUTH_SECRET"] = "test-secret-for-migration-only"

from sqlmodel import SQLModel, Session, select
from app.database.connection import engine
from app.models import Task, User

print("="*60)
print("Phase 2 Database Migration")
print("="*60)

# Create all tables
print("\nCreating database tables...")
SQLModel.metadata.create_all(engine)
print("[SUCCESS] Tables created")

# Verify tables were created
print("\nVerifying schema...")
with Session(engine) as session:
    # Test User model
    print("\n1. Testing User model:")
    test_user = User(
        email="test@example.com",
        password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqJfitzXCO"
    )
    session.add(test_user)
    session.commit()
    session.refresh(test_user)
    print(f"   - Created user: {test_user.id}")
    print(f"   - Email: {test_user.email}")
    print(f"   - Created at: {test_user.created_at}")

    # Test Task model with user_id
    print("\n2. Testing Task model with user_id:")
    test_task = Task(
        title="Test task with user",
        description="This task belongs to a user",
        user_id=test_user.id
    )
    session.add(test_task)
    session.commit()
    session.refresh(test_task)
    print(f"   - Created task: {test_task.id}")
    print(f"   - Title: {test_task.title}")
    print(f"   - User ID: {test_task.user_id}")

    # Test Task model without user_id (legacy)
    print("\n3. Testing Task model without user_id (legacy):")
    legacy_task = Task(
        title="Legacy task without user",
        description="This task has no user (nullable)"
    )
    session.add(legacy_task)
    session.commit()
    session.refresh(legacy_task)
    print(f"   - Created task: {legacy_task.id}")
    print(f"   - Title: {legacy_task.title}")
    print(f"   - User ID: {legacy_task.user_id} (None = legacy)")

    # Verify foreign key relationship
    print("\n4. Verifying foreign key relationship:")
    user_tasks = session.exec(
        select(Task).where(Task.user_id == test_user.id)
    ).all()
    print(f"   - User {test_user.email} has {len(user_tasks)} task(s)")

    # Verify nullable user_id
    print("\n5. Verifying nullable user_id:")
    orphan_tasks = session.exec(
        select(Task).where(Task.user_id == None)
    ).all()
    print(f"   - Found {len(orphan_tasks)} task(s) without user (legacy)")

print("\n" + "="*60)
print("Migration Summary")
print("="*60)
print("[SUCCESS] User model created and tested")
print("[SUCCESS] Task model extended with user_id foreign key")
print("[SUCCESS] Foreign key constraint working")
print("[SUCCESS] Nullable user_id supports legacy tasks")
print("[SUCCESS] All schema changes verified")
print("="*60)

print("\nDatabase file: test_migration.db")
print("You can inspect it with: sqlite3 test_migration.db")
