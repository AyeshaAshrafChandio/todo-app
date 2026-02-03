"""
Pydantic schemas for Task API request/response validation.

This module defines the data validation schemas used by the FastAPI endpoints:
- TaskCreate: Schema for creating new tasks (POST requests)
- TaskUpdate: Schema for updating existing tasks (PUT requests)
- TaskResponse: Schema for task responses (all endpoints)
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    """
    Schema for creating a new task.

    Used by POST /api/{user_id}/tasks endpoint.
    """
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

    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "title": "Buy groceries",
                "description": "Milk, eggs, bread"
            }
        }


class TaskUpdate(BaseModel):
    """
    Schema for updating an existing task.

    Used by PUT /api/{user_id}/tasks/{id} endpoint.
    """
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
    completed: Optional[bool] = Field(
        default=None,
        description="Completion status (optional)"
    )

    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "title": "Buy groceries",
                "description": "Milk, eggs, bread, cheese",
                "completed": False
            }
        }


class TaskResponse(BaseModel):
    """
    Schema for task responses.

    Used by all endpoints that return task data.
    Includes all task fields from the database model.
    """
    id: int
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime
    user_id: str

    class Config:
        """Pydantic configuration"""
        from_attributes = True  # Enable ORM mode for SQLModel compatibility
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
