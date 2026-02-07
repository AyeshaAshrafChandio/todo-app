"""
Mock Agent Service for Development/Testing

This service simulates OpenAI Agent responses without making actual API calls.
Use this when:
- OpenAI API quota is exceeded
- Testing frontend without API costs
- Developing offline

To enable: Set MOCK_OPENAI=true in backend/.env
"""

from typing import List, Dict, Any, Tuple
import logging
import random
from app.models.message import Message, MessageRole

logger = logging.getLogger(__name__)


class MockAgentService:
    """
    Mock implementation of AgentService for testing without OpenAI API.

    This service simulates realistic agent responses and tool calls
    based on common user intents.
    """

    def __init__(self):
        """Initialize mock agent service."""
        logger.info("MockAgentService initialized (no API calls will be made)")
        self.model = "mock-gpt-4o-mini"
        self.max_tokens = 4096

    def build_agent_context(self, messages: List[Message]) -> List[Dict[str, str]]:
        """Build agent message context (same as real service)."""
        return [
            {
                "role": msg.role.value,
                "content": msg.content
            }
            for msg in messages
        ]

    def get_system_prompt(self) -> str:
        """Get system prompt (same as real service)."""
        return """You are a helpful AI assistant for a task management application."""

    async def run_agent(
        self,
        user_message: str,
        conversation_history: List[Message],
        user_id: str
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Simulate agent response based on user message intent.

        Args:
            user_message: The user's message text
            conversation_history: Previous messages (not used in mock)
            user_id: UUID of the user

        Returns:
            Tuple of (assistant_response, tool_calls)
        """
        logger.info(
            f"Mock agent processing message: '{user_message[:50]}...'",
            extra={"user_id": user_id}
        )

        # Normalize message for intent detection
        msg_lower = user_message.lower()

        # Detect intent and generate appropriate response
        if any(word in msg_lower for word in ["add", "create", "new task", "remind me"]):
            return self._handle_create_task(user_message, user_id)

        elif any(word in msg_lower for word in ["list", "show", "what are", "my tasks", "tasks"]):
            return self._handle_list_tasks(user_message, user_id)

        elif any(word in msg_lower for word in ["complete", "done", "finish", "mark as"]):
            return self._handle_complete_task(user_message, user_id)

        elif any(word in msg_lower for word in ["delete", "remove", "cancel"]):
            return self._handle_delete_task(user_message, user_id)

        elif any(word in msg_lower for word in ["update", "change", "edit", "modify"]):
            return self._handle_update_task(user_message, user_id)

        elif any(word in msg_lower for word in ["hello", "hi", "hey"]):
            return self._handle_greeting(user_message, user_id)

        elif any(word in msg_lower for word in ["help", "what can you do"]):
            return self._handle_help(user_message, user_id)

        else:
            return self._handle_general(user_message, user_id)

    def _handle_create_task(self, message: str, user_id: str) -> Tuple[str, List[Dict[str, Any]]]:
        """Simulate creating a task."""
        # Extract task title from message (simple heuristic)
        title = message.replace("add", "").replace("create", "").replace("task", "").strip()
        if not title or len(title) < 3:
            title = "New task from chat"

        tool_calls = [{
            "tool": "add_task",
            "arguments": {
                "title": title,
                "description": f"Task created via chat: {message}"
            }
        }]

        response = f"I've added '{title}' to your task list."
        return response, tool_calls

    def _handle_list_tasks(self, message: str, user_id: str) -> Tuple[str, List[Dict[str, Any]]]:
        """Simulate listing tasks."""
        # Determine status filter
        if "completed" in message.lower() or "done" in message.lower():
            status = "completed"
            response = "Here are your completed tasks. (Mock: In real mode, this would show actual completed tasks)"
        elif "pending" in message.lower() or "active" in message.lower():
            status = "pending"
            response = "Here are your pending tasks. (Mock: In real mode, this would show actual pending tasks)"
        else:
            status = "all"
            response = "Here are all your tasks. (Mock: In real mode, this would show actual tasks from database)"

        tool_calls = [{
            "tool": "list_tasks",
            "arguments": {"status": status}
        }]

        return response, tool_calls

    def _handle_complete_task(self, message: str, user_id: str) -> Tuple[str, List[Dict[str, Any]]]:
        """Simulate completing a task."""
        # Extract task ID if mentioned (simple heuristic)
        import re
        task_id_match = re.search(r'\b(\d+)\b', message)
        task_id = int(task_id_match.group(1)) if task_id_match else 1

        tool_calls = [{
            "tool": "update_task",
            "arguments": {
                "task_id": task_id,
                "updates": {"completed": True}
            }
        }]

        response = f"I've marked task #{task_id} as completed. Great job!"
        return response, tool_calls

    def _handle_delete_task(self, message: str, user_id: str) -> Tuple[str, List[Dict[str, Any]]]:
        """Simulate deleting a task."""
        import re
        task_id_match = re.search(r'\b(\d+)\b', message)
        task_id = int(task_id_match.group(1)) if task_id_match else 1

        tool_calls = [{
            "tool": "delete_task",
            "arguments": {"task_id": task_id}
        }]

        response = f"I've deleted task #{task_id} from your list."
        return response, tool_calls

    def _handle_update_task(self, message: str, user_id: str) -> Tuple[str, List[Dict[str, Any]]]:
        """Simulate updating a task."""
        import re
        task_id_match = re.search(r'\b(\d+)\b', message)
        task_id = int(task_id_match.group(1)) if task_id_match else 1

        tool_calls = [{
            "tool": "update_task",
            "arguments": {
                "task_id": task_id,
                "updates": {"title": "Updated task title"}
            }
        }]

        response = f"I've updated task #{task_id}."
        return response, tool_calls

    def _handle_greeting(self, message: str, user_id: str) -> Tuple[str, List[Dict[str, Any]]]:
        """Handle greeting messages."""
        greetings = [
            "Hello! I'm your task management assistant. How can I help you today?",
            "Hi there! Ready to help you manage your tasks. What would you like to do?",
            "Hey! I can help you create, list, update, or complete tasks. What do you need?"
        ]
        response = random.choice(greetings)
        return response, []

    def _handle_help(self, message: str, user_id: str) -> Tuple[str, List[Dict[str, Any]]]:
        """Handle help requests."""
        response = """I can help you manage your tasks! Here's what I can do:

• **Create tasks**: "Add buy groceries" or "Create a task to call mom"
• **List tasks**: "Show my tasks" or "What are my pending tasks?"
• **Complete tasks**: "Mark task 1 as done" or "Complete task 2"
• **Update tasks**: "Update task 3" or "Change task 1 title"
• **Delete tasks**: "Delete task 2" or "Remove task 5"

Just tell me what you'd like to do in natural language!

(Note: Running in MOCK mode - no real API calls are being made)"""
        return response, []

    def _handle_general(self, message: str, user_id: str) -> Tuple[str, List[Dict[str, Any]]]:
        """Handle general messages."""
        responses = [
            "I'm here to help with your tasks. Try asking me to add, list, or complete tasks!",
            "I can help you manage your tasks. What would you like to do?",
            "I'm your task assistant. You can ask me to create tasks, show your task list, or mark tasks as complete."
        ]
        response = random.choice(responses)
        return response, []
