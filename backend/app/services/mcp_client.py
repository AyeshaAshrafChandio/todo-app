"""
MCPClient for invoking MCP tools from the AI agent.

This client provides a bridge between the OpenAI Agent and MCP tools,
handling tool registration and invocation (Spec 005 + Spec 006).

Updated in Spec 006 to use production MCP tool handlers.
"""

from typing import Dict, Any, List, Optional
import logging
from app.services.mcp_tools import (
    add_task,
    list_tasks,
    get_task,
    update_task_tool,
    delete_task_tool
)

logger = logging.getLogger(__name__)


class MCPClient:
    """
    Client for invoking MCP (Model Context Protocol) tools.

    This client manages tool registration and invocation for the AI agent.
    Production tools implemented in Spec 006 (MCP Task Tools).

    Attributes:
        tools: Dictionary of registered tool handlers
    """

    def __init__(self):
        """Initialize the MCP client with production tools."""
        self.tools = self._register_tools()

    def _register_tools(self) -> Dict[str, Any]:
        """
        Register production MCP tool handlers.

        Returns:
            Dictionary mapping tool names to tool handler functions

        Note:
            Production implementation from Spec 006 (MCP Task Tools).
            All tools delegate to existing service layer and enforce authorization.
        """
        return {
            "add_task": add_task,
            "list_tasks": list_tasks,
            "get_task": get_task,
            "update_task": update_task_tool,
            "delete_task": delete_task_tool
        }

    def get_tool_definitions_legacy(self) -> Dict[str, Dict[str, Any]]:
        """
        Get legacy tool definitions (for backward compatibility).

        Returns:
            Dictionary mapping tool names to tool definitions

        Note:
            Kept for backward compatibility. New code should use get_tool_definitions().
        """
        return {
            "create_task": {
                "name": "add_task",
                "description": "Create a new task for the user",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Task title"
                        },
                        "description": {
                            "type": "string",
                            "description": "Task description (optional)"
                        }
                    },
                    "required": ["title"]
                }
            },
            "list_tasks": {
                "name": "list_tasks",
                "description": "List all tasks for the user",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "enum": ["pending", "completed", "all"],
                            "description": "Filter tasks by status"
                        }
                    }
                }
            },
            "update_task": {
                "name": "update_task",
                "description": "Update an existing task",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "integer",
                            "description": "ID of the task to update"
                        },
                        "title": {
                            "type": "string",
                            "description": "New task title (optional)"
                        },
                        "description": {
                            "type": "string",
                            "description": "New task description (optional)"
                        },
                        "completed": {
                            "type": "boolean",
                            "description": "Mark task as completed (optional)"
                        }
                    },
                    "required": ["task_id"]
                }
            },
            "delete_task": {
                "name": "delete_task",
                "description": "Delete a task",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "integer",
                            "description": "ID of the task to delete"
                        }
                    },
                    "required": ["task_id"]
                }
            },
            "get_task": {
                "name": "get_task",
                "description": "Get details of a specific task",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "integer",
                            "description": "ID of the task to retrieve"
                        }
                    },
                    "required": ["task_id"]
                }
            }
        }

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """
        Get tool definitions for OpenAI function calling.

        Returns:
            List of tool definitions in OpenAI function calling format
        """
        legacy_defs = self.get_tool_definitions_legacy()
        return [
            {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["parameters"]
                }
            }
            for tool in legacy_defs.values()
        ]

    async def invoke_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        """
        Invoke a production MCP tool with the given arguments.

        Args:
            tool_name: Name of the tool to invoke
            arguments: Tool arguments
            user_id: UUID of the user (for authorization)

        Returns:
            Tool execution result

        Raises:
            ValueError: If tool is not found

        Note:
            Production implementation from Spec 006 (MCP Task Tools).
            All tools delegate to existing service layer.
        """
        # Map legacy tool names to new tool names
        tool_name_map = {
            "create_task": "add_task",
            "add_task": "add_task",
            "list_tasks": "list_tasks",
            "get_task": "get_task",
            "update_task": "update_task",
            "delete_task": "delete_task"
        }

        mapped_tool_name = tool_name_map.get(tool_name, tool_name)

        if mapped_tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not found")

        logger.info(
            f"Tool invocation: {mapped_tool_name}",
            extra={
                "tool": mapped_tool_name,
                "arguments": arguments,
                "user_id": user_id
            }
        )

        # Get the tool handler function
        tool_handler = self.tools[mapped_tool_name]

        # Add user_id to arguments
        tool_args = {**arguments, "user_id": user_id}

        # Invoke the production tool handler
        result = await tool_handler(**tool_args)

        return result
