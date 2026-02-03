# Data Model: Todo Backend Core & Data Layer

**Feature**: 001-backend-core-data
**Created**: 2026-01-20
**Status**: Design Phase

## Overview

This document defines the data model for the Todo Backend Core & Data Layer feature. The model consists of a single entity (Task) that represents todo items with persistent storage in PostgreSQL.

## Entity: Task

### Purpose

Represents a single todo item with metadata including title, description, completion status, timestamps, and user ownership.

### SQLModel Schema Definition

```python
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel

class Task(SQLModel, table=True):
    """
    Task model representing a todo item.

    This model uses SQLModel which combines SQLAlchemy (ORM) and Pydantic (validation).
    The table=True parameter indicates this is a database table model.
    """
    __tablename__ = "tasks"

    # Primary key
    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Unique identifier for the task (auto-generated)"
    )

    # Required fields
    title: str = Field(
        min_length=1,
        max_length=200,
        description="Task title (required, non-empty)"
    )

    completed: bool = Field(
        default=False,
        description="Completion status (defaults to False)"
    )

    user_id: str = Field(
        max_length=100,
        index=True,
        description="User identifier (placeholder for Spec-2, no enforcement)"
    )

    # Optional fields
    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Optional detailed description"
    )

    # Timestamps (auto-managed)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when task was created (UTC)"
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
        description="Timestamp when task was last updated (UTC)"
    )

    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "completed": False,
                "user_id": "user123",
                "created_at": "2026-01-20T10:30:00Z",
                "updated_at": "2026-01-20T10:30:00Z"
            }
        }
```

## Field Specifications

| Field | Type | Constraints | Default | Description |
|-------|------|-------------|---------|-------------|
| `id` | Integer | Primary key, auto-increment | Auto-generated | Unique identifier |
| `title` | String | Required, 1-200 chars, non-empty | None | Task title |
| `description` | String | Optional, max 1000 chars, nullable | NULL | Detailed description |
| `completed` | Boolean | Required | False | Completion status |
| `created_at` | DateTime | Required, auto-generated, UTC | Current UTC time | Creation timestamp |
| `updated_at` | DateTime | Required, auto-updated, UTC | Current UTC time | Last update timestamp |
| `user_id` | String | Required, max 100 chars, indexed | None | User identifier (placeholder) |

## Database Indexes

### Primary Index
- **Index Name**: `pk_tasks`
- **Type**: Primary Key
- **Column**: `id`
- **Purpose**: Unique identification and fast lookups by ID

### User Index
- **Index Name**: `idx_tasks_user_id`
- **Type**: B-tree
- **Column**: `user_id`
- **Purpose**: Fast filtering by user (for Spec-2 authentication)

### Composite Index
- **Index Name**: `idx_tasks_user_created`
- **Type**: B-tree
- **Columns**: `(user_id, created_at)`
- **Purpose**: Efficient listing of user's tasks ordered by creation time

## Validation Rules

### Title Validation
- **Rule**: Must not be empty or whitespace-only
- **Implementation**: `min_length=1` in SQLModel Field
- **Error**: 422 Unprocessable Entity with validation details

### Description Validation
- **Rule**: Optional, but if provided must not exceed 1000 characters
- **Implementation**: `max_length=1000` in SQLModel Field
- **Error**: 422 Unprocessable Entity if too long

### User ID Validation
- **Rule**: Required, max 100 characters
- **Implementation**: `max_length=100` in SQLModel Field
- **Note**: No format validation in Spec-1 (placeholder only)

## State Transitions

### Task Creation
```
Initial State: None (task doesn't exist)
Action: POST /api/{user_id}/tasks
Result:
  - id: Auto-generated
  - title: From request
  - description: From request or NULL
  - completed: False
  - created_at: Current UTC time
  - updated_at: Current UTC time
  - user_id: From URL path
```

### Task Update
```
Initial State: Task exists
Action: PUT /api/{user_id}/tasks/{id}
Result:
  - id: Unchanged
  - title: Updated from request
  - description: Updated from request
  - completed: Updated from request (optional)
  - created_at: Unchanged
  - updated_at: Refreshed to current UTC time
  - user_id: Unchanged
```

### Task Completion Toggle
```
Initial State: Task exists with completed=X
Action: PATCH /api/{user_id}/tasks/{id}/complete
Result:
  - id: Unchanged
  - title: Unchanged
  - description: Unchanged
  - completed: Toggled (!X)
  - created_at: Unchanged
  - updated_at: Refreshed to current UTC time
  - user_id: Unchanged
```

### Task Deletion
```
Initial State: Task exists
Action: DELETE /api/{user_id}/tasks/{id}
Result: Task removed from database (hard delete)
```

## Pydantic Schemas (Request/Response)

### TaskCreate (Request Schema for POST)
```python
from pydantic import BaseModel, Field
from typing import Optional

class TaskCreate(BaseModel):
    """Schema for creating a new task"""
    title: str = Field(
        min_length=1,
        max_length=200,
        description="Task title"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Optional task description"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Buy groceries",
                "description": "Milk, eggs, bread"
            }
        }
```

### TaskUpdate (Request Schema for PUT)
```python
class TaskUpdate(BaseModel):
    """Schema for updating an existing task"""
    title: str = Field(
        min_length=1,
        max_length=200,
        description="Task title"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Optional task description"
    )
    completed: Optional[bool] = Field(
        default=None,
        description="Completion status"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Buy groceries",
                "description": "Milk, eggs, bread, cheese",
                "completed": False
            }
        }
```

### TaskResponse (Response Schema for all endpoints)
```python
from datetime import datetime

class TaskResponse(BaseModel):
    """Schema for task responses"""
    id: int
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime
    user_id: str

    class Config:
        from_attributes = True  # Enable ORM mode
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "completed": False,
                "created_at": "2026-01-20T10:30:00Z",
                "updated_at": "2026-01-20T10:30:00Z",
                "user_id": "user123"
            }
        }
```

## Database Migration

### Initial Migration (Create Table)

```sql
-- Migration: 001_create_tasks_table
-- Created: 2026-01-20

CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL CHECK (LENGTH(title) > 0),
    description VARCHAR(1000),
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    user_id VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create index on user_id for filtering
CREATE INDEX idx_tasks_user_id ON tasks(user_id);

-- Create composite index for efficient user task listing
CREATE INDEX idx_tasks_user_created ON tasks(user_id, created_at);

-- Create trigger to auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_tasks_updated_at
    BEFORE UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

## Data Integrity Constraints

### Application-Level Constraints
- Title must not be empty (enforced by Pydantic validation)
- Description length must not exceed 1000 characters (enforced by Pydantic)
- User ID must be provided (enforced by API path parameter)

### Database-Level Constraints
- Primary key uniqueness on `id`
- NOT NULL constraints on required fields
- CHECK constraint on title length
- Default values for `completed`, `created_at`, `updated_at`

## Future Considerations (Spec-2)

### User Relationship
When authentication is added in Spec-2:
- Add foreign key constraint: `user_id REFERENCES users(id)`
- Add ON DELETE CASCADE to remove tasks when user is deleted
- Enforce user_id validation against authenticated user

### Additional Indexes
Consider adding indexes for:
- `completed` status for filtering completed/incomplete tasks
- `created_at` for sorting by creation date
- Full-text search on `title` and `description` if search is added

## Testing Considerations

### Unit Tests
- Test Task model creation with valid data
- Test validation errors for invalid data (empty title, too long description)
- Test default values (completed=False, timestamps)
- Test timestamp auto-update behavior

### Integration Tests
- Test database persistence (create, read, update, delete)
- Test index usage for queries
- Test constraint enforcement
- Test concurrent updates to same task

---

**Status**: ✅ Design Complete - Ready for implementation
