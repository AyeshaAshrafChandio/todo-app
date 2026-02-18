"""
AgentService for orchestrating OpenAI Agent interactions.

This service manages the OpenAI Agent lifecycle, context building,
and tool invocation for the AI Chat Backend (Spec 005).
"""

from typing import List, Dict, Any, Optional
import logging
import json
from openai import AsyncOpenAI
from app.config import settings
from app.models.message import Message, MessageRole
from app.services.mcp_client import MCPClient

logger = logging.getLogger(__name__)


class AgentService:
    """
    Service for orchestrating OpenAI Agent interactions.

    This service handles:
    - OpenAI client initialization
    - Agent context building from conversation history
    - Agent execution with tool invocation
    - Response generation and formatting
    """

    def __init__(self):
        """Initialize the agent service with OpenAI client and MCP client."""
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.mcp_client = MCPClient()
        self.model = settings.OPENAI_MODEL
        self.max_tokens = settings.OPENAI_MAX_TOKENS

    def build_agent_context(self, messages: List[Message]) -> List[Dict[str, str]]:
        """
        Build agent message context from conversation history.

        Args:
            messages: List of Message objects from conversation history

        Returns:
            List of message dictionaries in OpenAI format

        Example:
            ```python
            messages = [
                Message(role=MessageRole.USER, content="Hello"),
                Message(role=MessageRole.ASSISTANT, content="Hi there!")
            ]
            context = service.build_agent_context(messages)
            # Returns: [
            #     {"role": "user", "content": "Hello"},
            #     {"role": "assistant", "content": "Hi there!"}
            # ]
            ```
        """
        return [
            {
                "role": msg.role.value,
                "content": msg.content
            }
            for msg in messages
        ]

    def get_system_prompt(self) -> str:
        """
        Get the system prompt for the AI agent.

        Returns:
            System prompt string with agent behavior guidelines

        Note:
            This prompt defines the agent's personality, capabilities,
            and behavior constraints.
        """
        return """You are a helpful AI assistant for a task management application.

Your capabilities:
- Create tasks for users using natural language
- List and search tasks
- Update task details and completion status
- Delete tasks

Behavior guidelines:
- Be concise and friendly in your responses
- Confirm actions after executing them (e.g., "I've added 'buy groceries' to your task list")
- Ask for clarification if user intent is ambiguous
- For destructive actions (delete, bulk operations), ask for confirmation first
- Use the available tools to perform task operations - never claim to do something without invoking the appropriate tool
- If a tool invocation fails, explain the issue to the user in a friendly way

Task management rules:
- Always use the create_task tool to create new tasks
- Always use the list_tasks tool to retrieve task information
- Always use the update_task tool to modify tasks
- Always use the delete_task tool to remove tasks
- Never make up task IDs or data - always use the tools to get accurate information

Response format:
- Provide natural, conversational responses
- Confirm what action was taken
- If multiple tasks match a query, list them and ask for clarification
- Keep responses concise but informative"""

    async def run_agent(
        self,
        user_message: str,
        conversation_history: List[Message],
        user_id: str
    ) -> tuple[str, List[Dict[str, Any]]]:
        """
        Run the OpenAI Agent to process user message and invoke tools.

        Args:
            user_message: The user's message text
            conversation_history: Previous messages in the conversation
            user_id: UUID of the user (for tool authorization)

        Returns:
            Tuple of (assistant_response, tool_calls)
            - assistant_response: Natural language response from agent
            - tool_calls: List of tools invoked with their arguments

        Raises:
            Exception: If OpenAI API call fails

        Example:
            ```python
            response, tools = await service.run_agent(
                user_message="Add buy groceries to my list",
                conversation_history=[],
                user_id="550e8400-..."
            )
            print(f"Response: {response}")
            print(f"Tools used: {[t['tool'] for t in tools]}")
            ```
        """
        # Build message context
        messages = [
            {"role": "system", "content": self.get_system_prompt()}
        ]

        # Add conversation history
        messages.extend(self.build_agent_context(conversation_history))

        # Add current user message
        messages.append({"role": "user", "content": user_message})

        # Track tool calls
        tool_calls_made = []

        try:
            # Call OpenAI API with function calling
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.mcp_client.get_tool_definitions(),
                tool_choice="auto",
                max_tokens=self.max_tokens
            )

            # Get the assistant's response
            assistant_message = response.choices[0].message

            # Check if agent wants to call tools
            if assistant_message.tool_calls:
                # Execute tool calls
                for tool_call in assistant_message.tool_calls:
                    tool_name = tool_call.function.name

                    # SECURITY FIX: Use json.loads() instead of eval()
                    # eval() is dangerous and can execute arbitrary code
                    try:
                        tool_args = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError as e:
                        logger.error(
                            f"Failed to parse tool arguments: {str(e)}",
                            extra={
                                "tool": tool_name,
                                "arguments_raw": tool_call.function.arguments,
                                "user_id": user_id
                            }
                        )
                        raise ValueError(f"Invalid tool arguments format: {str(e)}")

                    logger.info(
                        f"Agent invoking tool: {tool_name}",
                        extra={
                            "tool": tool_name,
                            "arguments": tool_args,
                            "user_id": user_id
                        }
                    )

                    # Invoke the tool via MCP client
                    tool_result = await self.mcp_client.invoke_tool(
                        tool_name=tool_name,
                        arguments=tool_args,
                        user_id=user_id
                    )

                    # Track tool call
                    tool_calls_made.append({
                        "tool": tool_name,
                        "arguments": tool_args
                    })

                    # Add tool result to messages for agent to process
                    messages.append({
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [
                            {
                                "id": tool_call.id,
                                "type": "function",
                                "function": {
                                    "name": tool_name,
                                    "arguments": tool_call.function.arguments
                                }
                            }
                        ]
                    })
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(tool_result)
                    })

                # Get final response after tool execution
                final_response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=self.max_tokens
                )

                assistant_response = final_response.choices[0].message.content

            else:
                # No tool calls, just return the response
                assistant_response = assistant_message.content

            return assistant_response, tool_calls_made

        except Exception as e:
            logger.error(
                f"Agent execution failed: {str(e)}",
                extra={"user_id": user_id, "error": str(e)}
            )
            raise
