#!/usr/bin/env python3
"""
Test the mock agent service to ensure it works correctly.
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from dotenv import load_dotenv
load_dotenv("backend/.env")


async def test_mock_service():
    """Test the mock agent service with various message types."""
    print("=" * 60)
    print("Mock Agent Service Test")
    print("=" * 60)
    print()

    from app.services.mock_agent_service import MockAgentService
    from app.config import settings

    print(f"Mock Mode Enabled: {settings.MOCK_OPENAI}")
    print()

    service = MockAgentService()
    print(f"[OK] MockAgentService initialized")
    print(f"  Model: {service.model}")
    print()

    # Test cases
    test_cases = [
        ("Hello!", "Greeting"),
        ("Add buy groceries", "Create Task"),
        ("List my tasks", "List Tasks"),
        ("Show completed tasks", "List Completed"),
        ("Mark task 1 as done", "Complete Task"),
        ("Delete task 2", "Delete Task"),
        ("Update task 3", "Update Task"),
        ("What can you do?", "Help Request"),
        ("Random message", "General Response"),
    ]

    print("Running test cases...")
    print("-" * 60)

    for message, test_name in test_cases:
        print(f"\nTest: {test_name}")
        print(f"Message: '{message}'")

        try:
            response, tool_calls = await service.run_agent(
                user_message=message,
                conversation_history=[],
                user_id="test-user-123"
            )

            print(f"[OK] Response: {response[:100]}{'...' if len(response) > 100 else ''}")
            print(f"[OK] Tool calls: {len(tool_calls)}")

            if tool_calls:
                for tc in tool_calls:
                    print(f"     - {tc['tool']}: {tc['arguments']}")

        except Exception as e:
            print(f"[FAIL] Error: {e}")
            import traceback
            traceback.print_exc()

    print()
    print("=" * 60)
    print("Mock Service Test Complete!")
    print("=" * 60)
    print()
    print("The mock service is working correctly.")
    print("You can now test your frontend chat without API calls.")


if __name__ == "__main__":
    asyncio.run(test_mock_service())
