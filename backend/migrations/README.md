# Database Migration Workflow

This document describes the database migration workflow using Alembic for the MCP Backend Data & Dashboard feature.

## Overview

We use Alembic for database schema versioning and migrations. Alembic provides:
- Version control for database schema changes
- Automatic migration generation from SQLModel changes
- Rollback capabilities for safe deployments
- Migration history tracking

## Directory Structure

```
backend/
├── alembic/                    # Alembic configuration directory
│   ├── env.py                  # Migration environment configuration
│   ├── script.py.mako          # Template for migration files
│   ├── README                  # Alembic documentation
│   └── versions/               # Migration scripts (numbered sequentially)
│       ├── 001_create_tasks_table.py
│       ├── 002_create_conversations_table.py
│       └── ...
├── alembic.ini                 # Alembic configuration file
└── migrations/                 # Migration workflow documentation
    └── README.md               # This file
```

## Prerequisites

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure database URL in `.env`:
   ```
   DATABASE_URL=postgresql://user:pass@host/dbname?sslmode=require
   ```

3. Verify Alembic configuration:
   ```bash
   alembic current
   ```

## Common Workflows

### 1. Create a New Migration (Auto-generate)

Alembic can automatically detect changes in SQLModel models and generate migrations:

```bash
# Generate migration from model changes
alembic revision --autogenerate -m "create tasks table"

# This creates: alembic/versions/001_create_tasks_table.py
```

**Important**: Always review auto-generated migrations before applying them!

### 2. Create a New Migration (Manual)

For complex changes or data migrations, create a manual migration:

```bash
# Create empty migration file
alembic revision -m "add custom indexes"

# Edit the generated file to add upgrade/downgrade logic
```

### 3. Apply Migrations (Upgrade)

```bash
# Apply all pending migrations
alembic upgrade head

# Apply specific number of migrations
alembic upgrade +1

# Apply to specific revision
alembic upgrade abc123
```

### 4. Rollback Migrations (Downgrade)

```bash
# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade abc123

# Rollback all migrations
alembic downgrade base
```

### 5. View Migration History

```bash
# Show current database version
alembic current

# Show migration history
alembic history

# Show verbose history with details
alembic history --verbose
```

### 6. Test Migrations on Neon Branch

Before applying to production, test on a Neon branch:

```bash
# Create Neon branch (via Neon CLI or UI)
neon branches create --name test-migration

# Update DATABASE_URL to branch endpoint
export DATABASE_URL="postgresql://...@branch-endpoint/neondb"

# Test migration
alembic upgrade head

# Verify schema
psql $DATABASE_URL -c "\dt"

# If successful, apply to production
# If failed, fix migration and retry
```

## Migration Best Practices

### DO:

1. **Always review auto-generated migrations**
   - Alembic may not detect all changes correctly
   - Verify column types, constraints, and indexes

2. **Write reversible migrations**
   - Every `upgrade()` should have a corresponding `downgrade()`
   - Test rollback before deploying

3. **Use transactions**
   - Migrations run in transactions by default
   - Keep migrations atomic (all-or-nothing)

4. **Create indexes concurrently**
   ```python
   # For production (no table locks)
   op.execute('CREATE INDEX CONCURRENTLY idx_name ON table(column)')
   ```

5. **Test migrations on branches**
   - Use Neon branching to test migrations safely
   - Never test directly on production

6. **Keep migrations small**
   - One logical change per migration
   - Easier to review, test, and rollback

7. **Document complex migrations**
   - Add comments explaining the purpose
   - Document any manual steps required

### DON'T:

1. **Don't modify existing migrations**
   - Once applied to production, migrations are immutable
   - Create a new migration to fix issues

2. **Don't skip migrations**
   - Apply migrations in order
   - Never cherry-pick migrations

3. **Don't use DROP without backup**
   - Always backup data before destructive operations
   - Consider soft deletes instead of hard deletes

4. **Don't hardcode values**
   - Use environment variables for configuration
   - Keep migrations environment-agnostic

5. **Don't ignore downgrade**
   - Always implement downgrade logic
   - Test rollback scenarios

## Migration Template

```python
"""
Brief description of what this migration does.

Revision ID: abc123
Revises: xyz789
Create Date: 2026-02-07 12:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic
revision: str = 'abc123'
down_revision: Union[str, None] = 'xyz789'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Apply schema changes.

    This function should:
    1. Create/modify tables
    2. Add/modify columns
    3. Create indexes
    4. Migrate data if needed
    """
    # Create table
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('completed', sa.Boolean(), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )

    # Create index
    op.create_index('idx_tasks_user_id', 'tasks', ['user_id'], unique=False)


def downgrade() -> None:
    """
    Reverse schema changes.

    This function should undo everything done in upgrade().
    Operations should be in reverse order.
    """
    # Drop index
    op.drop_index('idx_tasks_user_id', table_name='tasks')

    # Drop table
    op.drop_table('tasks')
```

## Data Migration Example

For migrations that transform data:

```python
def upgrade() -> None:
    # Add new column
    op.add_column('tasks', sa.Column('status', sa.String(length=20), nullable=True))

    # Migrate data
    connection = op.get_bind()
    connection.execute(
        sa.text("""
            UPDATE tasks
            SET status = CASE
                WHEN completed = true THEN 'completed'
                ELSE 'pending'
            END
        """)
    )

    # Make column non-nullable after data migration
    op.alter_column('tasks', 'status', nullable=False)

    # Drop old column
    op.drop_column('tasks', 'completed')


def downgrade() -> None:
    # Add old column back
    op.add_column('tasks', sa.Column('completed', sa.Boolean(), nullable=True))

    # Migrate data back
    connection = op.get_bind()
    connection.execute(
        sa.text("""
            UPDATE tasks
            SET completed = CASE
                WHEN status = 'completed' THEN true
                ELSE false
            END
        """)
    )

    # Make column non-nullable
    op.alter_column('tasks', 'completed', nullable=False)

    # Drop new column
    op.drop_column('tasks', 'status')
```

## Troubleshooting

### Migration fails with "relation already exists"

```bash
# Check current database version
alembic current

# Check migration history
alembic history

# If out of sync, stamp database with current version
alembic stamp head
```

### Migration fails with "column does not exist"

- Review the migration order
- Ensure all dependencies are applied
- Check if previous migration was rolled back

### Need to fix a failed migration

```bash
# Rollback the failed migration
alembic downgrade -1

# Fix the migration file
# Re-apply the migration
alembic upgrade +1
```

### Database and migrations out of sync

```bash
# Check current version
alembic current

# Check what Alembic thinks should be applied
alembic history

# Manually stamp database to specific version
alembic stamp <revision_id>
```

## Neon-Specific Considerations

### Connection Pooling

Neon uses NullPool (no connection pooling) in the application, but migrations use the default pool. This is configured in `alembic/env.py`:

```python
connectable = engine_from_config(
    config.get_section(config.config_ini_section, {}),
    prefix="sqlalchemy.",
    poolclass=pool.NullPool,  # Use NullPool for Neon Serverless
)
```

### SSL Requirements

Neon requires SSL connections. Ensure your DATABASE_URL includes:
```
?sslmode=require&channel_binding=require
```

### Branching for Testing

Use Neon's branching feature to test migrations:

1. Create branch: `neon branches create --name test-migration`
2. Get branch endpoint from Neon console
3. Update DATABASE_URL to branch endpoint
4. Run migrations: `alembic upgrade head`
5. Test application with new schema
6. If successful, apply to production
7. Delete test branch: `neon branches delete test-migration`

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Database Migrations

on:
  push:
    branches: [main]

jobs:
  migrate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt

      - name: Run migrations
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
        run: |
          alembic upgrade head
```

## Migration Checklist

Before applying migrations to production:

- [ ] Migration tested on local database
- [ ] Migration tested on Neon branch
- [ ] Downgrade tested and works correctly
- [ ] Migration is idempotent (can run multiple times safely)
- [ ] Indexes created with CONCURRENTLY (if applicable)
- [ ] Data migration tested with production-like data volume
- [ ] Backup created (Neon automatic backups enabled)
- [ ] Team notified of schema changes
- [ ] Application code updated to work with new schema
- [ ] Documentation updated

## Resources

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Neon Documentation](https://neon.tech/docs/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

## Support

For issues or questions:
1. Check this documentation
2. Review Alembic logs: `alembic history --verbose`
3. Check database state: `alembic current`
4. Consult team lead or database administrator
