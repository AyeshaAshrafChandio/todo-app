# Data Model: MCP Backend Data & Dashboard

**Feature**: 008-mcp-backend-dashboard
**Date**: 2026-02-07
**Status**: Complete

## Entity Definitions

### 1. Task

**Purpose**: Represents a todo item that users can create, update, and complete.

**Fields**:
- `id` (Integer, Primary Key): Unique identifier for the task
- `user_id` (Integer, Foreign Key → users.id): Owner of the task
- `title` (String, max 200 chars, required): Task title
- `description` (String, max 1000 chars, optional): Detailed description
- `status` (Enum: 'pending' | 'completed', default 'pending'): Task completion status
- `created_at` (DateTime, auto): Timestamp when task was created
- `updated_at` (DateTime, auto): Timestamp when task was last updated

**Relationships**:
- Belongs to User (many-to-one)
- Can have many TaskShares (one-to-many)

**Validation Rules**:
- `title` must not be empty
- `title` length: 1-200 characters
- `description` length: 0-1000 characters
- `status` must be 'pending' or 'completed'
- `user_id` must reference existing user

**Indexes**:
- `idx_tasks_user_id` on `user_id`
- `idx_tasks_user_status` on `(user_id, status)` (composite)
- `idx_tasks_created_at` on `created_at DESC`

---

### 2. Conversation

**Purpose**: Represents an AI chat conversation session between a user and the assistant.

**Fields**:
- `id` (Integer, Primary Key): Unique identifier for the conversation
- `user_id` (Integer, Foreign Key → users.id): Owner of the conversation
- `created_at` (DateTime, auto): Timestamp when conversation started
- `updated_at` (DateTime, auto): Timestamp when conversation was last updated

**Relationships**:
- Belongs to User (many-to-one)
- Has many Messages (one-to-many)

**Validation Rules**:
- `user_id` must reference existing user

**Indexes**:
- `idx_conversations_user_id` on `user_id`
- `idx_conversations_created_at` on `created_at DESC`

---

### 3. Message

**Purpose**: Represents a single message in a conversation (from user or assistant).

**Fields**:
- `id` (Integer, Primary Key): Unique identifier for the message
- `conversation_id` (Integer, Foreign Key → conversations.id): Parent conversation
- `user_id` (Integer, Foreign Key → users.id): User who owns this conversation
- `role` (Enum: 'user' | 'assistant', required): Who sent the message
- `content` (Text, required): Message content
- `created_at` (DateTime, auto): Timestamp when message was sent

**Relationships**:
- Belongs to Conversation (many-to-one)
- Belongs to User (many-to-one)

**Validation Rules**:
- `conversation_id` must reference existing conversation
- `user_id` must reference existing user
- `role` must be 'user' or 'assistant'
- `content` must not be empty
- `content` length: 1-10000 characters

**Indexes**:
- `idx_messages_conversation_id` on `conversation_id`
- `idx_messages_created_at` on `created_at DESC`

---

### 4. Team

**Purpose**: Represents a group of users collaborating on tasks.

**Fields**:
- `id` (Integer, Primary Key): Unique identifier for the team
- `name` (String, max 100 chars, required): Team name
- `owner_id` (Integer, Foreign Key → users.id): User who created the team
- `created_at` (DateTime, auto): Timestamp when team was created
- `updated_at` (DateTime, auto): Timestamp when team was last updated

**Relationships**:
- Belongs to User (owner, many-to-one)
- Has many TeamMembers (one-to-many)

**Validation Rules**:
- `name` must not be empty
- `name` length: 1-100 characters
- `owner_id` must reference existing user

**Indexes**:
- `idx_teams_owner_id` on `owner_id`

---

### 5. TeamMember

**Purpose**: Represents membership of a user in a team.

**Fields**:
- `id` (Integer, Primary Key): Unique identifier for the membership
- `team_id` (Integer, Foreign Key → teams.id): Team the user belongs to
- `user_id` (Integer, Foreign Key → users.id): User who is a member
- `role` (Enum: 'owner' | 'admin' | 'member', default 'member'): User's role in team
- `created_at` (DateTime, auto): Timestamp when user joined team

**Relationships**:
- Belongs to Team (many-to-one)
- Belongs to User (many-to-one)

**Validation Rules**:
- `team_id` must reference existing team
- `user_id` must reference existing user
- `role` must be 'owner', 'admin', or 'member'
- Unique constraint on `(team_id, user_id)` - user can only be in team once

**Indexes**:
- `idx_team_members_team_id` on `team_id`
- `idx_team_members_user_id` on `user_id`
- Unique index on `(team_id, user_id)`

---

### 6. TaskShare

**Purpose**: Represents a task shared with another user or team.

**Fields**:
- `id` (Integer, Primary Key): Unique identifier for the share
- `task_id` (Integer, Foreign Key → tasks.id): Task being shared
- `shared_with_user_id` (Integer, Foreign Key → users.id): User receiving the share
- `shared_by_user_id` (Integer, Foreign Key → users.id): User who shared the task
- `permission` (Enum: 'view' | 'edit', default 'view'): Access level
- `created_at` (DateTime, auto): Timestamp when task was shared

**Relationships**:
- Belongs to Task (many-to-one)
- Belongs to User (shared_with, many-to-one)
- Belongs to User (shared_by, many-to-one)

**Validation Rules**:
- `task_id` must reference existing task
- `shared_with_user_id` must reference existing user
- `shared_by_user_id` must reference existing user
- `permission` must be 'view' or 'edit'
- `shared_with_user_id` cannot equal `shared_by_user_id` (cannot share with self)
- Unique constraint on `(task_id, shared_with_user_id)` - task can only be shared once per user

**Indexes**:
- `idx_task_shares_task_id` on `task_id`
- `idx_task_shares_shared_with_user_id` on `shared_with_user_id`
- Unique index on `(task_id, shared_with_user_id)`

---

## Entity Relationships Diagram

```
┌─────────────┐
│    User     │
│  (existing) │
└──────┬──────┘
       │
       │ 1:N
       │
       ├──────────────────────────────────────┐
       │                                      │
       ▼                                      ▼
┌─────────────┐                        ┌─────────────┐
│    Task     │                        │Conversation │
│             │                        │             │
│ - id        │                        │ - id        │
│ - user_id   │                        │ - user_id   │
│ - title     │                        │ - created_at│
│ - status    │                        │ - updated_at│
└──────┬──────┘                        └──────┬──────┘
       │                                      │
       │ 1:N                                  │ 1:N
       │                                      │
       ▼                                      ▼
┌─────────────┐                        ┌─────────────┐
│ TaskShare   │                        │   Message   │
│             │                        │             │
│ - task_id   │                        │ - conv_id   │
│ - shared_   │                        │ - user_id   │
│   with_id   │                        │ - role      │
│ - shared_   │                        │ - content   │
│   by_id     │                        └─────────────┘
└─────────────┘

       ┌──────────────┐
       │     Team     │
       │              │
       │ - id         │
       │ - name       │
       │ - owner_id   │
       └──────┬───────┘
              │
              │ 1:N
              │
              ▼
       ┌──────────────┐
       │ TeamMember   │
       │              │
       │ - team_id    │
       │ - user_id    │
       │ - role       │
       └──────────────┘
```

---

## Query Patterns

### Dashboard Statistics Query

**Purpose**: Get task counts for dashboard display

**Query**:
```sql
-- Total tasks
SELECT COUNT(*) FROM tasks WHERE user_id = ?

-- Pending tasks
SELECT COUNT(*) FROM tasks WHERE user_id = ? AND status = 'pending'

-- Completed tasks
SELECT COUNT(*) FROM tasks WHERE user_id = ? AND status = 'completed'

-- Shared tasks (tasks shared with user)
SELECT COUNT(DISTINCT task_id)
FROM task_shares
WHERE shared_with_user_id = ?
```

**Indexes Used**:
- `idx_tasks_user_status` for filtered counts
- `idx_task_shares_shared_with_user_id` for shared tasks

**Performance**: < 50ms with proper indexes

---

### Conversation History Query

**Purpose**: Load conversation with all messages

**Query**:
```sql
-- Get conversation
SELECT * FROM conversations WHERE id = ? AND user_id = ?

-- Get messages in conversation
SELECT * FROM messages
WHERE conversation_id = ?
ORDER BY created_at ASC
```

**Indexes Used**:
- `idx_conversations_user_id` for conversation lookup
- `idx_messages_conversation_id` for message retrieval

**Performance**: < 100ms for conversations with 100+ messages

---

### Team Tasks Query

**Purpose**: Get all tasks visible to user (own + shared + team)

**Query**:
```sql
-- Own tasks
SELECT * FROM tasks WHERE user_id = ?

UNION

-- Shared tasks
SELECT t.* FROM tasks t
JOIN task_shares ts ON t.id = ts.task_id
WHERE ts.shared_with_user_id = ?

UNION

-- Team tasks (if user is in teams)
SELECT t.* FROM tasks t
JOIN task_shares ts ON t.id = ts.task_id
JOIN team_members tm ON ts.shared_with_user_id = tm.user_id
WHERE tm.user_id = ?
```

**Indexes Used**:
- `idx_tasks_user_id` for own tasks
- `idx_task_shares_shared_with_user_id` for shared tasks
- `idx_team_members_user_id` for team membership

**Performance**: < 200ms with proper indexes

---

## State Transitions

### Task Status

```
┌─────────┐
│ pending │ ──────────────────────────────┐
└────┬────┘                               │
     │                                    │
     │ update(status='completed')         │
     │                                    │
     ▼                                    │
┌───────────┐                             │
│ completed │                             │
└───────────┘                             │
     │                                    │
     │ update(status='pending')           │
     │ (reopen task)                      │
     └────────────────────────────────────┘
```

**Rules**:
- Tasks start as 'pending' by default
- Can transition from 'pending' to 'completed'
- Can transition from 'completed' back to 'pending' (reopen)
- No other status values allowed

---

### Conversation Lifecycle

```
┌─────────┐
│ Created │ ──────────────────────────────┐
└────┬────┘                               │
     │                                    │
     │ add_message()                      │
     │                                    │
     ▼                                    │
┌────────┐                                │
│ Active │ ◄──────────────────────────────┘
└────┬───┘
     │
     │ (no explicit close - remains active)
     │
     ▼
┌─────────┐
│ Archived│ (future feature)
└─────────┘
```

**Rules**:
- Conversations are created when first message is sent
- Conversations remain active indefinitely
- Messages can be added to any conversation
- No explicit "close" operation in MVP

---

## Data Isolation Rules

### User-Level Isolation

**Rule**: Users can only access their own data

**Enforcement**:
```sql
-- All queries MUST include user_id filter
SELECT * FROM tasks WHERE user_id = {authenticated_user_id}
SELECT * FROM conversations WHERE user_id = {authenticated_user_id}
```

**Validation**: Security tests verify no cross-user access

---

### Team-Level Isolation

**Rule**: Team members can only access team data

**Enforcement**:
```sql
-- Check team membership before returning data
SELECT * FROM tasks t
JOIN task_shares ts ON t.id = ts.task_id
JOIN team_members tm ON ts.shared_with_user_id = tm.user_id
WHERE tm.user_id = {authenticated_user_id}
  AND tm.team_id = {requested_team_id}
```

**Validation**: Security tests verify no unauthorized team access

---

## Migration Strategy

### Phase 1: Core Tables (US1)
1. Create tasks table (if not exists, or add missing fields)
2. Create conversations table
3. Create messages table
4. Add indexes for core queries

### Phase 2: Collaboration Tables (US2)
5. Create teams table
6. Create team_members table
7. Create task_shares table
8. Add indexes for team queries

### Phase 3: Optimization (US9)
9. Optimize indexes based on query patterns
10. Add composite indexes for common filters

**Rollback**: Each migration must have a down() method to reverse changes

---

## Performance Considerations

### Index Strategy
- Create indexes on foreign keys for JOIN performance
- Create composite indexes for common WHERE clauses
- Use DESC indexes for "recent items" queries
- Monitor index usage with EXPLAIN ANALYZE

### Query Optimization
- Use COUNT(*) instead of fetching all records
- Avoid N+1 queries (use JOINs or batch queries)
- Implement caching for frequently accessed data
- Use database connection pooling

### Scalability
- Partition large tables by user_id if needed (future)
- Archive old conversations to separate table (future)
- Implement read replicas for dashboard queries (future)

---

## Validation Summary

### Required Validations
- All foreign keys must reference existing records
- All enum fields must have valid values
- All required fields must not be null
- All string fields must respect length limits
- All unique constraints must be enforced

### Business Rules
- Users cannot share tasks with themselves
- Users cannot be added to same team twice
- Task status must be 'pending' or 'completed'
- Message role must be 'user' or 'assistant'
- Team member role must be 'owner', 'admin', or 'member'

### Security Rules
- All queries must filter by authenticated user_id
- Team queries must verify team membership
- Shared task queries must verify share exists
- No raw user_id from client (always from JWT token)

---

## Conclusion

The data model supports all 6 user stories with proper relationships, indexes, and validation rules. All entities follow constitutional principles (stateless, secure, isolated). The model is ready for implementation via Alembic migrations.

**Next Steps**:
1. Generate API contracts in contracts/
2. Generate quickstart.md with setup instructions
3. Implement database migrations (Phase 3 tasks)
