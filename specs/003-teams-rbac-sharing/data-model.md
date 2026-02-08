# Data Model: Teams, RBAC, and Task Sharing

**Feature**: 003-teams-rbac-sharing
**Date**: 2026-02-04
**Status**: Complete

## Overview

This document defines the data model for multi-user collaboration with team-based task management, role-based access control, and direct task sharing. The design extends the existing data model from Spec 001 and Spec 002 while maintaining 100% backward compatibility.

## Entity Relationship Diagram

```
┌─────────────┐
│    User     │ (Existing - Spec 002)
│─────────────│
│ id (PK)     │
│ email       │
│ password_hash│
│ created_at  │
│ updated_at  │
└──────┬──────┘
       │
       │ 1:N (owns tasks)
       │
       ├──────────────────────────────────┐
       │                                  │
       │ 1:N (owns teams)                 │ 1:N (team memberships)
       │                                  │
┌──────▼──────┐                    ┌──────▼──────────┐
│    Team     │                    │  TeamMember     │
│─────────────│                    │─────────────────│
│ id (PK)     │◄───────────────────│ id (PK)         │
│ name (UQ)   │ 1:N (has members)  │ team_id (FK)    │
│ description │                    │ user_id (FK)    │
│ owner_id(FK)│                    │ role (ENUM)     │
│ created_at  │                    │ joined_at       │
│ updated_at  │                    └─────────────────┘
└──────┬──────┘                    UNIQUE(team_id, user_id)
       │
       │ 1:N (has tasks)
       │
┌──────▼──────┐
│    Task     │ (Extended - Spec 001)
│─────────────│
│ id (PK)     │
│ title       │
│ description │
│ completed   │
│ user_id(FK) │───────┐
│ team_id(FK) │       │ 1:N (shared with users)
│ created_at  │       │
│ updated_at  │       │
└──────┬──────┘       │
       │              │
       │              │
       │              │
       │         ┌────▼────────────┐
       └─────────►   TaskShare     │
         1:N      │─────────────────│
                  │ id (PK)         │
                  │ task_id (FK)    │
                  │ shared_with_user_id (FK)
                  │ shared_by_user_id (FK)
                  │ permission (ENUM)
                  │ shared_at       │
                  └─────────────────┘
                  UNIQUE(task_id, shared_with_user_id)
```

## Entities

### 1. Team (NEW)

**Purpose**: Represents a collaboration group that can own tasks and have multiple members with different roles.

**Table Name**: `teams`

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique identifier for the team |
| name | VARCHAR(255) | NOT NULL, UNIQUE | Team name (must be unique across all teams) |
| description | TEXT | NULLABLE | Optional team description |
| owner_id | UUID | NOT NULL, FOREIGN KEY → users.id | User who owns the team (has ultimate authority) |
| created_at | TIMESTAMP | NOT NULL | When the team was created |
| updated_at | TIMESTAMP | NOT NULL | When the team was last modified |

**Relationships**:
- **owner**: Many-to-One with User (owner_id → users.id)
- **members**: One-to-Many with TeamMember (team.id ← team_members.team_id)
- **tasks**: One-to-Many with Task (team.id ← tasks.team_id)

**Constraints**:
- `name` must be unique across all teams
- `owner_id` must reference a valid user
- ON DELETE CASCADE: When team is deleted, all team_members are deleted
- ON DELETE SET NULL: When team is deleted, tasks.team_id is set to NULL (converts to personal tasks)

**Validation Rules**:
- Name: 1-255 characters, non-empty after trimming
- Description: Optional, max 5000 characters
- Owner must be a valid, existing user

**State Transitions**:
- Created → Active (on creation)
- Active → Deleted (on deletion)
- No soft delete; deletion is permanent with cascading effects

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, List

class Team(SQLModel, table=True):
    __tablename__ = "teams"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(max_length=255, unique=True, index=True)
    description: Optional[str] = Field(default=None, max_length=5000)
    owner_id: UUID = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    owner: "User" = Relationship(back_populates="owned_teams")
    members: List["TeamMember"] = Relationship(back_populates="team", cascade_delete=True)
    tasks: List["Task"] = Relationship(back_populates="team")
```

---

### 2. TeamMember (NEW)

**Purpose**: Junction table representing the many-to-many relationship between users and teams, with an additional role attribute for RBAC.

**Table Name**: `team_members`

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique identifier for the membership record |
| team_id | UUID | NOT NULL, FOREIGN KEY → teams.id | Team this membership belongs to |
| user_id | UUID | NOT NULL, FOREIGN KEY → users.id | User who is a member |
| role | ENUM | NOT NULL, CHECK IN ('owner', 'admin', 'member', 'viewer') | User's role in the team |
| joined_at | TIMESTAMP | NOT NULL | When the user joined the team |

**Relationships**:
- **team**: Many-to-One with Team (team_id → teams.id)
- **user**: Many-to-One with User (user_id → users.id)

**Constraints**:
- UNIQUE(team_id, user_id): A user can only have one membership per team
- ON DELETE CASCADE: When team is deleted, all memberships are deleted
- ON DELETE CASCADE: When user is deleted, all their memberships are deleted
- CHECK: role must be one of: 'owner', 'admin', 'member', 'viewer'

**Validation Rules**:
- team_id must reference an existing team
- user_id must reference an existing user
- role must be a valid TeamRole enum value
- Each team must have exactly one owner (enforced at application level)

**Role Definitions**:

| Role | Permissions |
|------|-------------|
| **owner** | Full control: manage team, manage members, assign all roles, create/edit/delete all tasks, delete team |
| **admin** | Team management: manage members, assign member/viewer roles, create/edit/delete all tasks |
| **member** | Task contributor: create tasks, edit own tasks, view all tasks |
| **viewer** | Read-only: view all tasks, no modifications |

**SQLModel Definition**:
```python
from enum import Enum

class TeamRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"

class TeamMember(SQLModel, table=True):
    __tablename__ = "team_members"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    team_id: UUID = Field(foreign_key="teams.id", index=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    role: TeamRole = Field(sa_column=Column(Enum(TeamRole)))
    joined_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    team: Team = Relationship(back_populates="members")
    user: "User" = Relationship(back_populates="team_memberships")

    class Config:
        # Ensure unique team-user combination
        table_args = (
            UniqueConstraint('team_id', 'user_id', name='uq_team_user'),
        )
```

---

### 3. TaskShare (NEW)

**Purpose**: Represents direct sharing of a task with a specific user, enabling collaboration outside team context.

**Table Name**: `task_shares`

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique identifier for the share record |
| task_id | UUID | NOT NULL, FOREIGN KEY → tasks.id | Task being shared |
| shared_with_user_id | UUID | NOT NULL, FOREIGN KEY → users.id | User receiving access |
| shared_by_user_id | UUID | NOT NULL, FOREIGN KEY → users.id | User who shared the task |
| permission | ENUM | NOT NULL, CHECK IN ('view', 'edit') | Level of access granted |
| shared_at | TIMESTAMP | NOT NULL | When the task was shared |

**Relationships**:
- **task**: Many-to-One with Task (task_id → tasks.id)
- **shared_with_user**: Many-to-One with User (shared_with_user_id → users.id)
- **shared_by_user**: Many-to-One with User (shared_by_user_id → users.id)

**Constraints**:
- UNIQUE(task_id, shared_with_user_id): A task can only be shared once with each user
- ON DELETE CASCADE: When task is deleted, all shares are deleted
- ON DELETE CASCADE: When user is deleted, all shares involving them are deleted
- CHECK: permission must be one of: 'view', 'edit'

**Validation Rules**:
- task_id must reference an existing task
- shared_with_user_id must reference an existing user
- shared_by_user_id must reference an existing user (typically the task owner)
- Cannot share a task with yourself (enforced at application level)
- Only task owner can share (enforced at application level)

**Permission Definitions**:

| Permission | Capabilities |
|------------|--------------|
| **view** | Read-only access: view task details, cannot modify |
| **edit** | Modify access: view and update task details, cannot delete |

**SQLModel Definition**:
```python
class SharePermission(str, Enum):
    VIEW = "view"
    EDIT = "edit"

class TaskShare(SQLModel, table=True):
    __tablename__ = "task_shares"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    task_id: UUID = Field(foreign_key="tasks.id", index=True)
    shared_with_user_id: UUID = Field(foreign_key="users.id", index=True)
    shared_by_user_id: UUID = Field(foreign_key="users.id")
    permission: SharePermission = Field(sa_column=Column(Enum(SharePermission)))
    shared_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    task: "Task" = Relationship(back_populates="shares")
    shared_with_user: "User" = Relationship(
        back_populates="received_shares",
        sa_relationship_kwargs={"foreign_keys": "[TaskShare.shared_with_user_id]"}
    )
    shared_by_user: "User" = Relationship(
        back_populates="given_shares",
        sa_relationship_kwargs={"foreign_keys": "[TaskShare.shared_by_user_id]"}
    )

    class Config:
        table_args = (
            UniqueConstraint('task_id', 'shared_with_user_id', name='uq_task_share'),
        )
```

---

### 4. Task (EXTENDED)

**Purpose**: Existing task entity extended to support team ownership while maintaining backward compatibility with personal tasks.

**Table Name**: `tasks`

**New Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| team_id | UUID | NULLABLE, FOREIGN KEY → teams.id | Optional team ownership (NULL = personal task) |

**Existing Fields** (from Spec 001):
- id (UUID, PRIMARY KEY)
- title (VARCHAR)
- description (TEXT, NULLABLE)
- completed (BOOLEAN)
- user_id (UUID, FOREIGN KEY → users.id)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)

**New Relationships**:
- **team**: Many-to-One with Team (team_id → teams.id) - NULLABLE
- **shares**: One-to-Many with TaskShare (task.id ← task_shares.task_id)

**Constraints**:
- team_id is NULLABLE (NULL means personal task)
- ON DELETE SET NULL: When team is deleted, team_id is set to NULL (converts to personal task)
- Index on team_id for efficient team task queries

**Validation Rules**:
- If team_id is set, user must be a member of that team (enforced at application level)
- Personal tasks (team_id = NULL) can still be shared directly

**Access Control Logic**:
```python
def can_access_task(user: User, task: Task, db: Session) -> Tuple[bool, str]:
    """
    Determine if user can access task and return access type.
    Returns: (can_access: bool, access_type: str)
    """
    # 1. Owner always has full access
    if task.user_id == user.id:
        return (True, "owner")

    # 2. Team member access (if task is team-owned)
    if task.team_id:
        member = db.query(TeamMember).filter(
            TeamMember.team_id == task.team_id,
            TeamMember.user_id == user.id
        ).first()
        if member:
            return (True, f"team_{member.role.value}")

    # 3. Direct share access
    share = db.query(TaskShare).filter(
        TaskShare.task_id == task.id,
        TaskShare.shared_with_user_id == user.id
    ).first()
    if share:
        return (True, f"shared_{share.permission.value}")

    # 4. No access
    return (False, None)
```

**Extended SQLModel Definition**:
```python
class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str = Field(max_length=255)
    description: Optional[str] = Field(default=None, max_length=5000)
    completed: bool = Field(default=False)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    team_id: Optional[UUID] = Field(default=None, foreign_key="teams.id", index=True)  # NEW
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: "User" = Relationship(back_populates="tasks")
    team: Optional[Team] = Relationship(back_populates="tasks")  # NEW
    shares: List[TaskShare] = Relationship(back_populates="task", cascade_delete=True)  # NEW
```

---

### 5. User (EXISTING - No Changes)

**Purpose**: Existing user entity from Spec 002. No modifications needed, but new relationships are added.

**Table Name**: `users`

**New Relationships** (added to existing model):
- **owned_teams**: One-to-Many with Team (user.id ← teams.owner_id)
- **team_memberships**: One-to-Many with TeamMember (user.id ← team_members.user_id)
- **received_shares**: One-to-Many with TaskShare (user.id ← task_shares.shared_with_user_id)
- **given_shares**: One-to-Many with TaskShare (user.id ← task_shares.shared_by_user_id)

**Extended SQLModel Definition**:
```python
class User(SQLModel, table=True):
    __tablename__ = "users"

    # Existing fields (from Spec 002)
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Existing relationships
    tasks: List["Task"] = Relationship(back_populates="user")

    # NEW relationships (this feature)
    owned_teams: List[Team] = Relationship(back_populates="owner")
    team_memberships: List[TeamMember] = Relationship(back_populates="user")
    received_shares: List[TaskShare] = Relationship(
        back_populates="shared_with_user",
        sa_relationship_kwargs={"foreign_keys": "[TaskShare.shared_with_user_id]"}
    )
    given_shares: List[TaskShare] = Relationship(
        back_populates="shared_by_user",
        sa_relationship_kwargs={"foreign_keys": "[TaskShare.shared_by_user_id]"}
    )
```

## Database Indexes

**Required Indexes** (for query performance):

```sql
-- Team lookups
CREATE INDEX idx_teams_owner_id ON teams(owner_id);
CREATE INDEX idx_teams_name ON teams(name);  -- Already unique, but explicit index

-- Team member lookups
CREATE INDEX idx_team_members_team_id ON team_members(team_id);
CREATE INDEX idx_team_members_user_id ON team_members(user_id);
CREATE INDEX idx_team_members_role ON team_members(role);  -- For role-based queries

-- Task share lookups
CREATE INDEX idx_task_shares_task_id ON task_shares(task_id);
CREATE INDEX idx_task_shares_shared_with_user_id ON task_shares(shared_with_user_id);
CREATE INDEX idx_task_shares_shared_by_user_id ON task_shares(shared_by_user_id);

-- Task team lookups (NEW)
CREATE INDEX idx_tasks_team_id ON tasks(team_id);
```

## Migration Strategy

### Phase 1: Add New Tables
```sql
-- Create teams table
CREATE TABLE teams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create team_members table
CREATE TABLE team_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('owner', 'admin', 'member', 'viewer')),
    joined_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(team_id, user_id)
);

-- Create task_shares table
CREATE TABLE task_shares (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    shared_with_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    shared_by_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    permission VARCHAR(10) NOT NULL CHECK (permission IN ('view', 'edit')),
    shared_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(task_id, shared_with_user_id)
);
```

### Phase 2: Extend Existing Tables
```sql
-- Add team_id to tasks table
ALTER TABLE tasks ADD COLUMN team_id UUID REFERENCES teams(id) ON DELETE SET NULL;
CREATE INDEX idx_tasks_team_id ON tasks(team_id);
```

### Phase 3: Create Indexes
```sql
-- (Indexes listed in "Database Indexes" section above)
```

### Rollback Strategy
```sql
-- Remove team_id from tasks
ALTER TABLE tasks DROP COLUMN team_id;

-- Drop new tables (in reverse order of dependencies)
DROP TABLE task_shares;
DROP TABLE team_members;
DROP TABLE teams;
```

## Data Integrity Rules

### Application-Level Constraints

1. **Single Owner Rule**: Each team must have exactly one owner
   - Enforced by checking role='owner' count before role changes
   - Ownership transfer is atomic (demote current owner, promote new owner in transaction)

2. **Self-Share Prevention**: Users cannot share tasks with themselves
   - Enforced by checking shared_with_user_id != task.user_id

3. **Owner-Only Sharing**: Only task owners can share tasks
   - Enforced by checking current_user.id == task.user_id before creating share

4. **Team Membership Requirement**: Users creating team tasks must be team members
   - Enforced by checking team membership before allowing team_id assignment

5. **Role Hierarchy**: Admins cannot change owner roles
   - Enforced by checking current_user.role before allowing role changes

### Database-Level Constraints

1. **Foreign Key Integrity**: All foreign keys have ON DELETE CASCADE or SET NULL
2. **Unique Constraints**: Prevent duplicate memberships and shares
3. **Check Constraints**: Validate enum values (roles, permissions)
4. **Not Null Constraints**: Ensure required fields are always populated

## Query Patterns

### Common Queries

**Get all teams for a user**:
```sql
SELECT t.* FROM teams t
JOIN team_members tm ON t.id = tm.team_id
WHERE tm.user_id = :user_id
ORDER BY t.created_at DESC;
```

**Get all tasks accessible to a user**:
```sql
-- Personal tasks
SELECT * FROM tasks WHERE user_id = :user_id

UNION

-- Team tasks
SELECT t.* FROM tasks t
JOIN team_members tm ON t.team_id = tm.team_id
WHERE tm.user_id = :user_id

UNION

-- Shared tasks
SELECT t.* FROM tasks t
JOIN task_shares ts ON t.id = ts.task_id
WHERE ts.shared_with_user_id = :user_id;
```

**Check if user can edit a task**:
```sql
-- Owner check
SELECT 1 FROM tasks WHERE id = :task_id AND user_id = :user_id

UNION

-- Team admin/owner check
SELECT 1 FROM tasks t
JOIN team_members tm ON t.team_id = tm.team_id
WHERE t.id = :task_id AND tm.user_id = :user_id
  AND tm.role IN ('owner', 'admin')

UNION

-- Edit share check
SELECT 1 FROM task_shares
WHERE task_id = :task_id AND shared_with_user_id = :user_id
  AND permission = 'edit';
```

## Conclusion

The data model extends the existing schema with three new tables and one extended table, maintaining full backward compatibility. All relationships are properly defined with foreign keys, unique constraints, and appropriate cascading behaviors. The design supports efficient querying through strategic indexing and enables flexible permission management through the RBAC system and direct sharing mechanism.

**Status**: Data model complete. Ready for API contract generation.
