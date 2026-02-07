"""
Database seed script with sample data for development and testing.

This module provides functions to seed the database with sample data for:
- Users
- Tasks
- Conversations
- Messages
- Teams
- Team Members
- Task Shares

Usage:
    python -m app.database.seed
"""

from datetime import datetime, timedelta
from app.database.session import get_db_context
from app.models.user import User
from app.models.task import Task
from app.models.conversation import Conversation
from app.models.message import Message, MessageRole
from app.models.team import Team
from app.models.team_member import TeamMember, TeamRole
from app.models.task_share import TaskShare, SharePermission


def seed_users(db):
    """Create sample users."""
    print("Seeding users...")

    users = [
        User(
            id="user-001",
            email="alice@example.com",
            name="Alice Johnson",
            created_at=datetime.utcnow() - timedelta(days=30)
        ),
        User(
            id="user-002",
            email="bob@example.com",
            name="Bob Smith",
            created_at=datetime.utcnow() - timedelta(days=25)
        ),
        User(
            id="user-003",
            email="charlie@example.com",
            name="Charlie Brown",
            created_at=datetime.utcnow() - timedelta(days=20)
        ),
    ]

    for user in users:
        db.add(user)

    db.commit()
    print(f"  Created {len(users)} users")
    return users


def seed_tasks(db, users):
    """Create sample tasks."""
    print("Seeding tasks...")

    tasks = [
        # Alice's tasks
        Task(
            title="Buy groceries",
            description="Milk, eggs, bread, and vegetables",
            completed=False,
            user_id=users[0].id,
            created_at=datetime.utcnow() - timedelta(days=5)
        ),
        Task(
            title="Finish project report",
            description="Complete the Q1 project report and submit to manager",
            completed=True,
            user_id=users[0].id,
            created_at=datetime.utcnow() - timedelta(days=10)
        ),
        Task(
            title="Schedule dentist appointment",
            description="Call dentist office and schedule checkup",
            completed=False,
            user_id=users[0].id,
            created_at=datetime.utcnow() - timedelta(days=2)
        ),

        # Bob's tasks
        Task(
            title="Review pull requests",
            description="Review and approve pending PRs in the repository",
            completed=False,
            user_id=users[1].id,
            created_at=datetime.utcnow() - timedelta(days=3)
        ),
        Task(
            title="Update documentation",
            description="Update API documentation with new endpoints",
            completed=True,
            user_id=users[1].id,
            created_at=datetime.utcnow() - timedelta(days=7)
        ),

        # Charlie's tasks
        Task(
            title="Prepare presentation",
            description="Create slides for team meeting on Friday",
            completed=False,
            user_id=users[2].id,
            created_at=datetime.utcnow() - timedelta(days=1)
        ),
    ]

    for task in tasks:
        db.add(task)

    db.commit()
    print(f"  Created {len(tasks)} tasks")
    return tasks


def seed_conversations(db, users):
    """Create sample conversations."""
    print("Seeding conversations...")

    conversations = [
        # Alice's conversations
        Conversation(
            user_id=users[0].id,
            created_at=datetime.utcnow() - timedelta(days=5),
            updated_at=datetime.utcnow() - timedelta(days=5)
        ),
        Conversation(
            user_id=users[0].id,
            created_at=datetime.utcnow() - timedelta(days=2),
            updated_at=datetime.utcnow() - timedelta(days=2)
        ),

        # Bob's conversations
        Conversation(
            user_id=users[1].id,
            created_at=datetime.utcnow() - timedelta(days=3),
            updated_at=datetime.utcnow() - timedelta(days=3)
        ),
    ]

    for conversation in conversations:
        db.add(conversation)

    db.commit()
    db.refresh(conversations[0])
    db.refresh(conversations[1])
    db.refresh(conversations[2])

    print(f"  Created {len(conversations)} conversations")
    return conversations


def seed_messages(db, conversations, users):
    """Create sample messages."""
    print("Seeding messages...")

    messages = [
        # Conversation 1 (Alice)
        Message(
            conversation_id=conversations[0].id,
            user_id=users[0].id,
            role=MessageRole.USER,
            content="Add buy groceries to my task list",
            created_at=datetime.utcnow() - timedelta(days=5, hours=2)
        ),
        Message(
            conversation_id=conversations[0].id,
            user_id=users[0].id,
            role=MessageRole.ASSISTANT,
            content="I've added 'Buy groceries' to your task list. Is there anything else you'd like me to help with?",
            created_at=datetime.utcnow() - timedelta(days=5, hours=2, minutes=1)
        ),
        Message(
            conversation_id=conversations[0].id,
            user_id=users[0].id,
            role=MessageRole.USER,
            content="Yes, also add schedule dentist appointment",
            created_at=datetime.utcnow() - timedelta(days=5, hours=1)
        ),
        Message(
            conversation_id=conversations[0].id,
            user_id=users[0].id,
            role=MessageRole.ASSISTANT,
            content="Done! I've added 'Schedule dentist appointment' to your task list. You now have 2 pending tasks.",
            created_at=datetime.utcnow() - timedelta(days=5, hours=1, minutes=1)
        ),

        # Conversation 2 (Alice)
        Message(
            conversation_id=conversations[1].id,
            user_id=users[0].id,
            role=MessageRole.USER,
            content="Show me my completed tasks",
            created_at=datetime.utcnow() - timedelta(days=2, hours=3)
        ),
        Message(
            conversation_id=conversations[1].id,
            user_id=users[0].id,
            role=MessageRole.ASSISTANT,
            content="You have 1 completed task: 'Finish project report'. Great job!",
            created_at=datetime.utcnow() - timedelta(days=2, hours=3, minutes=1)
        ),

        # Conversation 3 (Bob)
        Message(
            conversation_id=conversations[2].id,
            user_id=users[1].id,
            role=MessageRole.USER,
            content="What tasks do I have pending?",
            created_at=datetime.utcnow() - timedelta(days=3, hours=4)
        ),
        Message(
            conversation_id=conversations[2].id,
            user_id=users[1].id,
            role=MessageRole.ASSISTANT,
            content="You have 1 pending task: 'Review pull requests'. Would you like me to mark it as complete?",
            created_at=datetime.utcnow() - timedelta(days=3, hours=4, minutes=1)
        ),
    ]

    for message in messages:
        db.add(message)

    db.commit()
    print(f"  Created {len(messages)} messages")
    return messages


def seed_teams(db, users):
    """Create sample teams."""
    print("Seeding teams...")

    teams = [
        Team(
            id="team-001",
            name="Engineering Team",
            owner_id=users[0].id,
            created_at=datetime.utcnow() - timedelta(days=15)
        ),
        Team(
            id="team-002",
            name="Product Team",
            owner_id=users[1].id,
            created_at=datetime.utcnow() - timedelta(days=10)
        ),
    ]

    for team in teams:
        db.add(team)

    db.commit()
    print(f"  Created {len(teams)} teams")
    return teams


def seed_team_members(db, teams, users):
    """Create sample team members."""
    print("Seeding team members...")

    team_members = [
        # Engineering Team
        TeamMember(
            team_id=teams[0].id,
            user_id=users[0].id,
            role=TeamRole.OWNER,
            created_at=datetime.utcnow() - timedelta(days=15)
        ),
        TeamMember(
            team_id=teams[0].id,
            user_id=users[1].id,
            role=TeamRole.MEMBER,
            created_at=datetime.utcnow() - timedelta(days=14)
        ),
        TeamMember(
            team_id=teams[0].id,
            user_id=users[2].id,
            role=TeamRole.MEMBER,
            created_at=datetime.utcnow() - timedelta(days=13)
        ),

        # Product Team
        TeamMember(
            team_id=teams[1].id,
            user_id=users[1].id,
            role=TeamRole.OWNER,
            created_at=datetime.utcnow() - timedelta(days=10)
        ),
        TeamMember(
            team_id=teams[1].id,
            user_id=users[2].id,
            role=TeamRole.MEMBER,
            created_at=datetime.utcnow() - timedelta(days=9)
        ),
    ]

    for member in team_members:
        db.add(member)

    db.commit()
    print(f"  Created {len(team_members)} team members")
    return team_members


def seed_task_shares(db, tasks, users):
    """Create sample task shares."""
    print("Seeding task shares...")

    task_shares = [
        # Alice shares task with Bob
        TaskShare(
            task_id=tasks[0].id,  # Buy groceries
            shared_with_user_id=users[1].id,  # Bob
            shared_by_user_id=users[0].id,  # Alice
            permission=SharePermission.VIEW,
            created_at=datetime.utcnow() - timedelta(days=4)
        ),
        # Bob shares task with Charlie
        TaskShare(
            task_id=tasks[3].id,  # Review pull requests
            shared_with_user_id=users[2].id,  # Charlie
            shared_by_user_id=users[1].id,  # Bob
            permission=SharePermission.EDIT,
            created_at=datetime.utcnow() - timedelta(days=2)
        ),
    ]

    for share in task_shares:
        db.add(share)

    db.commit()
    print(f"  Created {len(task_shares)} task shares")
    return task_shares


def seed_all():
    """Seed all sample data."""
    print("\n=== Starting Database Seeding ===\n")

    with get_db_context() as db:
        # Check if data already exists
        from sqlalchemy import text
        user_count = db.exec(text("SELECT COUNT(*) FROM users")).first()[0]

        if user_count > 0:
            print(f"Database already contains {user_count} users.")
            response = input("Do you want to clear existing data and reseed? (yes/no): ")
            if response.lower() != 'yes':
                print("Seeding cancelled.")
                return

            # Clear existing data (in reverse order of dependencies)
            print("\nClearing existing data...")
            db.exec(text("DELETE FROM task_shares"))
            db.exec(text("DELETE FROM team_members"))
            db.exec(text("DELETE FROM teams"))
            db.exec(text("DELETE FROM messages"))
            db.exec(text("DELETE FROM conversations"))
            db.exec(text("DELETE FROM tasks"))
            db.exec(text("DELETE FROM users"))
            db.commit()
            print("  Existing data cleared")

        # Seed data
        users = seed_users(db)
        tasks = seed_tasks(db, users)
        conversations = seed_conversations(db, users)
        messages = seed_messages(db, conversations, users)
        teams = seed_teams(db, users)
        team_members = seed_team_members(db, teams, users)
        task_shares = seed_task_shares(db, tasks, users)

        print("\n=== Database Seeding Complete ===")
        print(f"\nSummary:")
        print(f"  Users: {len(users)}")
        print(f"  Tasks: {len(tasks)}")
        print(f"  Conversations: {len(conversations)}")
        print(f"  Messages: {len(messages)}")
        print(f"  Teams: {len(teams)}")
        print(f"  Team Members: {len(team_members)}")
        print(f"  Task Shares: {len(task_shares)}")
        print("\nSample credentials:")
        print("  alice@example.com")
        print("  bob@example.com")
        print("  charlie@example.com")


if __name__ == "__main__":
    seed_all()
