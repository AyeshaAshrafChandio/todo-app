#!/usr/bin/env python3
"""
Simulate frontend chat request to diagnose 500 error.
This script mimics what the frontend does when sending a chat message.
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from dotenv import load_dotenv
load_dotenv("backend/.env")


async def test_chat_flow():
    """Simulate the complete chat flow to identify the error."""
    print("=" * 60)
    print("Chat Flow Simulation - Diagnosing 500 Error")
    print("=" * 60)
    print()

    # Step 1: Import and initialize services
    print("Step 1: Initializing services...")
    try:
        from app.services.agent_service import AgentService
        from app.config import settings

        print(f"[OK] Services imported")
        print(f"  Model: {settings.OPENAI_MODEL}")
        print(f"  API Key: {'*' * 20}...{settings.OPENAI_API_KEY[-10:]}")
    except Exception as e:
        print(f"[FAIL] Import failed: {e}")
        return

    # Step 2: Create agent service
    print("\nStep 2: Creating AgentService...")
    try:
        agent_service = AgentService()
        print("[OK] AgentService created")
    except Exception as e:
        print(f"[FAIL] AgentService creation failed: {e}")
        import traceback
        traceback.print_exc()
        return

    # Step 3: Simulate chat request
    print("\nStep 3: Simulating chat request...")
    print("  Message: 'List my tasks'")
    print("  User ID: test-user-123")
    print()

    try:
        print("Calling agent_service.run_agent()...")
        response, tool_calls = await agent_service.run_agent(
            user_message="List my tasks",
            conversation_history=[],
            user_id="550e8400-e29b-41d4-a716-446655440000"
        )

        print("\n[SUCCESS] Chat request completed!")
        print(f"Response: {response}")
        print(f"Tool calls: {len(tool_calls)}")

        if tool_calls:
            for tc in tool_calls:
                print(f"  - {tc['tool']}: {tc['arguments']}")

        return True

    except Exception as e:
        print("\n" + "=" * 60)
        print("ERROR CAPTURED - This is what's causing the 500 error:")
        print("=" * 60)
        print(f"\nError Type: {type(e).__name__}")
        print(f"Error Message: {str(e)}")
        print()

        # Check for specific error types
        if "insufficient_quota" in str(e).lower() or "429" in str(e):
            print("DIAGNOSIS: OpenAI API Quota Exceeded")
            print("-" * 60)
            print("Your OpenAI API key has exceeded its usage quota.")
            print()
            print("SOLUTIONS:")
            print()
            print("1. Add Billing to OpenAI Account (Recommended)")
            print("   - Visit: https://platform.openai.com/account/billing")
            print("   - Add payment method")
            print("   - Set usage limit: $5-10/month for development")
            print("   - Cost: ~$0.0003 per message with gpt-4o-mini")
            print()
            print("2. Use Different API Key")
            print("   - Get new key: https://platform.openai.com/api-keys")
            print("   - Update backend/.env: OPENAI_API_KEY=sk-your-key")
            print()
            print("3. Use Mock Service (Testing Only)")
            print("   - I can create a mock agent service")
            print("   - Allows frontend testing without API calls")
            print("   - No real AI responses, just simulated data")

        elif "model_not_found" in str(e).lower() or "404" in str(e):
            print("DIAGNOSIS: Model Not Found or Inaccessible")
            print("-" * 60)
            print("The configured model is not accessible with your API key.")
            print()
            print("SOLUTION:")
            print("Update backend/.env:")
            print("  OPENAI_MODEL=gpt-3.5-turbo  # Most accessible")

        elif "invalid" in str(e).lower() and "api" in str(e).lower():
            print("DIAGNOSIS: Invalid API Key")
            print("-" * 60)
            print("The OpenAI API key is invalid or expired.")
            print()
            print("SOLUTION:")
            print("1. Get new key: https://platform.openai.com/api-keys")
            print("2. Update backend/.env: OPENAI_API_KEY=sk-your-key")

        else:
            print("DIAGNOSIS: Unexpected Error")
            print("-" * 60)
            print("Full traceback:")
            print()
            import traceback
            traceback.print_exc()

        print()
        print("=" * 60)
        return False


async def main():
    """Run the diagnostic test."""
    success = await test_chat_flow()

    print()
    print("=" * 60)
    print("NEXT STEPS")
    print("=" * 60)

    if success:
        print("\n[SUCCESS] Chat integration is working!")
        print("\nYou can now:")
        print("1. Start the backend: cd backend && uvicorn app.main:app --reload --port 8001")
        print("2. Test from frontend")
    else:
        print("\n[ACTION REQUIRED] Fix the error above, then:")
        print("1. Restart backend: cd backend && uvicorn app.main:app --reload --port 8001")
        print("2. Test again")
        print()
        print("Need help? I can:")
        print("- Create a mock service for testing without API calls")
        print("- Help you configure a different OpenAI model")
        print("- Provide alternative testing approaches")


if __name__ == "__main__":
    asyncio.run(main())
