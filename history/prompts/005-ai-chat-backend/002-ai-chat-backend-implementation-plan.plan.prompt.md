---
id: 002
title: AI Chat Backend Implementation Plan
stage: plan
date: 2026-02-06
surface: agent
model: claude-sonnet-4-5
feature: 005-ai-chat-backend
branch: 005-ai-chat-backend
user: Ali Haider
command: /sp.plan
labels: ["plan", "phase-iii", "ai-chatbot", "openai-agents", "mcp-tools", "stateless-architecture"]
links:
  spec: specs/005-ai-chat-backend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/005-ai-chat-backend/plan.md
  - specs/005-ai-chat-backend/research.md
  - specs/005-ai-chat-backend/data-model.md
  - specs/005-ai-chat-backend/contracts/chat-api.yaml
  - specs/005-ai-chat-backend/quickstart.md
tests:
  - N/A (planning artifact)
---

## Prompt

/sp.plan

## Response snapshot

Generated comprehensive implementation plan for AI Chat Backend (005-ai-chat-backend) following Phase III constitutional principles:

**Phase 0: Research & Discovery** (research.md):
- OpenAI Agents SDK integration with FastAPI (AsyncOpenAI client, assistant creation, thread management)
- MCP SDK usage for tool invocation (Tool decorator, registration, OpenAI function calling)
- Stateless conversation management (database-backed context reconstruction)
- Agent failure handling (retry logic, graceful degradation, user-friendly errors)
- Token limit management (last 50 messages, ~100k tokens, intelligent truncation)
- Agent prompt engineering (structured system prompt with capabilities, tools, behavior guidelines, examples)

**Key Technology Decisions**:
- OpenAI Model: GPT-4 Turbo (gpt-4-turbo-preview) - 128k context window
- MCP SDK: mcp-python 0.1.0+ (official implementation)
- Database: Add Conversation and Message tables with foreign keys to User
- Performance: ~4-6 seconds typical response time (database 50ms, agent 3-5s, tools 100-500ms)

**Phase 1: Design & Contracts** (data-model.md, contracts/chat-api.yaml, quickstart.md):

1. **Data Models** (data-model.md):
   - Conversation model: id, user_id, created_at, updated_at
   - Message model: id, conversation_id, user_id, role (user/assistant), content (max 10k chars), created_at
   - Relationships: User 1:N Conversation 1:N Message
   - Indexes: user_id, conversation_id, created_at, composite (conversation_id, created_at)
   - Migration script with proper foreign keys and cascade deletes

2. **API Contract** (contracts/chat-api.yaml):
   - POST /api/chat endpoint with JWT authentication
   - Request: conversation_id (nullable integer), message (string, 1-10,000 chars)
   - Response: conversation_id (integer), response (string), tool_calls (array)
   - Error responses: 400 (validation), 401 (unauthorized), 403 (forbidden), 404 (not found), 429 (rate limit), 500 (server error)
   - Security: Bearer JWT token required, user_id extracted from token

3. **Setup Guide** (quickstart.md):
   - OpenAI API key configuration
   - Database migration steps
   - MCP Tool Server setup (placeholder for spec 006)
   - Testing workflow (new conversation, continue conversation, resume after restart)
   - Troubleshooting common issues

**Constitution Check**: All 11 principles pass
- Principle VI (Stateless Architecture): No in-memory session state
- Principle VII (Agent Behavior Constraints): Agents decide, tools execute
- Principle VIII (MCP Tool Design): Tools validate authorization server-side
- Principle X (Backward Compatibility): Phase I & II APIs unchanged
- Principle XI (Multi-Spec Architecture): Clear boundaries with 006 (MCP) and 007 (Frontend)

**Project Structure**:
- Backend extension: New models (conversation.py, message.py), routes (chat.py), services (agent_service.py, conversation_service.py, mcp_client.py)
- Migration: alembic/versions/xxx_add_conversation_message_tables.py
- Tests: test_chat_endpoint.py, test_agent_service.py, test_conversation_service.py, test_mcp_client.py

**Performance Goals**:
- Chat response time: <10 seconds (includes agent reasoning + tool execution)
- Concurrent requests: 100 users without degradation
- Database query time: <100ms for conversation history loading
- Agent reasoning time: <5 seconds (OpenAI API dependent)

**Security Requirements**:
- JWT authentication on all requests
- User ID extracted only from JWT (never from client input)
- Cross-user conversation access prevented
- Input validation for malicious content
- Rate limiting (60 requests per minute per user)

## Outcome

- ✅ Impact: Created production-ready implementation plan for AI Chat Backend with stateless architecture, OpenAI Agents SDK integration, and MCP tool delegation
- 🧪 Tests: N/A (planning artifact) - Test strategy defined for implementation phase
- 📁 Files: Created plan.md (technical plan), research.md (Phase 0 research), data-model.md (database schema), contracts/chat-api.yaml (OpenAPI spec), quickstart.md (setup guide)
- 🔁 Next prompts: Ready for `/sp.tasks` to generate testable tasks, then use `fastapi-backend` agent for implementation
- 🧠 Reflection: Plan successfully balances AI-native architecture with constitutional requirements. Stateless design ensures scalability and conversation resume. Agent-tool separation maintains clear boundaries. Database schema supports efficient conversation history loading. OpenAPI contract provides clear API surface. Quickstart guide enables rapid local development setup. All Phase 0 research decisions documented with rationale and alternatives considered.

## Evaluation notes (flywheel)

- Failure modes observed: None - plan generation successful, all constitutional principles pass, all Phase 0 and Phase 1 artifacts complete
- Graders run and results (PASS/FAIL): PASS - Constitution check passes all 11 principles, data models align with existing schema patterns, API contract follows REST conventions, performance goals measurable, security requirements explicit
- Prompt variant (if applicable): N/A - Standard planning workflow with Phase III constitutional principles
- Next experiment (smallest change to try): Proceed with `/sp.tasks` to validate plan completeness through task breakdown, particularly agent service implementation, conversation persistence, and MCP client integration patterns
