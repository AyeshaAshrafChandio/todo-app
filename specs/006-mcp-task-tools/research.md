# Research & Discovery: MCP Task Tools

**Feature**: 006-mcp-task-tools
**Date**: 2026-02-06
**Phase**: 0 - Research & Discovery

## Overview

This document captures research findings for implementing production-grade MCP tools that enable AI agent interaction with the task system. The research focuses on MCP SDK integration patterns, service layer delegation strategies, and best practices for tool implementation.

## Research Questions

1. How to implement MCP tool handlers using mcp-python SDK?
2. How to delegate tool operations to existing service layer?
3. How to define and validate tool input/output schemas?
4. How to handle tool errors gracefully?
5. How to log tool invocations for auditability?
6. How to test MCP tools and agent-tool integration?

## Research Findings

### 1. MCP SDK Tool Handler Implementation

**Decision**: Use MCP SDK's `@Tool` decorator pattern with async handlers

**Rationale**:
- MCP SDK provides high-level abstractions for tool registration
- Decorator pattern is clean and Pythonic
- Async handlers integrate well with FastAPI's async architecture
- Built-in schema validation from decorator parameters
- Supports structured input/output definitions

**Implementation Pattern**:
```python
from mcp import Tool
from typing import Dict, Any

@Tool(
    name="add_task",
    description="Create a new task for the user",
    parameters={
        "user_id": {"type": "string", "description": "User UUID"},
        "title": {"type": "string", "description": "Task title"},
        "description": {"type": "string", "description": "Task description", "optional": True}
    }
)
async def add_task(user_id: str, title: str, description: str = "") -> Dict[str, Any]:
    # Validate inputs
    # Delegate to service layer
    # Return structured response
    pass
```

**Alternatives Considered**:
- **Manual function registration**: More control but verbose, no built-in validation
- **Class-based tools**: More structure but overkill for simple CRUD operations
- **Direct OpenAI function calling**: Bypasses MCP abstraction, loses auditability

**Rejected Because**: Decorator pattern provides best balance of simplicity and functionality.

### 2. Service Layer Delegation Strategy

**Decision**: Direct function calls to existing task service layer

**Rationale**:
- Existing task service (Spec 001) already provides all CRUD operations
- Direct function calls are faster than internal API calls
- No network overhead or serialization costs
- Service layer already handles database transactions
- Service layer already enforces business rules

**Implementation Strategy**:
```python
from app.services.task_service import TaskService
from app.database.connection import get_db

async def add_task(user_id: str, title: str, description: str = "") -> Dict[str, Any]:
    try:
        # Get database session
        db = next(get_db())

        # Delegate to service layer
        task = TaskService.create_task(
            db=db,
            user_id=user_id,
            title=title,
            description=description
        )

        # Return structured response
        return {
            "task_id": task.id,
            "status": "created",
            "title": task.title
        }
    except Exception as e:
        # Handle errors gracefully
        return {"error": "TaskCreationError", "detail": str(e)}
```

**Alternatives Considered**:
- **Internal API calls**: More overhead, unnecessary network layer
- **Direct database access**: Violates separation of concerns, bypasses business logic
- **Duplicate service logic in tools**: Code duplication, maintenance burden

**Rejected Because**: Direct service layer calls provide best performance and maintain separation of concerns.

### 3. Tool Schema Definition and Validation

**Decision**: Use Pydantic models for tool input/output schemas

**Rationale**:
- Pydantic provides automatic validation
- Type hints improve code clarity
- JSON schema generation for documentation
- Integrates well with FastAPI and MCP SDK
- Supports complex nested structures

**Schema Definition Pattern**:
```python
from pydantic import BaseModel, Field, validator
from typing import Optional
import uuid

class AddTaskInput(BaseModel):
    user_id: str = Field(..., description="User UUID")
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field("", description="Task description")

    @validator('user_id')
    def validate_user_id(cls, v):
        try:
            uuid.UUID(v)
            return v
        except ValueError:
            raise ValueError("Invalid user_id format (must be UUID)")

class AddTaskOutput(BaseModel):
    task_id: int
    status: str
    title: str

class ToolError(BaseModel):
    error: str
    detail: str
```

**Alternatives Considered**:
- **Dict-based schemas**: No validation, error-prone
- **JSON Schema directly**: More verbose, less Pythonic
- **TypedDict**: No runtime validation

**Rejected Because**: Pydantic provides best combination of validation, type safety, and developer experience.

### 4. Error Handling Patterns

**Decision**: Structured error responses with error type and detail

**Rationale**:
- Enables agent to understand error category
- Provides user-friendly error messages
- Maintains security (no internal details exposed)
- Consistent error format across all tools
- Supports error logging and monitoring

**Error Handling Strategy**:
```python
class ToolErrorType:
    VALIDATION_ERROR = "ValidationError"
    AUTHORIZATION_ERROR = "AuthorizationError"
    NOT_FOUND_ERROR = "NotFoundError"
    SERVER_ERROR = "ServerError"

async def add_task(user_id: str, title: str, description: str = "") -> Dict[str, Any]:
    try:
        # Validate inputs
        if not title or len(title) > 200:
            return {
                "error": ToolErrorType.VALIDATION_ERROR,
                "detail": "Title must be between 1 and 200 characters"
            }

        # Validate user_id format
        try:
            uuid.UUID(user_id)
        except ValueError:
            return {
                "error": ToolErrorType.VALIDATION_ERROR,
                "detail": "Invalid user_id format (must be UUID)"
            }

        # Delegate to service layer
        task = TaskService.create_task(...)

        return {"task_id": task.id, "status": "created", "title": task.title}

    except PermissionError:
        return {
            "error": ToolErrorType.AUTHORIZATION_ERROR,
            "detail": "You do not have permission to perform this action"
        }
    except Exception as e:
        # Log full error server-side
        logger.error(f"Tool error: {e}", exc_info=True)
        # Return generic error to agent
        return {
            "error": ToolErrorType.SERVER_ERROR,
            "detail": "An error occurred while processing your request"
        }
```

**Alternatives Considered**:
- **Exception-based errors**: Harder for agent to parse, may crash
- **HTTP status codes**: Not applicable for tool responses
- **Unstructured error messages**: Inconsistent, hard to handle

**Rejected Because**: Structured error responses provide best agent experience and maintainability.

### 5. Logging and Auditability Strategy

**Decision**: JSON-structured logs with tool name, user_id, parameters, result

**Rationale**:
- Enables audit trail of all agent actions
- Supports debugging and monitoring
- JSON format is machine-parseable
- Includes all context needed for investigation
- Low overhead (<10ms per call)

**Logging Strategy**:
```python
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

async def add_task(user_id: str, title: str, description: str = "") -> Dict[str, Any]:
    start_time = datetime.utcnow()

    # Log tool invocation
    logger.info(json.dumps({
        "event": "tool_invocation",
        "tool": "add_task",
        "user_id": user_id,
        "parameters": {
            "title": title,
            "description": description
        },
        "timestamp": start_time.isoformat()
    }))

    try:
        # Execute tool logic
        result = TaskService.create_task(...)

        # Log success
        logger.info(json.dumps({
            "event": "tool_success",
            "tool": "add_task",
            "user_id": user_id,
            "result": {"task_id": result.id, "status": "created"},
            "execution_time_ms": (datetime.utcnow() - start_time).total_seconds() * 1000,
            "timestamp": datetime.utcnow().isoformat()
        }))

        return {"task_id": result.id, "status": "created", "title": result.title}

    except Exception as e:
        # Log error
        logger.error(json.dumps({
            "event": "tool_error",
            "tool": "add_task",
            "user_id": user_id,
            "error": str(e),
            "execution_time_ms": (datetime.utcnow() - start_time).total_seconds() * 1000,
            "timestamp": datetime.utcnow().isoformat()
        }), exc_info=True)

        return {"error": "ServerError", "detail": "An error occurred"}
```

**Alternatives Considered**:
- **Plain text logs**: Harder to parse, less structured
- **Database logging**: More overhead, overkill for MVP
- **External logging service**: Additional dependency, complexity

**Rejected Because**: JSON-structured logs provide best balance of functionality and simplicity.

### 6. Tool Testing Strategy

**Decision**: Unit tests for individual tools + integration tests for agent-tool workflow

**Rationale**:
- Unit tests validate tool logic in isolation
- Integration tests validate end-to-end workflow
- Mocking service layer for unit tests
- Real service layer for integration tests
- Fast feedback loop for development

**Testing Strategy**:
```python
# Unit test example
import pytest
from unittest.mock import Mock, patch

@pytest.mark.asyncio
async def test_add_task_success():
    # Mock service layer
    with patch('app.services.task_service.TaskService.create_task') as mock_create:
        mock_create.return_value = Mock(id=1, title="Buy groceries")

        # Call tool
        result = await add_task(
            user_id="550e8400-e29b-41d4-a716-446655440000",
            title="Buy groceries",
            description="Milk, eggs, bread"
        )

        # Assert
        assert result["task_id"] == 1
        assert result["status"] == "created"
        assert result["title"] == "Buy groceries"

@pytest.mark.asyncio
async def test_add_task_validation_error():
    # Call tool with invalid input
    result = await add_task(
        user_id="invalid-uuid",
        title="Buy groceries"
    )

    # Assert error response
    assert result["error"] == "ValidationError"
    assert "Invalid user_id format" in result["detail"]

# Integration test example
@pytest.mark.asyncio
async def test_agent_tool_integration():
    # Setup: Create test user and authenticate
    user = create_test_user()
    token = get_jwt_token(user)

    # Send chat message
    response = await client.post(
        "/api/chat",
        json={"conversation_id": None, "message": "Add buy groceries to my list"},
        headers={"Authorization": f"Bearer {token}"}
    )

    # Assert agent called tool and task was created
    assert response.status_code == 200
    assert "buy groceries" in response.json()["response"].lower()

    # Verify task exists in database
    tasks = TaskService.list_tasks(db, user_id=user.id)
    assert len(tasks) == 1
    assert tasks[0].title == "buy groceries"
```

**Alternatives Considered**:
- **Manual testing only**: Not scalable, error-prone
- **Integration tests only**: Slow, hard to debug
- **End-to-end tests only**: Very slow, brittle

**Rejected Because**: Combination of unit and integration tests provides best coverage and feedback.

## Technology Decisions

### MCP SDK Version

**Decision**: Use mcp-python 0.1.0+ (already installed in Spec 005)

**Rationale**:
- Official MCP implementation
- Active development and support
- Python 3.11+ compatibility
- Async/await support
- Already installed and tested in Spec 005

### Service Layer Integration

**Decision**: Direct function calls to existing TaskService (Spec 001)

**Rationale**:
- TaskService already provides all CRUD operations
- No need for additional abstraction layer
- Maintains separation of concerns
- Backward compatible (no changes to service layer)

### Tool Registration

**Decision**: Register tools at application startup

**Rationale**:
- Tools are static (no dynamic registration needed)
- Startup registration is simple and reliable
- No runtime overhead for registration
- Easy to test and validate

## Performance Considerations

### Expected Latency Breakdown

- Input validation: ~1-5ms
- Service layer call: ~50-200ms (depends on database query)
- Response formatting: ~1-5ms
- Logging overhead: ~5-10ms
- **Total**: ~60-220ms typical, <500ms target

### Optimization Strategies

1. **Database Indexing**: Ensure proper indexes on user_id and task_id (already in place from Spec 001)
2. **Connection Pooling**: Reuse database connections (already configured)
3. **Async I/O**: Use async/await for all I/O operations
4. **Minimal Logging**: Log only essential information to reduce overhead
5. **Schema Validation**: Use Pydantic for fast validation

## Security Considerations

### Authorization Validation

- Validate user_id format (UUID) before processing
- Validate user owns task before mutations (update, delete)
- Never trust agent-provided user_id (always from JWT)
- Log all authorization failures for security monitoring

### Input Sanitization

- Validate all string inputs for length and format
- Sanitize inputs to prevent SQL injection (handled by SQLModel ORM)
- Validate enum values (status filter)
- Reject malformed JSON (handled by MCP SDK)

### Error Message Security

- Never expose internal error details to agent
- Never expose database schema or query details
- Never expose file paths or system information
- Log full errors server-side for debugging

## Risks & Mitigations

### Risk 1: Service Layer API Changes
**Mitigation**: Use stable service layer interfaces, add integration tests, document dependencies

### Risk 2: Tool Performance Degradation
**Mitigation**: Monitor tool response times, optimize database queries, add caching if needed

### Risk 3: Authorization Bypass
**Mitigation**: Validate user ownership at tool level, add authorization tests, log all failures

## Next Steps

1. Implement tool schemas (data-model.md)
2. Define tool contracts (contracts/mcp-tools.yaml)
3. Write quickstart guide (quickstart.md)
4. Proceed to Phase 2: Tasks generation
