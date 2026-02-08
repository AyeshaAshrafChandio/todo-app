# Quickstart Guide: MCP Task Tools

**Feature**: 006-mcp-task-tools
**Date**: 2026-02-06
**Phase**: 1 - Design & Contracts

## Overview

This guide walks you through developing and testing production-grade MCP tools that enable AI agent interaction with the task system. You'll implement tool handlers, integrate with existing service layer, and validate tool behavior.

**Prerequisites**:
- Python 3.11+ installed
- Existing backend from Spec 001 (task service layer)
- Existing AI Chat Backend from Spec 005 (agent orchestration)
- MCP SDK (mcp-python 0.1.0+) already installed

**Estimated Development Time**: 4-6 hours for all 5 tools

---

## Step 1: Understand the Architecture

### Component Overview

```
AI Agent (Spec 005)
    ↓ calls
MCP Tools (Spec 006) ← YOU ARE HERE
    ↓ delegates to
Task Service Layer (Spec 001)
    ↓ persists to
PostgreSQL Database
```

**Key Principles**:
- **Stateless**: Tools maintain no in-memory state between calls
- **Delegation**: Tools delegate all logic to existing service layer
- **Authorization**: Tools validate user ownership before mutations
- **Auditability**: All tool invocations logged with complete context

---

## Step 2: Review Existing Code

### Existing Task Service (Spec 001)

The task service layer already provides all CRUD operations:

```python
# backend/app/services/task_service.py (EXISTING)

class TaskService:
    @staticmethod
    def create_task(db: Session, user_id: str, title: str, description: str = "") -> Task:
        """Create a new task for the user"""
        task = Task(
            user_id=user_id,
            title=title,
            description=description,
            completed=False
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def list_tasks(db: Session, user_id: str, status: str = "all") -> List[Task]:
        """List all tasks for the user with optional status filter"""
        query = db.query(Task).filter(Task.user_id == user_id)
        if status == "pending":
            query = query.filter(Task.completed == False)
        elif status == "completed":
            query = query.filter(Task.completed == True)
        return query.all()

    @staticmethod
    def update_task(db: Session, user_id: str, task_id: int, updates: dict) -> Task:
        """Update task details"""
        task = db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
        if not task:
            raise ValueError("Task not found or unauthorized")
        for key, value in updates.items():
            setattr(task, key, value)
        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def delete_task(db: Session, user_id: str, task_id: int) -> bool:
        """Delete a task"""
        task = db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
        if not task:
            raise ValueError("Task not found or unauthorized")
        db.delete(task)
        db.commit()
        return True

    @staticmethod
    def get_task(db: Session, user_id: str, task_id: int) -> Task:
        """Get task details"""
        task = db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
        if not task:
            raise ValueError("Task not found or unauthorized")
        return task
```

**Your job**: Wrap these service methods in MCP tool handlers with validation, error handling, and logging.

---

## Step 3: Implement Tool Schemas

Create `backend/app/schemas/mcp_schemas.py` with all tool input/output schemas:

```python
# backend/app/schemas/mcp_schemas.py

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum
import uuid

# See data-model.md for complete schema definitions
# Copy all schemas from data-model.md into this file
```

**Reference**: See `specs/006-mcp-task-tools/data-model.md` for complete schema definitions.

---

## Step 4: Implement Tool Handlers

Create `backend/app/services/mcp_tools.py` with production tool handlers:

```python
# backend/app/services/mcp_tools.py

from mcp import Tool
from typing import Dict, Any
import logging
import json
from datetime import datetime

from app.services.task_service import TaskService
from app.database.connection import get_db
from app.schemas.mcp_schemas import (
    AddTaskInput, AddTaskOutput,
    ListTasksInput, ListTasksOutput,
    UpdateTaskInput, UpdateTaskOutput,
    DeleteTaskInput, DeleteTaskOutput,
    GetTaskInput, GetTaskOutput,
    ToolError, ToolErrorType
)

logger = logging.getLogger(__name__)

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
    """Create a new task for the authenticated user"""
    start_time = datetime.utcnow()

    # Log tool invocation
    logger.info(json.dumps({
        "event": "tool_invocation",
        "tool": "add_task",
        "user_id": user_id,
        "parameters": {"title": title, "description": description},
        "timestamp": start_time.isoformat()
    }))

    try:
        # Validate input
        input_data = AddTaskInput(
            user_id=user_id,
            title=title,
            description=description
        )

        # Get database session
        db = next(get_db())

        # Delegate to service layer
        task = TaskService.create_task(
            db=db,
            user_id=input_data.user_id,
            title=input_data.title,
            description=input_data.description
        )

        # Format output
        output = AddTaskOutput(
            task_id=task.id,
            status="created",
            title=task.title
        )

        # Log success
        logger.info(json.dumps({
            "event": "tool_success",
            "tool": "add_task",
            "user_id": user_id,
            "result": {"task_id": task.id, "status": "created"},
            "execution_time_ms": (datetime.utcnow() - start_time).total_seconds() * 1000,
            "timestamp": datetime.utcnow().isoformat()
        }))

        return output.dict()

    except ValueError as e:
        # Validation error
        logger.warning(json.dumps({
            "event": "tool_error",
            "tool": "add_task",
            "user_id": user_id,
            "error_type": "ValidationError",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }))
        return ToolError(
            error=ToolErrorType.VALIDATION_ERROR,
            detail=str(e)
        ).dict()

    except Exception as e:
        # Server error
        logger.error(json.dumps({
            "event": "tool_error",
            "tool": "add_task",
            "user_id": user_id,
            "error_type": "ServerError",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), exc_info=True)
        return ToolError(
            error=ToolErrorType.SERVER_ERROR,
            detail="An error occurred while creating the task"
        ).dict()

# Implement remaining tools: list_tasks, update_task, delete_task, get_task
# Follow the same pattern: validate → delegate → log → return
```

**Pattern**: All tools follow the same structure:
1. Log invocation
2. Validate input with Pydantic schema
3. Get database session
4. Delegate to service layer
5. Format output
6. Log success/error
7. Return structured response

---

## Step 5: Update MCP Client (Spec 005)

Replace placeholder MCP client with production tool registration:

```python
# backend/app/services/mcp_client.py (UPDATE)

from mcp import MCPServer
from app.services.mcp_tools import (
    add_task,
    list_tasks,
    update_task,
    delete_task,
    get_task
)

class MCPClient:
    def __init__(self):
        self.server = MCPServer()
        self._register_tools()

    def _register_tools(self):
        """Register all MCP tools"""
        self.server.register_tool(add_task)
        self.server.register_tool(list_tasks)
        self.server.register_tool(update_task)
        self.server.register_tool(delete_task)
        self.server.register_tool(get_task)

    async def call_tool(self, tool_name: str, **kwargs) -> dict:
        """Call a registered tool"""
        return await self.server.call_tool(tool_name, **kwargs)
```

---

## Step 6: Test Tool Implementation

### Unit Test Example

```python
# backend/tests/test_mcp_tools.py

import pytest
from unittest.mock import Mock, patch
from app.services.mcp_tools import add_task

@pytest.mark.asyncio
async def test_add_task_success():
    """Test successful task creation"""
    with patch('app.services.task_service.TaskService.create_task') as mock_create:
        # Mock service layer response
        mock_task = Mock(id=1, title="Buy groceries")
        mock_create.return_value = mock_task

        # Call tool
        result = await add_task(
            user_id="550e8400-e29b-41d4-a716-446655440000",
            title="Buy groceries",
            description="Milk, eggs, bread"
        )

        # Assert success
        assert result["task_id"] == 1
        assert result["status"] == "created"
        assert result["title"] == "Buy groceries"

@pytest.mark.asyncio
async def test_add_task_validation_error():
    """Test validation error handling"""
    result = await add_task(
        user_id="invalid-uuid",
        title="Buy groceries"
    )

    # Assert error response
    assert result["error"] == "ValidationError"
    assert "Invalid user_id format" in result["detail"]
```

### Integration Test Example

```python
# backend/tests/test_mcp_integration.py

import pytest
from app.services.mcp_client import MCPClient

@pytest.mark.asyncio
async def test_agent_tool_integration():
    """Test agent calling tool through MCP client"""
    # Setup
    mcp_client = MCPClient()
    user_id = "550e8400-e29b-41d4-a716-446655440000"

    # Call add_task tool
    result = await mcp_client.call_tool(
        "add_task",
        user_id=user_id,
        title="Buy groceries",
        description="Milk, eggs, bread"
    )

    # Assert task created
    assert result["status"] == "created"
    assert "task_id" in result

    # Call list_tasks tool
    tasks = await mcp_client.call_tool(
        "list_tasks",
        user_id=user_id,
        status="all"
    )

    # Assert task appears in list
    assert tasks["count"] == 1
    assert tasks["tasks"][0]["title"] == "Buy groceries"
```

---

## Step 7: Test with Agent (End-to-End)

### Manual Testing

1. **Start backend server**:
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload --port 8001
   ```

2. **Authenticate and get JWT token**:
   ```bash
   curl -X POST http://localhost:8001/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com", "password": "password"}'
   ```

3. **Send chat message to test tool**:
   ```bash
   curl -X POST http://localhost:8001/api/chat \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer <TOKEN>" \
     -d '{
       "conversation_id": null,
       "message": "Add buy groceries to my list"
     }'
   ```

4. **Verify task created**:
   ```bash
   curl -X GET http://localhost:8001/api/<user_id>/tasks \
     -H "Authorization: Bearer <TOKEN>"
   ```

**Expected Result**: Task "buy groceries" appears in task list.

---

## Step 8: Verify Logging

Check that all tool invocations are logged:

```bash
# View logs
tail -f backend/logs/app.log | grep "tool_invocation"

# Expected log format:
{
  "event": "tool_invocation",
  "tool": "add_task",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "parameters": {"title": "Buy groceries", "description": "Milk, eggs, bread"},
  "timestamp": "2026-02-06T10:00:00Z"
}

{
  "event": "tool_success",
  "tool": "add_task",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "result": {"task_id": 1, "status": "created"},
  "execution_time_ms": 150,
  "timestamp": "2026-02-06T10:00:00.150Z"
}
```

---

## Troubleshooting

### Issue: "Tool not registered"

**Symptoms**: Agent cannot find tool

**Solution**:
1. Verify tool is registered in MCPClient._register_tools()
2. Check tool name matches exactly (case-sensitive)
3. Restart backend server to reload tools

---

### Issue: "Authorization error"

**Symptoms**: Tool returns "AuthorizationError"

**Solution**:
1. Verify user_id is valid UUID format
2. Verify user owns the task (for update/delete/get)
3. Check JWT token is valid and not expired

---

### Issue: "Service layer error"

**Symptoms**: Tool returns "ServerError"

**Solution**:
1. Check backend logs for full error details
2. Verify database connection is healthy
3. Verify task service layer is working (test REST API endpoints)

---

## Next Steps

1. **Run `/sp.tasks`**: Generate testable tasks from implementation plan
2. **Implement all 5 tools**: Use `fastapi-backend` agent for implementation
3. **Run tests**: Validate all tools work correctly
4. **Integration testing**: Test with agent from Spec 005
5. **End-to-end testing**: Test full conversational workflow

---

## Additional Resources

- **MCP SDK Documentation**: https://github.com/modelcontextprotocol/python-sdk
- **Pydantic Documentation**: https://docs.pydantic.dev/
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **Specification**: `specs/006-mcp-task-tools/spec.md`
- **Implementation Plan**: `specs/006-mcp-task-tools/plan.md`
- **Tool Schemas**: `specs/006-mcp-task-tools/data-model.md`
- **Tool Contracts**: `specs/006-mcp-task-tools/contracts/mcp-tools.yaml`

---

## Support

If you encounter issues not covered in this guide:

1. Check backend logs: `tail -f backend/logs/app.log`
2. Review the specification: `specs/006-mcp-task-tools/spec.md`
3. Review the implementation plan: `specs/006-mcp-task-tools/plan.md`
4. Check existing task service: `backend/app/services/task_service.py`
5. Check agent integration: `backend/app/services/agent_service.py`

For questions or issues, contact the development team.
