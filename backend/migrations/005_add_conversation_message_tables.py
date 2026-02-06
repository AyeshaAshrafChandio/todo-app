"""
Migration 005: Add Conversation and Message tables for AI Chat Backend

This migration adds support for AI-powered chatbot conversations by creating:
- conversations table: Stores chat sessions between users and AI assistant
- messages table: Stores individual messages in conversations

Spec: 005-ai-chat-backend
Date: 2026-02-06
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./todo_dev.db")


def upgrade():
    """
    Apply migration: Create conversations and messages tables.
    """
    engine = create_engine(DATABASE_URL)

    with Session(engine) as session:
        print("Starting Migration 005: Add Conversation and Message tables...")

        # Create conversations table
        print("Creating conversations table...")
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id VARCHAR(36) NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """))

        # Create indexes for conversations
        print("Creating indexes for conversations table...")
        session.execute(text("""
            CREATE INDEX IF NOT EXISTS ix_conversations_user_id
            ON conversations(user_id)
        """))

        session.execute(text("""
            CREATE INDEX IF NOT EXISTS ix_conversations_updated_at
            ON conversations(updated_at)
        """))

        # Create messages table
        print("Creating messages table...")
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL,
                user_id VARCHAR(36) NOT NULL,
                role VARCHAR(20) NOT NULL CHECK(role IN ('user', 'assistant')),
                content TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """))

        # Create indexes for messages
        print("Creating indexes for messages table...")
        session.execute(text("""
            CREATE INDEX IF NOT EXISTS ix_messages_conversation_id
            ON messages(conversation_id)
        """))

        session.execute(text("""
            CREATE INDEX IF NOT EXISTS ix_messages_user_id
            ON messages(user_id)
        """))

        session.execute(text("""
            CREATE INDEX IF NOT EXISTS ix_messages_created_at
            ON messages(created_at)
        """))

        session.execute(text("""
            CREATE INDEX IF NOT EXISTS ix_messages_conversation_created
            ON messages(conversation_id, created_at)
        """))

        session.commit()
        print("Migration 005 completed successfully!")


def downgrade():
    """
    Rollback migration: Drop conversations and messages tables.
    """
    engine = create_engine(DATABASE_URL)

    with Session(engine) as session:
        print("Rolling back Migration 005...")

        # Drop tables in reverse order (messages first due to foreign key)
        print("Dropping messages table...")
        session.execute(text("DROP TABLE IF EXISTS messages"))

        print("Dropping conversations table...")
        session.execute(text("DROP TABLE IF EXISTS conversations"))

        session.commit()
        print("Migration 005 rollback completed!")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "downgrade":
        downgrade()
    else:
        upgrade()
