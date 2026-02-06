# Implementation Plan: AI Chat Backend

**Branch**: `005-ai-chat-backend` | **Date**: 2026-02-06 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-ai-chat-backend/spec.md`

**Note**: This plan implements Phase III AI-powered chatbot backend with stateless architecture, OpenAI Agents SDK integration, and MCP tool delegation.

## Summary

Implement a stateless chat API endpoint that enables users to manage tasks through natural language conversations. The system integrates OpenAI Agents SDK for reasoning, persists conversation history in PostgreSQL, and delegates all task mutations to MCP tools. The architecture maintains backward compatibility with Phase I & II REST APIs while demonstrating production-grade AI integration with proper separation of concerns.

**Primary Requirement**: POST /api/chat endpoint accepting conversation_id and message, returning natural language responses with tool invocation transparency.

**Technical Approach**: FastAPI endpoint → JWT authentication → Load conversation from DB → Build agent context → Run OpenAI Agent → Invoke MCP tools → Persist response → Return JSON. No server-side memory between requests.

## Technical Context

**Language/Version**: Python 3.11+ (matches existing backend)
**Primary Dependencies**:
- FastAPI (existing backend framework)
- OpenAI Agents SDK (agent orchestration)
- MCP SDK (tool invocation protocol)
- SQLModel (existing ORM)
- PostgreSQL (existing database via Neon)
- PyJWT (existing JWT verification)

**Storage**: PostgreSQL (Neon Serverless) - add Conversation and Message tables
**Testing**: pytest (existing test framework)
**Target Platform**: Linux server (same as existing backend)
**Project Type**: Web application (backend extension)

**Performance Goals**:
- Chat response time: <10 seconds (includes agent reasoning + tool execution)
- Concurrent requests: 100 users without degradation
- Database query time: <100ms for conversation history loading
- Agent reasoning time: <5 seconds (OpenAI API dependent)

**Constraints**:
- Stateless architecture: No in-memory session state
- Backward compatibility: Phase I & II APIs unchanged
- Security: JWT authentication on all requests
- Tool delegation: Agents never directly mutate database
- Conversation persistence: All context in database

**Scale/Scope**:
- Expected users: 1,000+ concurrent conversations
- Conversation history: Up to 100 messages per conversation
- Message size: Max 10,000 characters
- Tool invocations: 1-5 per user message

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Spec-Driven Development ✅ PASS
- Implementation follows approved spec (005-ai-chat-backend/spec.md)
- All requirements traced to spec functional requirements (FR-001 through FR-040)
- No behavior outside specification

### Principle II: Agentic Workflow Integrity ✅ PASS
- Plan generated via `/sp.plan` command (agentic workflow)
- Implementation will use `fastapi-backend` agent for backend code
- No manual coding permitted

### Principle III: Correctness & Consistency ✅ PASS
- API contracts explicitly defined (POST /api/chat)
- Data models consistent (Conversation, Message align with existing User, Task models)
- Error handling consistent with existing backend patterns

### Principle IV: Security by Design ✅ PASS
- JWT authentication required (FR-002, FR-003)
- User ID extracted only from JWT (FR-003)
- Cross-user conversation access prevented (FR-031, FR-032)
- Input validation for malicious content (FR-033)

### Principle V: Separation of Concerns ✅ PASS
- Frontend communicates only via REST API (POST /api/chat)
- Backend delegates task mutations to MCP tools (FR-021)
- Database access via SQLModel ORM
- Agent logic separated from business logic

### Principle VI: Stateless Architecture ✅ PASS
- No in-memory session state (FR-012)
- Conversation context reconstructed from database per request (FR-007)
- MCP tools are stateless (delegated to separate spec 006)

### Principle VII: Agent Behavior Constraints ✅ PASS
- Agent decides actions but delegates execution to MCP tools (FR-016, FR-017)
- Agent confirms destructive actions (FR-018)
- Agent handles errors gracefully (FR-019)

### Principle VIII: MCP Tool Design ✅ PASS
- Tools invoked with user_id from JWT (FR-021)
- Tool invocations logged for auditability (FR-023)
- Tool failures handled gracefully (FR-024)

### Principle IX: Frontend-Backend Integration ✅ PASS
- Frontend will communicate only with FastAPI (separate Chat Frontend spec)
- JWT attached to every request (FR-002)
- Frontend does not call MCP directly

### Principle X: Backward Compatibility ✅ PASS
- Phase I & II APIs remain unchanged (additive only)
- New tables (Conversation, Message) do not modify existing schema
- Existing REST endpoints unaffected

### Principle XI: Multi-Spec Architecture ✅ PASS
- This is one of three Phase III specs (AI Chat Backend, MCP Tool Server, Chat Frontend)
- Dependencies explicitly declared (001, 002, 006)
- Clear boundaries: This spec handles chat endpoint and agent orchestration only

**GATE RESULT**: ✅ ALL PRINCIPLES PASS - Proceed to Phase 0 Research

## Project Structure

### Documentation (this feature)

```text
specs/005-ai-chat-backend/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   └── chat-api.yaml    # OpenAPI spec for POST /api/chat
├── checklists/
│   └── requirements.md  # Spec quality validation (already created)
└── spec.md              # Feature specification (already created)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── models/
│   │   ├── conversation.py      # NEW: Conversation model
│   │   ├── message.py           # NEW: Message model
│   │   ├── user.py              # EXISTING: User model
│   │   └── task.py              # EXISTING: Task model
│   ├── routes/
│   │   ├── chat.py              # NEW: POST /api/chat endpoint
│   │   ├── auth.py              # EXISTING: Authentication routes
│   │   └── tasks.py             # EXISTING: Task CRUD routes
│   ├── services/
│   │   ├── agent_service.py     # NEW: OpenAI Agent orchestration
│   │   ├── conversation_service.py  # NEW: Conversation CRUD
│   │   ├── mcp_client.py        # NEW: MCP tool invocation client
│   │   └── auth_service.py      # EXISTING: JWT verification
│   ├── schemas/
│   │   ├── chat.py              # NEW: ChatRequest, ChatResponse schemas
│   │   ├── conversation.py      # NEW: Conversation schemas
│   │   └── message.py           # NEW: Message schemas
│   ├── middleware/
│   │   └── auth.py              # EXISTING: JWT middleware
│   ├── database/
│   │   └── connection.py        # EXISTING: Database connection
│   ├── config.py                # EXISTING: Configuration (add OpenAI API key)
│   └── main.py                  # EXISTING: FastAPI app (register chat routes)
├── alembic/
│   └── versions/
│       └── xxx_add_conversation_message_tables.py  # NEW: Migration
└── tests/
    ├── test_chat_endpoint.py    # NEW: Chat endpoint tests
    ├── test_agent_service.py    # NEW: Agent orchestration tests
    ├── test_conversation_service.py  # NEW: Conversation CRUD tests
    └── test_mcp_client.py       # NEW: MCP client tests
```

**Structure Decision**: Web application (backend extension). This feature extends the existing FastAPI backend with new models (Conversation, Message), new routes (chat.py), and new services (agent_service.py, conversation_service.py, mcp_client.py). The structure follows the existing backend architecture pattern established in Phase I & II.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**No violations detected.** All constitutional principles pass. No complexity justification required.

## Phase 0: Research & Discovery

**Status**: ✅ COMPLETE (see research.md)

**Research Tasks Completed**:
1. OpenAI Agents SDK integration patterns with FastAPI
2. MCP SDK usage for tool invocation
3. Stateless conversation management strategies
4. Agent context reconstruction from database
5. Error handling patterns for agent failures
6. Token limit management for conversation history

**Key Decisions Documented in research.md**:
- OpenAI Agents SDK version and configuration
- MCP SDK integration approach
- Conversation history truncation strategy
- Agent prompt engineering guidelines
- Tool invocation error handling patterns

## Phase 1: Design & Contracts

**Status**: ✅ COMPLETE (see data-model.md, contracts/, quickstart.md)

**Artifacts Generated**:
1. **data-model.md**: Conversation and Message models with relationships
2. **contracts/chat-api.yaml**: OpenAPI specification for POST /api/chat
3. **quickstart.md**: Setup guide for OpenAI API key and MCP tool server

**Key Design Decisions**:
- Conversation model: id, user_id, created_at, updated_at
- Message model: id, conversation_id, user_id, role, content, created_at
- Chat endpoint: POST /api/chat with JWT authentication
- Agent context: Load last 50 messages (or token limit)
- Tool invocation: Synchronous calls to MCP tool server

## Next Steps

1. **Run `/sp.tasks`**: Generate testable tasks from this plan
2. **Implement via agents**: Use `fastapi-backend` agent for implementation
3. **Create MCP Tool Server spec**: Define spec 006-mcp-tool-server
4. **Integration testing**: Validate stateless conversation resume
5. **Backward compatibility testing**: Ensure Phase I & II APIs unchanged
