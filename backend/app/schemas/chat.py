"""
Pydantic schemas for chat API requests and responses.

This module defines the request/response schemas for the chat endpoint
in the AI Chat Backend (Spec 005).
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ToolCall(BaseModel):
    """Schema for a tool invocation by the agent."""
    tool: str = Field(..., description="Name of the tool that was invoked")
    arguments: Dict[str, Any] = Field(..., description="Arguments passed to the tool")

    class Config:
        json_schema_extra = {
            "example": {
                "tool": "create_task",
                "arguments": {
                    "title": "buy groceries",
                    "description": "Purchase groceries from the store"
                }
            }
        }


class ChatRequest(BaseModel):
    """Schema for chat endpoint request."""
    conversation_id: Optional[int] = Field(
        default=None,
        description="Existing conversation ID to continue (null for new conversation)"
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="User message text (max 10,000 characters)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": 1,
                "message": "Add buy groceries to my list"
            }
        }


class ChatResponse(BaseModel):
    """Schema for chat endpoint response."""
    conversation_id: int = Field(..., description="Conversation ID for this exchange")
    response: str = Field(..., description="Assistant's natural language response")
    tool_calls: List[ToolCall] = Field(
        default_factory=list,
        description="Tools invoked by the agent (for transparency)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": 1,
                "response": "I've added 'buy groceries' to your task list.",
                "tool_calls": [
                    {
                        "tool": "create_task",
                        "arguments": {
                            "title": "buy groceries",
                            "description": "Purchase groceries from the store"
                        }
                    }
                ]
            }
        }
