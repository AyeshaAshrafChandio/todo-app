"""
Test database schema for Phase 3 (User Story 1).

This module tests that all database tables are created correctly with proper
relationships, constraints, and indexes.
"""

import pytest
from datetime import datetime
from sqlalchemy import text
from app.database.session import get_db_context
from app.models.user import User
from app.models.task import Task
from app.models.conversation import Conversation
from app.models.message import Message, MessageRole


class TestDatabaseSchema:
    """Test database schema structure and relationships."""

    def test_tables_exist(self):
        """Test that all required tables exist."""
        with get_db_context() as db:
            result = db.exec(text("""
                SELECT tablename
                FROM pg_tables
                WHERE schemaname = 'public'
                ORDER BY tablename
            """)).all()

            table_names = [row[0] for row in result]

            # Check core tables exist
            assert 'users' in table_names
            assert 'tasks' in table_names
            assert 'conversations' in table_names
            assert 'messages' in table_names
            assert 'teams' in table_names
            assert 'team_members' in table_names
            assert 'task_shares' in table_names

    def test_task_table_structure(self):
        """Test that tasks table has correct columns."""
        with get_db_context() as db:
            result = db.exec(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'tasks'
                ORDER BY ordinal_position
            """)).all()

            columns = {row[0]: (row[1], row[2]) for row in result}

            # Check required columns exist
            assert 'id' in columns
            assert 'user_id' in columns
            assert 'title' in columns
            assert 'description' in columns
            assert 'completed' in columns
            assert 'created_at' in columns
            assert 'updated_at' in columns

            # Check data types
            assert columns['id'][0] == 'integer'
            assert columns['user_id'][0] == 'character varying'
            assert columns['title'][0] == 'character varying'
            assert columns['completed'][0] == 'boolean'
            assert 'timestamp' in columns['created_at'][0]
            assert 'timestamp' in columns['updated_at'][0]

    def test_conversation_table_structure(self):
        """Test that conversations table has correct columns."""
        with get_db_context() as db:
            result = db.exec(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'conversations'
                ORDER BY ordinal_position
            """)).all()

            columns = {row[0]: (row[1], row[2]) for row in result}

            # Check required columns exist
            assert 'id' in columns
            assert 'user_id' in columns
            assert 'created_at' in columns
            assert 'updated_at' in columns

            # Check data types
            assert columns['id'][0] == 'integer'
            assert columns['user_id'][0] == 'character varying'
            assert 'timestamp' in columns['created_at'][0]
            assert 'timestamp' in columns['updated_at'][0]

    def test_message_table_structure(self):
        """Test that messages table has correct columns."""
        with get_db_context() as db:
            result = db.exec(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'messages'
                ORDER BY ordinal_position
            """)).all()

            columns = {row[0]: (row[1], row[2]) for row in result}

            # Check required columns exist
            assert 'id' in columns
            assert 'conversation_id' in columns
            assert 'user_id' in columns
            assert 'role' in columns
            assert 'content' in columns
            assert 'created_at' in columns

            # Check data types
            assert columns['id'][0] == 'integer'
            assert columns['conversation_id'][0] == 'integer'
            assert columns['user_id'][0] == 'character varying'
            assert columns['content'][0] == 'character varying'
            assert 'timestamp' in columns['created_at'][0]

    def test_foreign_key_constraints(self):
        """Test that foreign key constraints are properly defined."""
        with get_db_context() as db:
            result = db.exec(text("""
                SELECT
                    tc.table_name,
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY'
                    AND tc.table_schema = 'public'
                ORDER BY tc.table_name, kcu.column_name
            """)).all()

            fk_map = {}
            for row in result:
                table = row[0]
                if table not in fk_map:
                    fk_map[table] = []
                fk_map[table].append({
                    'column': row[1],
                    'references_table': row[2],
                    'references_column': row[3]
                })

            # Check tasks foreign keys
            assert 'tasks' in fk_map
            task_fks = {fk['column']: fk for fk in fk_map['tasks']}
            assert 'user_id' in task_fks
            assert task_fks['user_id']['references_table'] == 'users'

            # Check conversations foreign keys
            assert 'conversations' in fk_map
            conv_fks = {fk['column']: fk for fk in fk_map['conversations']}
            assert 'user_id' in conv_fks
            assert conv_fks['user_id']['references_table'] == 'users'

            # Check messages foreign keys
            assert 'messages' in fk_map
            msg_fks = {fk['column']: fk for fk in fk_map['messages']}
            assert 'conversation_id' in msg_fks
            assert msg_fks['conversation_id']['references_table'] == 'conversations'
            assert 'user_id' in msg_fks
            assert msg_fks['user_id']['references_table'] == 'users'

    def test_indexes_exist(self):
        """Test that required indexes are created."""
        with get_db_context() as db:
            result = db.exec(text("""
                SELECT tablename, indexname
                FROM pg_indexes
                WHERE schemaname = 'public'
                ORDER BY tablename, indexname
            """)).all()

            index_map = {}
            for row in result:
                table = row[0]
                if table not in index_map:
                    index_map[table] = []
                index_map[table].append(row[1])

            # Check tasks indexes
            assert 'tasks' in index_map
            assert any('user_id' in idx for idx in index_map['tasks'])

            # Check conversations indexes
            assert 'conversations' in index_map
            assert any('user_id' in idx for idx in index_map['conversations'])

            # Check messages indexes
            assert 'messages' in index_map
            assert any('conversation_id' in idx for idx in index_map['messages'])
            assert any('user_id' in idx for idx in index_map['messages'])
            assert any('created_at' in idx for idx in index_map['messages'])


class TestDatabaseRelationships:
    """Test database relationships work correctly."""

    @pytest.fixture
    def test_user(self):
        """Create a test user."""
        with get_db_context() as db:
            user = User(
                id="test-user-001",
                email="test@example.com",
                name="Test User",
                password_hash="$2b$12$test_hash_for_testing_only"  # Dummy hash for testing
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            yield user

            # Cleanup
            db.delete(user)
            db.commit()

    def test_create_task_with_user(self, test_user):
        """Test creating a task with user relationship."""
        with get_db_context() as db:
            task = Task(
                title="Test Task",
                description="Test description",
                completed=False,
                user_id=test_user.id
            )
            db.add(task)
            db.commit()
            db.refresh(task)

            assert task.id is not None
            assert task.user_id == test_user.id
            assert task.title == "Test Task"

            # Cleanup
            db.delete(task)
            db.commit()

    def test_create_conversation_with_messages(self, test_user):
        """Test creating a conversation with messages."""
        with get_db_context() as db:
            # Create conversation
            conversation = Conversation(user_id=test_user.id)
            db.add(conversation)
            db.commit()
            db.refresh(conversation)

            assert conversation.id is not None
            assert conversation.user_id == test_user.id

            # Create messages
            message1 = Message(
                conversation_id=conversation.id,
                user_id=test_user.id,
                role=MessageRole.USER,
                content="Hello"
            )
            message2 = Message(
                conversation_id=conversation.id,
                user_id=test_user.id,
                role=MessageRole.ASSISTANT,
                content="Hi there!"
            )
            db.add(message1)
            db.add(message2)
            db.commit()
            db.refresh(message1)
            db.refresh(message2)

            assert message1.id is not None
            assert message1.conversation_id == conversation.id
            assert message2.id is not None
            assert message2.conversation_id == conversation.id

            # Cleanup
            db.delete(message1)
            db.delete(message2)
            db.delete(conversation)
            db.commit()

    def test_cascade_delete_conversation_messages(self, test_user):
        """Test that deleting a conversation cascades to messages."""
        with get_db_context() as db:
            # Create conversation with message
            conversation = Conversation(user_id=test_user.id)
            db.add(conversation)
            db.commit()
            db.refresh(conversation)

            message = Message(
                conversation_id=conversation.id,
                user_id=test_user.id,
                role=MessageRole.USER,
                content="Test message"
            )
            db.add(message)
            db.commit()
            db.refresh(message)

            message_id = message.id
            conversation_id = conversation.id

            # Delete conversation
            db.delete(conversation)
            db.commit()

            # Verify message was also deleted (cascade)
            result = db.exec(text(f"""
                SELECT COUNT(*) FROM messages WHERE id = {message_id}
            """)).first()

            assert result[0] == 0, "Message should be deleted when conversation is deleted"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
