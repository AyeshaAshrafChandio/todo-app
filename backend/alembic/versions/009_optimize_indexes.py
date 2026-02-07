"""optimize database indexes for common queries

Revision ID: 009_optimize_indexes
Revises: 65694ec1b416
Create Date: 2026-02-07

This migration adds optimized indexes for common query patterns identified
through performance monitoring. These indexes improve query performance for:
- Task filtering by user and status
- Dashboard statistics queries
- Conversation and message lookups
- Team and sharing queries
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '009_optimize_indexes'
down_revision: Union[str, None] = '65694ec1b416'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Add optimized indexes for common query patterns.

    Index Strategy:
    1. Composite indexes for frequently combined filters
    2. Covering indexes for dashboard statistics
    3. Foreign key indexes for JOIN performance
    4. Timestamp indexes for date-based queries
    """

    # Tasks table indexes
    # -----------------

    # Composite index for user_id + status (most common query pattern)
    # Used by: GET /api/{user_id}/tasks?status=pending
    # Used by: Dashboard statistics queries
    op.create_index(
        'idx_tasks_user_status',
        'tasks',
        ['user_id', 'status'],
        unique=False
    )

    # Composite index for user_id + created_at (for sorting recent tasks)
    # Used by: Task list with date sorting
    op.create_index(
        'idx_tasks_user_created',
        'tasks',
        ['user_id', 'created_at'],
        unique=False
    )

    # Composite index for user_id + updated_at (for activity tracking)
    # Used by: Dashboard activity metrics
    op.create_index(
        'idx_tasks_user_updated',
        'tasks',
        ['user_id', 'updated_at'],
        unique=False
    )

    # Conversations table indexes
    # -------------------------

    # Composite index for user_id + created_at (for recent conversations)
    # Used by: GET /api/chat/conversations
    op.create_index(
        'idx_conversations_user_created',
        'conversations',
        ['user_id', 'created_at'],
        unique=False
    )

    # Messages table indexes
    # --------------------

    # Composite index for conversation_id + created_at (for message ordering)
    # Used by: GET /api/chat/conversations/{id}/messages
    op.create_index(
        'idx_messages_conversation_created',
        'messages',
        ['conversation_id', 'created_at'],
        unique=False
    )

    # Index on user_id for message filtering
    # Used by: User-specific message queries
    op.create_index(
        'idx_messages_user',
        'messages',
        ['user_id'],
        unique=False
    )

    # Team members table indexes
    # ------------------------

    # Composite index for user_id + team_id (for user's teams lookup)
    # Used by: GET /api/teams (user's teams)
    op.create_index(
        'idx_team_members_user_team',
        'team_members',
        ['user_id', 'team_id'],
        unique=False
    )

    # Index on role for permission checks
    # Used by: Authorization queries
    op.create_index(
        'idx_team_members_role',
        'team_members',
        ['role'],
        unique=False
    )

    # Task shares table indexes
    # -----------------------

    # Composite index for shared_with_user_id + task_id (for user's shared tasks)
    # Used by: Dashboard shared tasks count
    op.create_index(
        'idx_task_shares_user_task',
        'task_shares',
        ['shared_with_user_id', 'task_id'],
        unique=False
    )

    # Composite index for task_id + permission (for permission checks)
    # Used by: Authorization queries
    op.create_index(
        'idx_task_shares_task_permission',
        'task_shares',
        ['task_id', 'permission'],
        unique=False
    )

    # Index on shared_by_user_id (for tracking who shared what)
    # Used by: Audit and analytics queries
    op.create_index(
        'idx_task_shares_shared_by',
        'task_shares',
        ['shared_by_user_id'],
        unique=False
    )

    # Teams table indexes
    # -----------------

    # Index on owner_id (for owner's teams lookup)
    # Used by: GET /api/teams (owned teams)
    op.create_index(
        'idx_teams_owner',
        'teams',
        ['owner_id'],
        unique=False
    )

    # Index on created_at (for recent teams)
    # Used by: Team list sorting
    op.create_index(
        'idx_teams_created',
        'teams',
        ['created_at'],
        unique=False
    )


def downgrade() -> None:
    """
    Remove optimized indexes.
    """
    # Teams table indexes
    op.drop_index('idx_teams_created', table_name='teams')
    op.drop_index('idx_teams_owner', table_name='teams')

    # Task shares table indexes
    op.drop_index('idx_task_shares_shared_by', table_name='task_shares')
    op.drop_index('idx_task_shares_task_permission', table_name='task_shares')
    op.drop_index('idx_task_shares_user_task', table_name='task_shares')

    # Team members table indexes
    op.drop_index('idx_team_members_role', table_name='team_members')
    op.drop_index('idx_team_members_user_team', table_name='team_members')

    # Messages table indexes
    op.drop_index('idx_messages_user', table_name='messages')
    op.drop_index('idx_messages_conversation_created', table_name='messages')

    # Conversations table indexes
    op.drop_index('idx_conversations_user_created', table_name='conversations')

    # Tasks table indexes
    op.drop_index('idx_tasks_user_updated', table_name='tasks')
    op.drop_index('idx_tasks_user_created', table_name='tasks')
    op.drop_index('idx_tasks_user_status', table_name='tasks')
