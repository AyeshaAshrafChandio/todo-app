#!/usr/bin/env python3
"""
Test script for OpenAI integration debugging.

This script tests the OpenAI API connection and agent service
to identify configuration or integration issues.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()


async def test_openai_connection():
    """Test basic OpenAI API connection."""
    print("=" * 60)
    print("TEST 1: OpenAI API Connection")
    print("=" * 60)

    try:
        from openai import AsyncOpenAI
        from app.config import settings

        print("[OK] OpenAI library imported successfully")
        print(f"  Model: {settings.OPENAI_MODEL}")
        print(f"  Max Tokens: {settings.OPENAI_MAX_TOKENS}")

        # Check API key
        api_key = settings.OPENAI_API_KEY
        if not api_key or api_key == "your-openai-api-key-here":
            print("[FAIL] OPENAI_API_KEY is not configured!")
            print("  Get your API key from: https://platform.openai.com/api-keys")
            return False

        print(f"[OK] API Key configured (length: {len(api_key)})")

        # Test API connection
        print("\nTesting API connection...")
        client = AsyncOpenAI(api_key=api_key)

        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'Hello' in one word."}
            ],
            max_tokens=10
        )

        result = response.choices[0].message.content
        print("[OK] API connection successful!")
        print(f"  Response: {result}")
        return True

    except Exception as e:
        print(f"[FAIL] OpenAI connection failed: {str(e)}")
        print(f"  Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False


async def test_tool_definitions():
    """Test MCP tool definitions."""
    print("\n" + "=" * 60)
    print("TEST 2: MCP Tool Definitions")
    print("=" * 60)

    try:
        from app.services.mcp_client import MCPClient

        client = MCPClient()
        tools = client.get_tool_definitions()

        print(f"[OK] MCP Client initialized")
        print(f"  Registered tools: {len(tools)}")

        for tool in tools:
            tool_name = tool['function']['name']
            tool_desc = tool['function']['description']
            print(f"\n  Tool: {tool_name}")
            print(f"    Description: {tool_desc}")
            print(f"    Parameters: {list(tool['function']['parameters']['properties'].keys())}")

        return True

    except Exception as e:
        print(f"[FAIL] Tool definitions failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_agent_service():
    """Test AgentService initialization."""
    print("\n" + "=" * 60)
    print("TEST 3: AgentService Initialization")
    print("=" * 60)

    try:
        from app.services.agent_service import AgentService

        service = AgentService()
        print(f"[OK] AgentService initialized")
        print(f"  Model: {service.model}")
        print(f"  Max Tokens: {service.max_tokens}")

        # Test system prompt
        system_prompt = service.get_system_prompt()
        print(f"[OK] System prompt generated ({len(system_prompt)} chars)")

        return True

    except Exception as e:
        print(f"[FAIL] AgentService initialization failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_simple_agent_call():
    """Test a simple agent call without tools."""
    print("\n" + "=" * 60)
    print("TEST 4: Simple Agent Call (No Tools)")
    print("=" * 60)

    try:
        from app.services.agent_service import AgentService

        service = AgentService()

        print("Sending test message: 'Hello, how are you?'")
        response, tool_calls = await service.run_agent(
            user_message="Hello, how are you?",
            conversation_history=[],
            user_id="test-user-123"
        )

        print(f"[OK] Agent responded successfully")
        print(f"  Response: {response}")
        print(f"  Tool calls: {len(tool_calls)}")

        return True

    except Exception as e:
        print(f"[FAIL] Agent call failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_agent_with_tools():
    """Test agent call that should trigger tool usage."""
    print("\n" + "=" * 60)
    print("TEST 5: Agent Call with Tool Invocation")
    print("=" * 60)

    try:
        from app.services.agent_service import AgentService

        service = AgentService()

        print("Sending test message: 'List my tasks'")
        print("(This should trigger the list_tasks tool)")

        response, tool_calls = await service.run_agent(
            user_message="List my tasks",
            conversation_history=[],
            user_id="550e8400-e29b-41d4-a716-446655440000"  # Valid UUID
        )

        print(f"[OK] Agent responded successfully")
        print(f"  Response: {response}")
        print(f"  Tool calls made: {len(tool_calls)}")

        if tool_calls:
            for tc in tool_calls:
                print(f"    - {tc['tool']}: {tc['arguments']}")

        return True

    except Exception as e:
        print(f"[FAIL] Agent call with tools failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("OpenAI Integration Test Suite")
    print("=" * 60)
    print()

    results = []

    # Test 1: OpenAI Connection
    results.append(("OpenAI Connection", await test_openai_connection()))

    # Test 2: Tool Definitions
    results.append(("Tool Definitions", await test_tool_definitions()))

    # Test 3: AgentService Init
    results.append(("AgentService Init", await test_agent_service()))

    # Test 4: Simple Agent Call (only if previous tests passed)
    if all(r[1] for r in results):
        results.append(("Simple Agent Call", await test_simple_agent_call()))

    # Test 5: Agent with Tools (only if all previous tests passed)
    if all(r[1] for r in results):
        results.append(("Agent with Tools", await test_agent_with_tools()))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    for test_name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status}: {test_name}")

    total = len(results)
    passed = sum(1 for _, p in results if p)

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n[SUCCESS] All tests passed! OpenAI integration is working correctly.")
        return 0
    else:
        print(f"\n[ERROR] {total - passed} test(s) failed. Check errors above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
