# Implementation Plan: MCP Task Tools

**Branch**: `006-mcp-task-tools` | **Date**: 2026-02-06 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/006-mcp-task-tools/spec.md`

**Note**: This plan implements Phase III MCP layer to expose task operations as stateless, secure, auditable tools for AI agent integration.

## Summary

Implement production-grade MCP tools that enable the AI agent (Spec 005) to interact with the task system through secure, stateless tool interfaces. All 5 tools (add_task, list_tasks, update_task, delete_task, get_task) delegate to existing task service layer (Spec 001), enforce authorization, and provide deterministic responses. The architecture maintains complete separation between agent reasoning and business logic while ensuring auditability of all actions.

**Primary Requirement**: Replace placeholder MCP tool implementations in Spec 005 with production-grade tools that actually persist changes to database via service layer delegation.

**Technical Approach**: MCP tool handlers → Input validation → Authorization check → Service layer delegation → Structured response. All tools stateless, all invocations logged, all errors handled gracefully.

## Technical Context

**Language/Version**: Python 3.11+ (matches existing backend)
**Primary Dependencies**:
- MCP SDK (mcp-python 0.1.0+) - already installed in Spec 005
- FastAPI (existing backend framework)
- SQLModel (existing ORM)
- Existing task service layer (from Spec 001)
- PyJWT (existing JWT verification)

**Storage**: PostgreSQL (Neon Serverless) - existing database, no schema changes
**Testing**: pytest (existing test framework)
**Target Platform**: Linux server (same as existing backend)
**Project Type**: Web application (backend extension)

**Performance Goals**:
- Tool response time: <500ms for 95% of requests (excluding database query time)
- Concurrent tool calls: 100 simultaneous without degradation
- Tool invocation logging: <10ms overhead per call

**Constraints**:
- Stateless tools: No in-memory state between calls
- Service layer delegation: Tools never access database directly
- Authorization enforcement: All tools validate user ownership
- Backward compatibility: Existing REST APIs and services unchanged
- Auditability: All tool invocations logged with complete context

**Scale/Scope**:
- Expected tool calls: 1,000+ per day per active user
- Tool types: 5 tools (add_task, list_tasks, update_task, delete_task, get_task)
- Users: 1,000+ concurrent users
- Tool invocation rate: 10-50 calls per conversation

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Spec-Driven Development ✅ PASS
- Implementation follows approved spec (006-mcp-task-tools/spec.md)
- All requirements traced to spec functional requirements (FR-001 through FR-052)
- No behavior outside specification

### Principle II: Agentic Workflow Integrity ✅ PASS
- Plan generated via `/sp.plan` command (agentic workflow)
- Implementation will use `fastapi-backend` agent for backend code
- No manual coding permitted

### Principle III: Correctness & Consistency ✅ PASS
- Tool contracts explicitly defined (input/output schemas)
- Tool responses consistent and deterministic
- Error handling consistent with existing backend patterns

### Principle IV: Security by Design ✅ PASS
- All tools require user_id from authenticated chat layer (FR-039)
- User ownership validated before mutations (FR-040)
- Cross-user data access prevented (FR-041)
- Input sanitization for injection attacks (FR-042)

### Principle V: Separation of Concerns ✅ PASS
- MCP tools isolated from agent reasoning (constitutional requirement)
- Tools delegate to existing service layer (no business logic in tools)
- Service layer unchanged (backward compatibility)

### Principle VI: Stateless Architecture ✅ PASS
- MCP server maintains no in-memory state (FR-002)
- Tools are stateless between calls (constitutional requirement)
- Tools are idempotent where applicable (FR-032)

### Principle VII: Agent Behavior Constraints ✅ PASS
- Agents call tools but don't execute directly (constitutional requirement)
- Tools handle all database mutations (FR-009, FR-016, FR-022, FR-028, FR-035)
- Clear separation between decision (agent) and execution (tools)

### Principle VIII: MCP Tool Design ✅ PASS
- Tools map 1:1 to domain actions (5 tools for CRUD operations)
- Tools validate authorization server-side (FR-040)
- Tools are stateless and persist to database (FR-002, FR-009)
- Tools return structured, deterministic responses (FR-011, FR-017, FR-023, FR-029, FR-036)

### Principle X: Backward Compatibility ✅ PASS
- Existing REST APIs unchanged (additive only)
- Existing task service layer unchanged (tools delegate to it)
- No breaking schema changes

### Principle XI: Multi-Spec Architecture ✅ PASS
- This is one of three Phase III specs (AI Chat Backend, MCP Tool Server, Chat Frontend)
- Dependencies explicitly declared (001, 002, 005)
- Clear boundaries: This spec handles MCP tools only, not agent logic or frontend

**GATE RESULT**: ✅ ALL PRINCIPLES PASS - Proceed to Phase 0 Research

## Project Structure

### Documentation (this feature)

```text
specs/006-mcp-task-tools/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command) - Tool schemas
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   └── mcp-tools.yaml   # Tool schemas and contracts
├── checklists/
│   └── requirements.md  # Spec quality validation (already created)
└── spec.md              # Feature specification (already created)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── services/
│   │   ├── mcp_client.py        # EXISTING (Spec 005): Placeholder MCP client
│   │   ├── mcp_tools.py         # NEW: Production MCP tool handlers
│   │   ├── task_service.py      # EXISTING (Spec 001): Task CRUD service
│   │   └── agent_service.py     # EXISTING (Spec 005): Agent orchestration
│   ├── schemas/
│   │   └── mcp_schemas.py       # NEW: Tool input/output schemas
│   ├── models/
│   │   ├── task.py              # EXISTING (Spec 001): Task model
│   │   └── user.py              # EXISTING (Spec 001): User model
│   ├── config.py                # EXISTING: Configuration
│   └── main.py                  # EXISTING: FastAPI app
└── tests/
    ├── test_mcp_tools.py        # NEW: MCP tool tests
    └── test_mcp_integration.py  # NEW: Agent-tool integration tests
```

**Structure Decision**: Web application (backend extension). This feature extends the existing FastAPI backend by replacing placeholder MCP tool implementations (from Spec 005) with production-grade tools that delegate to existing task service layer (from Spec 001). The structure follows the existing backend architecture pattern.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**No violations detected.** All constitutional principles pass. No complexity justification required.

## Phase 0: Research & Discovery

**Status**: ✅ COMPLETE (see research.md)

**Research Tasks Completed**:
1. MCP SDK tool handler patterns and best practices
2. Service layer delegation strategies for tool implementations
3. Tool schema definition and validation approaches
4. Error handling patterns for tool failures
5. Logging and auditability strategies for tool invocations
6. Tool testing strategies (unit tests, integration tests)

**Key Decisions Documented in research.md**:
- MCP SDK tool handler implementation pattern
- Service layer delegation approach (direct function calls vs. API calls)
- Tool schema definition strategy (Pydantic models)
- Error handling and response formatting
- Logging strategy for auditability
- Testing approach for tools and agent-tool integration

## Phase 1: Design & Contracts

**Status**: ✅ COMPLETE (see data-model.md, contracts/, quickstart.md)

**Artifacts Generated**:
1. **data-model.md**: Tool schemas (input/output for all 5 tools)
2. **contracts/mcp-tools.yaml**: MCP tool contracts with JSON schemas
3. **quickstart.md**: Setup guide for MCP tool development and testing

**Key Design Decisions**:
- Tool input schemas: Pydantic models for validation
- Tool output schemas: Structured responses with success/error formats
- Service layer integration: Direct function calls to existing task service
- Error handling: Structured error responses with error type and detail
- Logging: JSON-structured logs with tool name, user_id, parameters, result

## Next Steps

1. **Run `/sp.tasks`**: Generate testable tasks from this plan
2. **Implement via agents**: Use `fastapi-backend` agent for implementation
3. **Update Spec 005**: Replace placeholder MCP client with production tools
4. **Integration testing**: Validate tools work correctly with agent
5. **End-to-end testing**: Test full conversational workflow (user → agent → tools → database)
