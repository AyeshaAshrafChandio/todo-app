# How to Complete T012: Database Migration

## Overview

The migration script is ready and tested. It only needs a valid database connection to execute.

## Prerequisites

1. **Neon PostgreSQL Database**: Active Neon project with connection string
2. **psycopg3 Driver**: Already installed via `psycopg[binary]>=3.2.0`

## Connection String Format

**IMPORTANT**: The project uses psycopg3, which requires a specific connection string format.

### Correct Format (psycopg3)
```bash
postgresql+psycopg://username:password@host:port/database?sslmode=require
```

### Example
```bash
# Neon connection string (correct format)
DATABASE_URL="postgresql+psycopg://neondb_owner:npg_rt6ehgLcaHw2@ep-curly-lab-ahyp95q8-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require"
```

### Common Mistake
```bash
# This will NOT work (missing +psycopg)
DATABASE_URL="postgresql://neondb_owner:password@host/database"
```

## Step-by-Step Instructions

### Option 1: Using Environment Variables (Recommended)

```bash
# Navigate to project root
cd C:\Users\Ali Haider\hakathon2\phase2

# Set environment variables (Windows PowerShell)
$env:DATABASE_URL="postgresql+psycopg://your-neon-connection-string"
$env:BETTER_AUTH_SECRET="your-secret-key"

# Run migration
python backend/migrations/003_add_teams_rbac_sharing.py
```

### Option 2: Using .env File

1. Update `backend/.env` with correct format:
```env
DATABASE_URL=postgresql+psycopg://neondb_owner:password@host/database?sslmode=require
BETTER_AUTH_SECRET=your-secret-key
```

2. Run migration:
```bash
cd C:\Users\Ali Haider\hakathon2\phase2
python backend/migrations/003_add_teams_rbac_sharing.py
```

### Option 3: Test on Neon Branch First (Best Practice)

```bash
# 1. Create a test branch in Neon
neon branches create --name migration-test

# 2. Get the branch connection string
# (Neon will provide a connection string for the branch)

# 3. Set environment variables with branch connection
$env:DATABASE_URL="postgresql+psycopg://branch-connection-string"
$env:BETTER_AUTH_SECRET="test-secret"

# 4. Run migration on branch
python backend/migrations/003_add_teams_rbac_sharing.py

# 5. Verify success, then run on main database
```

## Expected Output

When the migration runs successfully, you should see:

```
======================================================================
Phase 3 Database Migration: Teams, RBAC, and Task Sharing
======================================================================

Step 1: Verifying database connection...
[SUCCESS] Database connection verified

Step 2: Checking prerequisites (Phase 2 migration)...
[SUCCESS] Prerequisites verified

Step 3: Checking existing tables...
   - teams table exists: False
   - team_members table exists: False
   - task_shares table exists: False
   - tasks.team_id column exists: False

Step 4: Found X existing tasks
   [INFO] These tasks will remain as personal tasks (team_id = NULL)

Step 5: Applying schema changes...
[SUCCESS] Schema changes applied successfully

Step 6: Verifying migration...

   Teams table columns:
      - id: uuid (nullable: NO)
      - name: character varying (nullable: NO)
      - description: text (nullable: YES)
      - owner_id: uuid (nullable: NO)
      - created_at: timestamp without time zone (nullable: NO)
      - updated_at: timestamp without time zone (nullable: NO)

   TeamMembers table columns:
      - id: uuid (nullable: NO)
      - team_id: uuid (nullable: NO)
      - user_id: uuid (nullable: NO)
      - role: character varying (nullable: NO)
      - joined_at: timestamp without time zone (nullable: NO)

   TaskShares table columns:
      - id: uuid (nullable: NO)
      - task_id: integer (nullable: NO)
      - shared_with_user_id: uuid (nullable: NO)
      - shared_by_user_id: uuid (nullable: NO)
      - permission: character varying (nullable: NO)
      - shared_at: timestamp without time zone (nullable: NO)

   Tasks table team_id column:
      - team_id: uuid (nullable: YES)

   Foreign key constraints:
      - teams.owner_id → users.id
      - team_members.team_id → teams.id
      - team_members.user_id → users.id
      - task_shares.task_id → tasks.id
      - task_shares.shared_with_user_id → users.id
      - task_shares.shared_by_user_id → users.id
      - tasks.team_id → teams.id

   Unique constraints:
      - teams.name (uq_teams_name)
      - team_members(team_id, user_id) (uq_team_user)
      - task_shares(task_id, shared_with_user_id) (uq_task_share)

   Indexes created:
      - idx_teams_owner_id on teams
      - idx_teams_name on teams
      - idx_team_members_team_id on team_members
      - idx_team_members_user_id on team_members
      - idx_team_members_role on team_members
      - idx_task_shares_task_id on task_shares
      - idx_task_shares_shared_with_user_id on task_shares
      - idx_task_shares_shared_by_user_id on task_shares
      - idx_tasks_team_id on tasks

[SUCCESS] Migration verification complete

======================================================================
Migration Summary
======================================================================
[SUCCESS] Teams table created
[SUCCESS] TeamMembers table created
[SUCCESS] TaskShares table created
[SUCCESS] Tasks table extended with team_id foreign key
[SUCCESS] All foreign key constraints created
[SUCCESS] All unique constraints created
[SUCCESS] All indexes created for performance
[SUCCESS] Existing task data preserved (team_id = NULL)

Next steps:
1. Implement team management endpoints (POST/GET/PATCH/DELETE /api/teams)
2. Implement team member management endpoints
3. Implement task sharing endpoints
4. Update task endpoints to support team_id parameter
5. Implement permission checking middleware
======================================================================
```

## Verification After Migration

After successful migration, verify the schema:

```bash
# Connect to your Neon database
psql "postgresql+psycopg://your-connection-string"

# Check tables exist
\dt

# Check teams table structure
\d teams

# Check team_members table structure
\d team_members

# Check task_shares table structure
\d task_shares

# Check tasks table has team_id column
\d tasks

# Verify existing tasks are preserved
SELECT COUNT(*) FROM tasks WHERE team_id IS NULL;
```

## Rollback (if needed)

If you need to undo the migration:

```bash
python backend/migrations/003_add_teams_rbac_sharing.py --rollback
```

This will:
- Drop task_shares table
- Drop team_members table
- Drop teams table
- Remove team_id column from tasks table

## Troubleshooting

### Error: "DATABASE_URL environment variable is not set"
**Solution**: Set the DATABASE_URL environment variable before running the script.

### Error: "ModuleNotFoundError: No module named 'psycopg2'"
**Solution**: The connection string format is incorrect. Use `postgresql+psycopg://` instead of `postgresql://`.

### Error: "Prerequisites not met"
**Solution**: Phase 2 migration must be complete first. Verify users and tasks tables exist.

### Error: "Connection refused" or "Connection timeout"
**Solution**:
- Check your Neon database is active
- Verify the connection string is correct
- Ensure your IP is allowed (Neon allows all IPs by default)
- Check SSL mode is set to "require"

## Next Steps After T012

Once the migration is complete:

1. **Verify Backward Compatibility**: Test that existing personal tasks still work
2. **Begin User Story Implementation**: Start with Phase 3 tasks
3. **Implement API Endpoints**: Create team management routes
4. **Add Permission Middleware**: Integrate permission checks into routes
5. **Test Thoroughly**: Verify all permission scenarios work correctly

## Files Involved

- **Migration Script**: `backend/migrations/003_add_teams_rbac_sharing.py`
- **Models**: `backend/app/models/team.py`, `team_member.py`, `task_share.py`
- **Permissions**: `backend/app/middleware/permissions.py`
- **Configuration**: `backend/.env` (update with correct connection string)

---

**Status**: Ready to execute
**Estimated Time**: 30-60 seconds
**Risk Level**: Low (includes rollback capability)
**Backward Compatible**: Yes (existing tasks preserved)
