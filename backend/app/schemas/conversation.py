"""
Pydantic schemas for Conversation API responses.

This module defines the response schemas for conversation-related endpoints
in the AI Chat Backend (Spec 005).
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class MessageSchema(BaseModel):
    """Schema for a single message in a conversation."""
    id: int = Field(..., description="Unique message identifier")
    conversation_id: int = Field(..., description="Conversation this message belongs to")
    user_id: str = Field(..., description="Owner of the conversation")
    role: str = Field(..., description="Message sender role (user or assistant)")
    content: str = Field(..., description="Message content text")
    created_at: datetime = Field(..., description="When message was created")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "conversation_id": 1,
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "role": "user",
                "content": "Add buy groceries to my list",
                "created_at": "2026-02-06T10:00:00Z"
            }
        }


class ConversationSchema(BaseModel):
    """Schema for a conversation with optional messages."""
    id: int = Field(..., description="Unique conversation identifier")
    user_id: str = Field(..., description="Owner of the conversation")
    created_at: datetime = Field(..., description="When conversation was created")
    updated_at: datetime = Field(..., description="When conversation was last updated")
    messages: Optional[List[MessageSchema]] = Field(
        default=None,
        description="Messages in this conversation (optional)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "created_at": "2026-02-06T10:00:00Z",
                "updated_at": "2026-02-06T10:05:00Z",
                "messages": [
                    {
                        "id": 1,
                        "conversation_id": 1,
                        "user_id": "550e8400-e29b-41d4-a716-446655440000",
                        "role": "user",
                        "content": "Add buy groceries to my list",
                        "created_at": "2026-02-06T10:00:00Z"
                    },
                    {
                        "id": 2,
                        "conversation_id": 1,
                        "user_id": "550e8400-e29b-41d4-a716-446655440000",
                        "role": "assistant",
                        "content": "I've added 'buy groceries' to your task list.",
                        "created_at": "2026-02-06T10:00:05Z"
                    }
                ]
            }
        }
