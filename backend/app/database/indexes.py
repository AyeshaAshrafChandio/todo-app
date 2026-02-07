"""
Database indexing strategy and utilities for optimal query performance.

This module documents the indexing strategy for the application and provides
utilities for creating and managing indexes. Proper indexing is critical for
query performance, especially for large datasets.

Indexing Strategy:
==================

1. Primary Keys (Automatic)
   - All tables have auto-incrementing integer primary keys
   - Primary keys are automatically indexed by the database

2. Foreign Keys (Required)
   - All foreign key columns MUST have indexes
   - Improves JOIN performance and referential integrity checks
   - Examples: user_id, conversation_id, team_id, task_id

3. Frequently Queried Columns (High Priority)
   - Columns used in WHERE clauses frequently
   - Columns used in ORDER BY clauses
   - Examples: status, created_at, completed

4. Composite Indexes (Optimization)
   - Multiple columns queried together
   - Order matters: most selective column first
   - Examples: (user_id, created_at), (team_id, status)

5. Partial Indexes (Advanced)
   - Indexes on subset of rows (WHERE condition)
   - Useful for filtering by status or flags
   - Example: CREATE INDEX idx_active_tasks ON tasks(user_id) WHERE completed = false

Index Naming Convention:
========================
- Single column: idx_{table}_{column}
- Composite: idx_{table}_{col1}_{col2}
- Partial: idx_{table}_{column}_where_{condition}
- Unique: uniq_{table}_{column}

Examples:
- idx_tasks_user_id
- idx_tasks_user_id_created_at
- idx_tasks_user_id_where_active
- uniq_users_email

Performance Guidelines:
=======================

DO:
- Index foreign keys (user_id, conversation_id, etc.)
- Index columns used in WHERE clauses frequently
- Index columns used in ORDER BY clauses
- Use composite indexes for multi-column queries
- Monitor index usage with pg_stat_user_indexes

DON'T:
- Over-index (each index has write overhead)
- Index low-cardinality columns (e.g., boolean with 2 values)
- Index columns that are rarely queried
- Create redundant indexes (e.g., (a,b) makes (a) redundant)

Monitoring Index Usage:
========================

Query to check index usage:
```sql
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan ASC;
```

Query to find missing indexes:
```sql
SELECT
    schemaname,
    tablename,
    seq_scan,
    seq_tup_read,
    idx_scan,
    seq_tup_read / seq_scan AS avg_seq_tup_read
FROM pg_stat_user_tables
WHERE schemaname = 'public'
    AND seq_scan > 0
ORDER BY seq_tup_read DESC;
```

Planned Indexes by Table:
==========================

tasks:
- idx_tasks_user_id (foreign key, high priority)
- idx_tasks_team_id (foreign key, medium priority)
- idx_tasks_status (filter by status, medium priority)
- idx_tasks_user_id_created_at (composite, list tasks by user, high priority)
- idx_tasks_user_id_where_active (partial, active tasks only, optimization)

conversations:
- idx_conversations_user_id (foreign key, high priority)
- idx_conversations_created_at (order by date, medium priority)
- idx_conversations_user_id_created_at (composite, list by user, high priority)

messages:
- idx_messages_conversation_id (foreign key, high priority)
- idx_messages_user_id (foreign key, medium priority)
- idx_messages_created_at (order by date, high priority)
- idx_messages_conversation_id_created_at (composite, chat history, high priority)

teams:
- idx_teams_owner_id (foreign key, high priority)
- idx_teams_created_at (order by date, low priority)

team_members:
- idx_team_members_team_id (foreign key, high priority)
- idx_team_members_user_id (foreign key, high priority)
- uniq_team_members_team_id_user_id (unique constraint, prevent duplicates)

task_shares:
- idx_task_shares_task_id (foreign key, high priority)
- idx_task_shares_shared_with_user_id (foreign key, high priority)
- idx_task_shares_shared_by_user_id (foreign key, medium priority)
- uniq_task_shares_task_id_user_id (unique constraint, prevent duplicates)

Implementation Notes:
=====================

1. Indexes are created via Alembic migrations
2. Use CREATE INDEX CONCURRENTLY for production (no table locks)
3. Monitor index usage and drop unused indexes
4. Re-index periodically if data distribution changes significantly
5. Consider BRIN indexes for very large tables with sequential data

Example Migration:
==================

```python
def upgrade() -> None:
    # Create index concurrently (no table lock)
    op.execute('''
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_tasks_user_id
        ON tasks(user_id)
    ''')

    # Create composite index
    op.create_index(
        'idx_tasks_user_id_created_at',
        'tasks',
        ['user_id', 'created_at'],
        unique=False
    )

    # Create partial index
    op.execute('''
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_tasks_user_id_where_active
        ON tasks(user_id)
        WHERE completed = false
    ''')

def downgrade() -> None:
    op.drop_index('idx_tasks_user_id', table_name='tasks')
    op.drop_index('idx_tasks_user_id_created_at', table_name='tasks')
    op.drop_index('idx_tasks_user_id_where_active', table_name='tasks')
```

Performance Targets:
====================

- Dashboard statistics query: < 50ms
- Task list query (paginated): < 100ms
- Single task lookup by ID: < 10ms
- Conversation history query: < 100ms
- Team member lookup: < 50ms

These targets should be achievable with proper indexing on a Neon Serverless
PostgreSQL database with moderate data volumes (< 1M rows per table).
"""

from typing import List, Dict, Any


# Index definitions for each table
# Format: {table_name: [index_definition, ...]}
INDEX_DEFINITIONS: Dict[str, List[Dict[str, Any]]] = {
    "tasks": [
        {
            "name": "idx_tasks_user_id",
            "columns": ["user_id"],
            "unique": False,
            "priority": "high",
            "description": "Foreign key index for user ownership"
        },
        {
            "name": "idx_tasks_team_id",
            "columns": ["team_id"],
            "unique": False,
            "priority": "medium",
            "description": "Foreign key index for team ownership"
        },
        {
            "name": "idx_tasks_user_id_created_at",
            "columns": ["user_id", "created_at"],
            "unique": False,
            "priority": "high",
            "description": "Composite index for listing user tasks by date"
        },
    ],
    "conversations": [
        {
            "name": "idx_conversations_user_id",
            "columns": ["user_id"],
            "unique": False,
            "priority": "high",
            "description": "Foreign key index for user ownership"
        },
        {
            "name": "idx_conversations_user_id_created_at",
            "columns": ["user_id", "created_at"],
            "unique": False,
            "priority": "high",
            "description": "Composite index for listing user conversations by date"
        },
    ],
    "messages": [
        {
            "name": "idx_messages_conversation_id",
            "columns": ["conversation_id"],
            "unique": False,
            "priority": "high",
            "description": "Foreign key index for conversation relationship"
        },
        {
            "name": "idx_messages_conversation_id_created_at",
            "columns": ["conversation_id", "created_at"],
            "unique": False,
            "priority": "high",
            "description": "Composite index for chat history retrieval"
        },
    ],
    "teams": [
        {
            "name": "idx_teams_owner_id",
            "columns": ["owner_id"],
            "unique": False,
            "priority": "high",
            "description": "Foreign key index for team ownership"
        },
    ],
    "team_members": [
        {
            "name": "idx_team_members_team_id",
            "columns": ["team_id"],
            "unique": False,
            "priority": "high",
            "description": "Foreign key index for team relationship"
        },
        {
            "name": "idx_team_members_user_id",
            "columns": ["user_id"],
            "unique": False,
            "priority": "high",
            "description": "Foreign key index for user relationship"
        },
        {
            "name": "uniq_team_members_team_id_user_id",
            "columns": ["team_id", "user_id"],
            "unique": True,
            "priority": "high",
            "description": "Unique constraint to prevent duplicate memberships"
        },
    ],
    "task_shares": [
        {
            "name": "idx_task_shares_task_id",
            "columns": ["task_id"],
            "unique": False,
            "priority": "high",
            "description": "Foreign key index for task relationship"
        },
        {
            "name": "idx_task_shares_shared_with_user_id",
            "columns": ["shared_with_user_id"],
            "unique": False,
            "priority": "high",
            "description": "Foreign key index for recipient user"
        },
        {
            "name": "uniq_task_shares_task_id_user_id",
            "columns": ["task_id", "shared_with_user_id"],
            "unique": True,
            "priority": "high",
            "description": "Unique constraint to prevent duplicate shares"
        },
    ],
}


def get_index_definitions(table_name: str) -> List[Dict[str, Any]]:
    """
    Get index definitions for a specific table.

    Args:
        table_name: Name of the table

    Returns:
        List of index definitions for the table

    Example:
        ```python
        from app.database.indexes import get_index_definitions

        indexes = get_index_definitions("tasks")
        for idx in indexes:
            print(f"Index: {idx['name']}, Columns: {idx['columns']}")
        ```
    """
    return INDEX_DEFINITIONS.get(table_name, [])


def get_all_index_definitions() -> Dict[str, List[Dict[str, Any]]]:
    """
    Get all index definitions for all tables.

    Returns:
        Dictionary mapping table names to their index definitions

    Example:
        ```python
        from app.database.indexes import get_all_index_definitions

        all_indexes = get_all_index_definitions()
        for table, indexes in all_indexes.items():
            print(f"Table: {table}, Indexes: {len(indexes)}")
        ```
    """
    return INDEX_DEFINITIONS
