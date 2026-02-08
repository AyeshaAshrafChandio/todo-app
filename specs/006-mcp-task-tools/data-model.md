# Data Model: MCP Task Tools

**Feature**: 006-mcp-task-tools
**Date**: 2026-02-06
**Phase**: 1 - Design & Contracts

## Overview

This document defines the tool schemas (input/output) for all 5 MCP tools that enable AI agent interaction with the task system. All schemas use Pydantic models for validation and are designed to be stateless, deterministic, and secure.

## Tool Schemas

### Tool: add_task

**Purpose**: Create a new task for the authenticated user

**Input Schema**:

```python
from pydantic import BaseModel, Field, validator
from typing import Optional
import uuid

class AddTaskInput(BaseModel):
    user_id: str = Field(..., description="User UUID from JWT token")
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field("", max_length=1000, description="Task description (optional)")

    @validator('user_id')
    def validate_user_id(cls, v):
        try:
            uuid.UUID(v)
            return v
        except ValueError:
            raise ValueError("Invalid user_id format (must be UUID)")

    @validator('title')
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "title": "Buy groceries",
                "description": "Milk, eggs, bread"
            }
        }
```

**Output Schema**:

```python
class AddTaskOutput(BaseModel):
    task_id: int = Field(..., description="Created task ID")
    status: str = Field("created", description="Creation status")
    title: str = Field(..., description="Task title")

    class Config:
        json_schema_extra = {
            "example": {
                "task_id": 1,
                "status": "created",
                "title": "Buy groceries"
            }
        }
```

---

### Tool: list_tasks

**Purpose**: Retrieve all tasks for the authenticated user with optional status filtering

**Input Schema**:

```python
from enum import Enum

class TaskStatus(str, Enum):
    ALL = "all"
    PENDING = "pending"
    COMPLETED = "completed"

class ListTasksInput(BaseModel):
    user_id: str = Field(..., description="User UUID from JWT token")
    status: TaskStatus = Field(TaskStatus.ALL, description="Filter by task status")

    @validator('user_id')
    def validate_user_id(cls, v):
        try:
            uuid.UUID(v)
            return v
        except ValueError:
            raise ValueError("Invalid user_id format (must be UUID)")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "all"
            }
        }
```

**Output Schema**:

```python
from typing import List
from datetime import datetime

class TaskItem(BaseModel):
    id: int
    title: str
    description: str
    completed: bool
    created_at: datetime
    updated_at: datetime

class ListTasksOutput(BaseModel):
    tasks: List[TaskItem] = Field(..., description="List of tasks")
    count: int = Field(..., description="Total number of tasks returned")

    class Config:
        json_schema_extra = {
            "example": {
                "tasks": [
                    {
                        "id": 1,
                        "title": "Buy groceries",
                        "description": "Milk, eggs, bread",
                        "completed": False,
                        "created_at": "2026-02-06T10:00:00Z",
                        "updated_at": "2026-02-06T10:00:00Z"
                    }
                ],
                "count": 1
            }
        }
```

---

### Tool: update_task

**Purpose**: Update task details (title, description, completion status)

**Input Schema**:

```python
class TaskUpdates(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="New task title")
    description: Optional[str] = Field(None, max_length=1000, description="New task description")
    completed: Optional[bool] = Field(None, description="New completion status")

    @validator('title')
    def validate_title(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError("Title cannot be empty")
        return v.strip() if v else v

class UpdateTaskInput(BaseModel):
    user_id: str = Field(..., description="User UUID from JWT token")
    task_id: int = Field(..., gt=0, description="Task ID to update")
    updates: TaskUpdates = Field(..., description="Fields to update")

    @validator('user_id')
    def validate_user_id(cls, v):
        try:
            uuid.UUID(v)
            return v
        except ValueError:
            raise ValueError("Invalid user_id format (must be UUID)")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "task_id": 1,
                "updates": {
                    "completed": True
                }
            }
        }
```

**Output Schema**:

```python
class UpdateTaskOutput(BaseModel):
    task_id: int = Field(..., description="Updated task ID")
    status: str = Field("updated", description="Update status")
    task: TaskItem = Field(..., description="Updated task details")

    class Config:
        json_schema_extra = {
            "example": {
                "task_id": 1,
                "status": "updated",
                "task": {
                    "id": 1,
                    "title": "Buy groceries",
                    "description": "Milk, eggs, bread",
                    "completed": True,
                    "created_at": "2026-02-06T10:00:00Z",
                    "updated_at": "2026-02-06T10:05:00Z"
                }
            }
        }
```

---

### Tool: delete_task

**Purpose**: Delete a task owned by the authenticated user

**Input Schema**:

```python
class DeleteTaskInput(BaseModel):
    user_id: str = Field(..., description="User UUID from JWT token")
    task_id: int = Field(..., gt=0, description="Task ID to delete")

    @validator('user_id')
    def validate_user_id(cls, v):
        try:
            uuid.UUID(v)
            return v
        except ValueError:
            raise ValueError("Invalid user_id format (must be UUID)")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "task_id": 1
            }
        }
```

**Output Schema**:

```python
class DeleteTaskOutput(BaseModel):
    task_id: int = Field(..., description="Deleted task ID")
    status: str = Field("deleted", description="Deletion status")

    class Config:
        json_schema_extra = {
            "example": {
                "task_id": 1,
                "status": "deleted"
            }
        }
```

---

### Tool: get_task

**Purpose**: Retrieve details of a single task owned by the authenticated user

**Input Schema**:

```python
class GetTaskInput(BaseModel):
    user_id: str = Field(..., description="User UUID from JWT token")
    task_id: int = Field(..., gt=0, description="Task ID to retrieve")

    @validator('user_id')
    def validate_user_id(cls, v):
        try:
            uuid.UUID(v)
            return v
        except ValueError:
            raise ValueError("Invalid user_id format (must be UUID)")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "task_id": 1
            }
        }
```

**Output Schema**:

```python
class GetTaskOutput(BaseModel):
    task: TaskItem = Field(..., description="Task details")

    class Config:
        json_schema_extra = {
            "example": {
                "task": {
                    "id": 1,
                    "title": "Buy groceries",
                    "description": "Milk, eggs, bread",
                    "completed": False,
                    "created_at": "2026-02-06T10:00:00Z",
                    "updated_at": "2026-02-06T10:00:00Z"
                }
            }
        }
```

---

## Error Schema

**Purpose**: Standardized error response for all tools

```python
class ToolErrorType(str, Enum):
    VALIDATION_ERROR = "ValidationError"
    AUTHORIZATION_ERROR = "AuthorizationError"
    NOT_FOUND_ERROR = "NotFoundError"
    SERVER_ERROR = "ServerError"

class ToolError(BaseModel):
    error: ToolErrorType = Field(..., description="Error type")
    detail: str = Field(..., description="Human-readable error message")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "ValidationError",
                "detail": "Title must be between 1 and 200 characters"
            }
        }
```

---

## Schema Validation Rules

### Common Validation Rules

1. **user_id**: Must be valid UUID format
2. **task_id**: Must be positive integer (> 0)
3. **title**: Must be non-empty, max 200 characters
4. **description**: Optional, max 1000 characters
5. **status**: Must be one of: "all", "pending", "completed"

### Security Validation

1. **User Ownership**: All tools validate user owns task before mutations
2. **Input Sanitization**: All string inputs trimmed and validated
3. **Type Safety**: Pydantic enforces type constraints
4. **Length Limits**: All strings have maximum length constraints

---

## Schema Implementation

**File Location**: `backend/app/schemas/mcp_schemas.py`

**Usage Example**:

```python
from app.schemas.mcp_schemas import AddTaskInput, AddTaskOutput, ToolError

# Validate input
try:
    input_data = AddTaskInput(
        user_id="550e8400-e29b-41d4-a716-446655440000",
        title="Buy groceries",
        description="Milk, eggs, bread"
    )
except ValidationError as e:
    return ToolError(
        error=ToolErrorType.VALIDATION_ERROR,
        detail=str(e)
    )

# Process and return output
output = AddTaskOutput(
    task_id=1,
    status="created",
    title=input_data.title
)
```

---

## Next Steps

1. Implement tool contracts (contracts/mcp-tools.yaml)
2. Write quickstart guide (quickstart.md)
3. Proceed to Phase 2: Tasks generation
