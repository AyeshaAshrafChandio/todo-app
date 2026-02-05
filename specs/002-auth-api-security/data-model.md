# Data Model: Authentication & API Security

**Feature**: 002-auth-api-security
**Date**: 2026-02-04
**Status**: Completed

This document defines the data entities, relationships, and validation rules for the authentication and authorization system.

## Entity Definitions

### User Entity

**Purpose**: Represents an authenticated user account in the system.

**Attributes**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID or String | Primary Key, Auto-generated | Unique identifier for the user |
| email | String | Unique, Not Null, Max 255 chars, Email format | User's email address (used for login) |
| password_hash | String | Not Null, Min 60 chars | Bcrypt-hashed password (never store plaintext) |
| created_at | DateTime | Not Null, Auto-generated (UTC) | Timestamp when user account was created |
| updated_at | DateTime | Not Null, Auto-updated (UTC) | Timestamp when user account was last modified |

**Validation Rules**:
- Email must be valid format (RFC 5322)
- Email must be unique (case-insensitive)
- Password must be at least 8 characters before hashing
- Password must contain at least one uppercase, one lowercase, one digit
- Password hash uses bcrypt with cost factor 12

**Indexes**:
- Primary key on `id`
- Unique index on `email` (case-insensitive)

**SQLModel Implementation**:
```python
from sqlmodel import Field, SQLModel
from datetime import datetime
from typing import Optional
import uuid

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        description="Unique identifier for the user"
    )

    email: str = Field(
        max_length=255,
        unique=True,
        index=True,
        description="User's email address (unique, case-insensitive)"
    )

    password_hash: str = Field(
        min_length=60,
        description="Bcrypt-hashed password"
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when user was created (UTC)"
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
        description="Timestamp when user was last updated (UTC)"
    )
```

**Relationships**:
- One-to-Many with Task (one user has many tasks)

---

### Task Entity (Extended from Spec 1)

**Purpose**: Represents a todo item with user ownership.

**Changes from Spec 1**:
- ✅ Add `user_id` field as foreign key to User
- ✅ Make `user_id` nullable to support existing tasks (migration strategy)
- ✅ Add foreign key constraint to enforce referential integrity

**Attributes**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | Primary Key, Auto-generated | Unique identifier for the task |
| title | String | Not Null, Min 1 char, Max 200 chars | Task title |
| description | String | Nullable, Max 1000 chars | Optional detailed description |
| completed | Boolean | Not Null, Default False | Completion status |
| user_id | String (UUID) | **Foreign Key to User.id**, Nullable, Indexed | Owner of the task |
| created_at | DateTime | Not Null, Auto-generated (UTC) | Timestamp when task was created |
| updated_at | DateTime | Not Null, Auto-updated (UTC) | Timestamp when task was last modified |

**Validation Rules**:
- Title must not be empty or whitespace-only
- Title length: 1-200 characters
- Description length: 0-1000 characters (optional)
- user_id must reference an existing User (if not NULL)
- Completed defaults to False

**Indexes**:
- Primary key on `id`
- Index on `user_id` for efficient filtering
- Composite index on `(user_id, created_at)` for efficient listing

**SQLModel Implementation**:
```python
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime
from typing import Optional

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Unique identifier for the task"
    )

    title: str = Field(
        min_length=1,
        max_length=200,
        description="Task title (required, non-empty)"
    )

    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Optional detailed description"
    )

    completed: bool = Field(
        default=False,
        description="Completion status (defaults to False)"
    )

    user_id: Optional[str] = Field(
        default=None,
        foreign_key="users.id",
        index=True,
        description="Owner of the task (foreign key to User)"
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when task was created (UTC)"
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
        description="Timestamp when task was last updated (UTC)"
    )

    # Relationship (optional, for ORM convenience)
    # user: Optional["User"] = Relationship(back_populates="tasks")
```

**Relationships**:
- Many-to-One with User (many tasks belong to one user)

---

### JWT Token (Logical Entity - Not Stored)

**Purpose**: Represents an authentication session (stateless, not persisted).

**Claims**:

| Claim | Type | Description |
|-------|------|-------------|
| userId | String (UUID) | User's unique identifier |
| email | String | User's email address |
| iat | Integer (Unix timestamp) | Issued at timestamp |
| exp | Integer (Unix timestamp) | Expiration timestamp (iat + 24 hours) |

**Token Structure**:
```json
{
  "userId": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "iat": 1706976000,
  "exp": 1707062400
}
```

**Signing**:
- Algorithm: HS256 (HMAC with SHA-256)
- Secret: `BETTER_AUTH_SECRET` environment variable
- Expiration: 24 hours from issuance

**Validation Rules**:
- Token must have valid signature (verified with BETTER_AUTH_SECRET)
- Token must not be expired (current time < exp)
- Token must contain required claims (userId, email)
- userId must reference an existing User in database

---

## Entity Relationships

```
┌─────────────────┐
│      User       │
│─────────────────│
│ id (PK)         │◄─────┐
│ email (UNIQUE)  │      │
│ password_hash   │      │
│ created_at      │      │
│ updated_at      │      │
└─────────────────┘      │
                         │
                         │ 1:N
                         │
                         │
┌─────────────────┐      │
│      Task       │      │
│─────────────────│      │
│ id (PK)         │      │
│ title           │      │
│ description     │      │
│ completed       │      │
│ user_id (FK)    │──────┘
│ created_at      │
│ updated_at      │
└─────────────────┘
```

**Relationship Rules**:
- One User can have many Tasks (1:N)
- Each Task belongs to at most one User (N:1)
- Tasks with NULL user_id are legacy tasks (from Spec 1, before auth)
- Deleting a User should cascade delete their Tasks (or set user_id to NULL)

---

## State Transitions

### User Account States

```
[New User] ──signup──> [Registered] ──login──> [Authenticated]
                                         │
                                         │ token expires
                                         ▼
                                    [Unauthenticated]
                                         │
                                         │ login
                                         ▼
                                    [Authenticated]
```

**State Descriptions**:
- **New User**: No account exists
- **Registered**: Account created, credentials stored
- **Authenticated**: Valid JWT token issued, can access protected resources
- **Unauthenticated**: No valid token, must login to access protected resources

### Task Ownership States

```
[No Owner] ──assign user──> [Owned by User A]
                                    │
                                    │ user deleted
                                    ▼
                            [No Owner (orphaned)]
```

**State Descriptions**:
- **No Owner**: Task has NULL user_id (legacy task from Spec 1)
- **Owned by User A**: Task has user_id referencing User A
- **Orphaned**: Task's user_id references deleted user (if cascade delete not configured)

---

## Data Validation

### User Validation

**Email Validation**:
```python
import re

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

def validate_email(email: str) -> bool:
    return bool(EMAIL_REGEX.match(email))
```

**Password Validation**:
```python
import re

def validate_password(password: str) -> tuple[bool, str]:
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    return True, "Password is valid"
```

**Password Hashing**:
```python
import bcrypt

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
```

### Task Validation

**Title Validation**:
```python
def validate_task_title(title: str) -> tuple[bool, str]:
    if not title or title.strip() == "":
        return False, "Title cannot be empty"
    if len(title) > 200:
        return False, "Title cannot exceed 200 characters"
    return True, "Title is valid"
```

**User Ownership Validation**:
```python
def validate_task_ownership(task: Task, user_id: str) -> bool:
    """Verify that the task belongs to the authenticated user."""
    return task.user_id == user_id
```

---

## Database Schema (SQL)

### Users Table

```sql
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(60) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX idx_users_email ON users(LOWER(email));
```

### Tasks Table (Modified from Spec 1)

```sql
-- Add user_id column to existing tasks table
ALTER TABLE tasks
ADD COLUMN user_id VARCHAR(36) NULL,
ADD CONSTRAINT fk_tasks_user_id FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_user_created ON tasks(user_id, created_at);
```

---

## Migration Strategy

### Step 1: Create Users Table
```python
# Run during database initialization
from app.models.user import User
SQLModel.metadata.create_all(engine)
```

### Step 2: Add user_id to Tasks Table
```python
# SQLModel will automatically add the column when Task model is updated
# Existing tasks will have user_id = NULL
```

### Step 3: Handle Legacy Tasks
```python
# Option A: Assign to system user
system_user = User(email="system@todo.app", password_hash="...")
db.add(system_user)
db.commit()

# Update legacy tasks
db.exec(
    update(Task)
    .where(Task.user_id == None)
    .values(user_id=system_user.id)
)

# Option B: Leave as NULL and filter them out in queries
# (Recommended for this implementation)
```

---

## Query Patterns

### Get Tasks for User
```python
def get_tasks_by_user(db: Session, user_id: str) -> List[Task]:
    return db.exec(
        select(Task)
        .where(Task.user_id == user_id)
        .order_by(Task.created_at.desc())
    ).all()
```

### Get Single Task with Ownership Check
```python
def get_task_by_id(db: Session, user_id: str, task_id: int) -> Optional[Task]:
    return db.exec(
        select(Task)
        .where(Task.id == task_id)
        .where(Task.user_id == user_id)
    ).first()
```

### Create Task with User Assignment
```python
def create_task(db: Session, user_id: str, task_data: TaskCreate) -> Task:
    task = Task(
        title=task_data.title,
        description=task_data.description,
        user_id=user_id,  # Automatically assign to authenticated user
        completed=False
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task
```

---

## Security Considerations

### Password Security
- ✅ Never store plaintext passwords
- ✅ Use bcrypt with cost factor 12 (balance security and performance)
- ✅ Salt is automatically generated by bcrypt
- ✅ Password validation enforces complexity requirements

### Data Isolation
- ✅ All task queries filter by user_id
- ✅ Foreign key constraint ensures referential integrity
- ✅ Cascade delete removes user's tasks when user is deleted
- ✅ No cross-user data access possible at query level

### Token Security
- ✅ JWT tokens signed with strong secret (BETTER_AUTH_SECRET)
- ✅ Tokens expire after 24 hours
- ✅ Tokens transmitted only via Authorization header (not URL)
- ✅ Token verification on every protected request

---

## Summary

**New Entities**: 1 (User)
**Modified Entities**: 1 (Task - added user_id)
**Logical Entities**: 1 (JWT Token - not persisted)

**Key Relationships**:
- User → Task (1:N)

**Migration Impact**:
- Backward compatible (user_id nullable)
- No data loss
- Existing tasks remain accessible

**Ready for**: API contract generation and implementation
