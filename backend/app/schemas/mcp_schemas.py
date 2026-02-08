"""
MCP Tool Schemas

This module defines Pydantic models for all MCP tool input/output schemas.
All schemas are designed to be stateless, deterministic, and secure.

Feature: 006-mcp-task-tools
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum
import uuid


# ============================================================================
# Common Schemas
# ============================================================================

class TaskStatus(str, Enum):
    """Task status filter options"""
    ALL = "all"
    PENDING = "pending"
    COMPLETED = "completed"


class TaskItem(BaseModel):
    """Task item representation for list/get operations"""
    id: int
    title: str
    description: str
    completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "completed": False,
                "created_at": "2026-02-06T10:00:00Z",
                "updated_at": "2026-02-06T10:00:00Z"
            }
        }


class ToolErrorType(str, Enum):
    """Error types for tool responses"""
    VALIDATION_ERROR = "ValidationError"
    AUTHORIZATION_ERROR = "AuthorizationError"
    NOT_FOUND_ERROR = "NotFoundError"
    SERVER_ERROR = "ServerError"


class ToolError(BaseModel):
    """Standardized error response for all tools"""
    error: ToolErrorType = Field(..., description="Error type")
    detail: str = Field(..., description="Human-readable error message")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "ValidationError",
                "detail": "Title must be between 1 and 200 characters"
            }
        }


# ============================================================================
# Tool: add_task
# ============================================================================

class AddTaskInput(BaseModel):
    """Input schema for add_task tool"""
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


class AddTaskOutput(BaseModel):
    """Output schema for add_task tool"""
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


# ============================================================================
# Tool: list_tasks
# ============================================================================

class ListTasksInput(BaseModel):
    """Input schema for list_tasks tool"""
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


class ListTasksOutput(BaseModel):
    """Output schema for list_tasks tool"""
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


# ============================================================================
# Tool: update_task
# ============================================================================

class TaskUpdates(BaseModel):
    """Updates object for update_task tool"""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="New task title")
    description: Optional[str] = Field(None, max_length=1000, description="New task description")
    completed: Optional[bool] = Field(None, description="New completion status")

    @validator('title')
    def validate_title(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError("Title cannot be empty")
        return v.strip() if v else v


class UpdateTaskInput(BaseModel):
    """Input schema for update_task tool"""
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


class UpdateTaskOutput(BaseModel):
    """Output schema for update_task tool"""
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


# ============================================================================
# Tool: delete_task
# ============================================================================

class DeleteTaskInput(BaseModel):
    """Input schema for delete_task tool"""
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


class DeleteTaskOutput(BaseModel):
    """Output schema for delete_task tool"""
    task_id: int = Field(..., description="Deleted task ID")
    status: str = Field("deleted", description="Deletion status")

    class Config:
        json_schema_extra = {
            "example": {
                "task_id": 1,
                "status": "deleted"
            }
        }


# ============================================================================
# Tool: get_task
# ============================================================================

class GetTaskInput(BaseModel):
    """Input schema for get_task tool"""
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


class GetTaskOutput(BaseModel):
    """Output schema for get_task tool"""
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
