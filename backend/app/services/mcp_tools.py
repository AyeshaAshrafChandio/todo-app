"""
MCP Tool Handlers

This module implements production-grade MCP tool handlers that enable AI agent
interaction with the task system. All tools delegate to existing service layer,
enforce authorization, and provide deterministic responses.

Feature: 006-mcp-task-tools
"""

from typing import Dict, Any
import logging
import json
from datetime import datetime

from app.services.task_service import (
    create_task,
    get_tasks_by_user,
    get_task_by_id,
    update_task,
    delete_task
)
from app.database.connection import get_db
from app.schemas.task import TaskCreate, TaskUpdate
from app.schemas.mcp_schemas import (
    AddTaskInput, AddTaskOutput,
    ListTasksInput, ListTasksOutput, TaskItem,
    UpdateTaskInput, UpdateTaskOutput,
    DeleteTaskInput, DeleteTaskOutput,
    GetTaskInput, GetTaskOutput,
    ToolError, ToolErrorType
)
from fastapi import HTTPException
from pydantic import ValidationError

logger = logging.getLogger(__name__)


async def add_task(user_id: str, title: str, description: str = "") -> Dict[str, Any]:
    """
    Create a new task for the authenticated user.

    This tool validates inputs, delegates to existing task service layer,
    and returns structured response with task_id.

    Args:
        user_id: User UUID from JWT token (validated)
        title: Task title (1-200 characters)
        description: Task description (optional, max 1000 characters)

    Returns:
        Dict with task_id, status, and title on success
        Dict with error and detail on failure
    """
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
        # Validate input with Pydantic schema
        input_data = AddTaskInput(
            user_id=user_id,
            title=title,
            description=description
        )

        # Get database session
        db = next(get_db())

        # Create TaskCreate schema for service layer
        task_data = TaskCreate(
            title=input_data.title,
            description=input_data.description
        )

        # Delegate to service layer
        task = create_task(db=db, user_id=input_data.user_id, task_data=task_data)

        # Format output
        output = AddTaskOutput(
            task_id=task.id,
            status="created",
            title=task.title
        )

        # Log success
        execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        logger.info(json.dumps({
            "event": "tool_success",
            "tool": "add_task",
            "user_id": user_id,
            "result": {"task_id": task.id, "status": "created"},
            "execution_time_ms": execution_time,
            "timestamp": datetime.utcnow().isoformat()
        }))

        return output.dict()

    except ValidationError as e:
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

    except HTTPException as e:
        # HTTP exception from service layer
        error_type = ToolErrorType.AUTHORIZATION_ERROR if e.status_code == 403 else ToolErrorType.SERVER_ERROR
        logger.warning(json.dumps({
            "event": "tool_error",
            "tool": "add_task",
            "user_id": user_id,
            "error_type": error_type.value,
            "error": e.detail,
            "timestamp": datetime.utcnow().isoformat()
        }))
        return ToolError(
            error=error_type,
            detail=e.detail
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


async def list_tasks(user_id: str, status: str = "all") -> Dict[str, Any]:
    """
    Retrieve all tasks for the authenticated user.

    This tool validates inputs, delegates to existing task service layer,
    and returns structured list of tasks.

    Args:
        user_id: User UUID from JWT token (validated)
        status: Filter by status - "all", "pending", or "completed"

    Returns:
        Dict with tasks array and count on success
        Dict with error and detail on failure
    """
    start_time = datetime.utcnow()

    # Log tool invocation
    logger.info(json.dumps({
        "event": "tool_invocation",
        "tool": "list_tasks",
        "user_id": user_id,
        "parameters": {"status": status},
        "timestamp": start_time.isoformat()
    }))

    try:
        # Validate input with Pydantic schema
        input_data = ListTasksInput(
            user_id=user_id,
            status=status
        )

        # Get database session
        db = next(get_db())

        # Delegate to service layer
        tasks = get_tasks_by_user(db=db, user_id=input_data.user_id)

        # Filter by status if needed
        if input_data.status.value == "pending":
            tasks = [t for t in tasks if not t.completed]
        elif input_data.status.value == "completed":
            tasks = [t for t in tasks if t.completed]

        # Convert Task models to TaskItem schemas
        task_items = [
            TaskItem(
                id=task.id,
                title=task.title,
                description=task.description,
                completed=task.completed,
                created_at=task.created_at,
                updated_at=task.updated_at
            )
            for task in tasks
        ]

        # Format output
        output = ListTasksOutput(
            tasks=task_items,
            count=len(task_items)
        )

        # Log success
        execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        logger.info(json.dumps({
            "event": "tool_success",
            "tool": "list_tasks",
            "user_id": user_id,
            "result": {"count": len(task_items), "status": status},
            "execution_time_ms": execution_time,
            "timestamp": datetime.utcnow().isoformat()
        }))

        return output.dict()

    except ValidationError as e:
        # Validation error
        logger.warning(json.dumps({
            "event": "tool_error",
            "tool": "list_tasks",
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
            "tool": "list_tasks",
            "user_id": user_id,
            "error_type": "ServerError",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), exc_info=True)
        return ToolError(
            error=ToolErrorType.SERVER_ERROR,
            detail="An error occurred while retrieving tasks"
        ).dict()


async def get_task(user_id: str, task_id: int) -> Dict[str, Any]:
    """
    Retrieve details of a single task.

    This tool validates inputs, delegates to existing task service layer,
    and returns complete task details.

    Args:
        user_id: User UUID from JWT token (validated)
        task_id: Task ID to retrieve

    Returns:
        Dict with task details on success
        Dict with error and detail on failure
    """
    start_time = datetime.utcnow()

    # Log tool invocation
    logger.info(json.dumps({
        "event": "tool_invocation",
        "tool": "get_task",
        "user_id": user_id,
        "parameters": {"task_id": task_id},
        "timestamp": start_time.isoformat()
    }))

    try:
        # Validate input with Pydantic schema
        input_data = GetTaskInput(
            user_id=user_id,
            task_id=task_id
        )

        # Get database session
        db = next(get_db())

        # Delegate to service layer
        task = get_task_by_id(db=db, user_id=input_data.user_id, task_id=input_data.task_id)

        # Convert Task model to TaskItem schema
        task_item = TaskItem(
            id=task.id,
            title=task.title,
            description=task.description,
            completed=task.completed,
            created_at=task.created_at,
            updated_at=task.updated_at
        )

        # Format output
        output = GetTaskOutput(task=task_item)

        # Log success
        execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        logger.info(json.dumps({
            "event": "tool_success",
            "tool": "get_task",
            "user_id": user_id,
            "result": {"task_id": task.id},
            "execution_time_ms": execution_time,
            "timestamp": datetime.utcnow().isoformat()
        }))

        return output.dict()

    except ValidationError as e:
        # Validation error
        logger.warning(json.dumps({
            "event": "tool_error",
            "tool": "get_task",
            "user_id": user_id,
            "error_type": "ValidationError",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }))
        return ToolError(
            error=ToolErrorType.VALIDATION_ERROR,
            detail=str(e)
        ).dict()

    except HTTPException as e:
        # HTTP exception from service layer
        if e.status_code == 404:
            error_type = ToolErrorType.NOT_FOUND_ERROR
        elif e.status_code == 403:
            error_type = ToolErrorType.AUTHORIZATION_ERROR
        else:
            error_type = ToolErrorType.SERVER_ERROR

        logger.warning(json.dumps({
            "event": "tool_error",
            "tool": "get_task",
            "user_id": user_id,
            "error_type": error_type.value,
            "error": e.detail,
            "timestamp": datetime.utcnow().isoformat()
        }))
        return ToolError(
            error=error_type,
            detail=e.detail
        ).dict()

    except Exception as e:
        # Server error
        logger.error(json.dumps({
            "event": "tool_error",
            "tool": "get_task",
            "user_id": user_id,
            "error_type": "ServerError",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), exc_info=True)
        return ToolError(
            error=ToolErrorType.SERVER_ERROR,
            detail="An error occurred while retrieving the task"
        ).dict()


async def update_task_tool(user_id: str, task_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update task details.

    This tool validates inputs, delegates to existing task service layer,
    and returns updated task details.

    Args:
        user_id: User UUID from JWT token (validated)
        task_id: Task ID to update
        updates: Dict with fields to update (title, description, completed)

    Returns:
        Dict with updated task details on success
        Dict with error and detail on failure
    """
    start_time = datetime.utcnow()

    # Log tool invocation
    logger.info(json.dumps({
        "event": "tool_invocation",
        "tool": "update_task",
        "user_id": user_id,
        "parameters": {"task_id": task_id, "updates": updates},
        "timestamp": start_time.isoformat()
    }))

    try:
        # Validate input with Pydantic schema
        input_data = UpdateTaskInput(
            user_id=user_id,
            task_id=task_id,
            updates=updates
        )

        # Get database session
        db = next(get_db())

        # Create TaskUpdate schema for service layer
        # Note: service layer expects title and description to always be present
        # Get current task first to preserve unchanged fields
        current_task = get_task_by_id(db=db, user_id=input_data.user_id, task_id=input_data.task_id)

        task_data = TaskUpdate(
            title=input_data.updates.title if input_data.updates.title is not None else current_task.title,
            description=input_data.updates.description if input_data.updates.description is not None else current_task.description,
            completed=input_data.updates.completed if input_data.updates.completed is not None else current_task.completed
        )

        # Delegate to service layer
        task = update_task(db=db, user_id=input_data.user_id, task_id=input_data.task_id, task_data=task_data)

        # Convert Task model to TaskItem schema
        task_item = TaskItem(
            id=task.id,
            title=task.title,
            description=task.description,
            completed=task.completed,
            created_at=task.created_at,
            updated_at=task.updated_at
        )

        # Format output
        output = UpdateTaskOutput(
            task_id=task.id,
            status="updated",
            task=task_item
        )

        # Log success
        execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        logger.info(json.dumps({
            "event": "tool_success",
            "tool": "update_task",
            "user_id": user_id,
            "result": {"task_id": task.id, "status": "updated"},
            "execution_time_ms": execution_time,
            "timestamp": datetime.utcnow().isoformat()
        }))

        return output.dict()

    except ValidationError as e:
        # Validation error
        logger.warning(json.dumps({
            "event": "tool_error",
            "tool": "update_task",
            "user_id": user_id,
            "error_type": "ValidationError",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }))
        return ToolError(
            error=ToolErrorType.VALIDATION_ERROR,
            detail=str(e)
        ).dict()

    except HTTPException as e:
        # HTTP exception from service layer
        if e.status_code == 404:
            error_type = ToolErrorType.NOT_FOUND_ERROR
        elif e.status_code == 403:
            error_type = ToolErrorType.AUTHORIZATION_ERROR
        else:
            error_type = ToolErrorType.SERVER_ERROR

        logger.warning(json.dumps({
            "event": "tool_error",
            "tool": "update_task",
            "user_id": user_id,
            "error_type": error_type.value,
            "error": e.detail,
            "timestamp": datetime.utcnow().isoformat()
        }))
        return ToolError(
            error=error_type,
            detail=e.detail
        ).dict()

    except Exception as e:
        # Server error
        logger.error(json.dumps({
            "event": "tool_error",
            "tool": "update_task",
            "user_id": user_id,
            "error_type": "ServerError",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), exc_info=True)
        return ToolError(
            error=ToolErrorType.SERVER_ERROR,
            detail="An error occurred while updating the task"
        ).dict()


async def delete_task_tool(user_id: str, task_id: int) -> Dict[str, Any]:
    """
    Delete a task.

    This tool validates inputs, delegates to existing task service layer,
    and returns deletion confirmation.

    Args:
        user_id: User UUID from JWT token (validated)
        task_id: Task ID to delete

    Returns:
        Dict with deletion confirmation on success
        Dict with error and detail on failure
    """
    start_time = datetime.utcnow()

    # Log tool invocation
    logger.info(json.dumps({
        "event": "tool_invocation",
        "tool": "delete_task",
        "user_id": user_id,
        "parameters": {"task_id": task_id},
        "timestamp": start_time.isoformat()
    }))

    try:
        # Validate input with Pydantic schema
        input_data = DeleteTaskInput(
            user_id=user_id,
            task_id=task_id
        )

        # Get database session
        db = next(get_db())

        # Delegate to service layer
        delete_task(db=db, user_id=input_data.user_id, task_id=input_data.task_id)

        # Format output
        output = DeleteTaskOutput(
            task_id=input_data.task_id,
            status="deleted"
        )

        # Log success
        execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        logger.info(json.dumps({
            "event": "tool_success",
            "tool": "delete_task",
            "user_id": user_id,
            "result": {"task_id": input_data.task_id, "status": "deleted"},
            "execution_time_ms": execution_time,
            "timestamp": datetime.utcnow().isoformat()
        }))

        return output.dict()

    except ValidationError as e:
        # Validation error
        logger.warning(json.dumps({
            "event": "tool_error",
            "tool": "delete_task",
            "user_id": user_id,
            "error_type": "ValidationError",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }))
        return ToolError(
            error=ToolErrorType.VALIDATION_ERROR,
            detail=str(e)
        ).dict()

    except HTTPException as e:
        # HTTP exception from service layer
        if e.status_code == 404:
            error_type = ToolErrorType.NOT_FOUND_ERROR
        elif e.status_code == 403:
            error_type = ToolErrorType.AUTHORIZATION_ERROR
        else:
            error_type = ToolErrorType.SERVER_ERROR

        logger.warning(json.dumps({
            "event": "tool_error",
            "tool": "delete_task",
            "user_id": user_id,
            "error_type": error_type.value,
            "error": e.detail,
            "timestamp": datetime.utcnow().isoformat()
        }))
        return ToolError(
            error=error_type,
            detail=e.detail
        ).dict()

    except Exception as e:
        # Server error
        logger.error(json.dumps({
            "event": "tool_error",
            "tool": "delete_task",
            "user_id": user_id,
            "error_type": "ServerError",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), exc_info=True)
        return ToolError(
            error=ToolErrorType.SERVER_ERROR,
            detail="An error occurred while deleting the task"
        ).dict()
