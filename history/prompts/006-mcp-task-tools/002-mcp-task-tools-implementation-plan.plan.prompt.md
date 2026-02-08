---
id: 002
title: MCP Task Tools Implementation Plan
stage: plan
date: 2026-02-06
surface: agent
model: claude-sonnet-4-5
feature: 006-mcp-task-tools
branch: 006-mcp-task-tools
user: Ali Haider
command: /sp.plan
labels: ["plan", "phase-iii", "mcp-tools", "task-operations", "agent-tool-separation"]
links:
  spec: specs/006-mcp-task-tools/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/006-mcp-task-tools/plan.md
  - specs/006-mcp-task-tools/research.md
  - specs/006-mcp-task-tools/data-model.md
  - specs/006-mcp-task-tools/contracts/mcp-tools.yaml
  - specs/006-mcp-task-tools/quickstart.md
tests:
  - N/A (planning artifact)
---

## Prompt

/sp.plan

## Response snapshot

Generated comprehensive implementation plan for MCP Task Tools (006-mcp-task-tools) following Phase III constitutional principles:

**Phase 0: Research & Discovery** (research.md):
- MCP SDK tool handler implementation (decorator pattern with async handlers)
- Service layer delegation strategy (direct function calls to existing TaskService)
- Tool schema definition and validation (Pydantic models)
- Error handling patterns (structured error responses with error type and detail)
- Logging and auditability strategy (JSON-structured logs)
- Tool testing strategy (unit tests + integration tests)

**Key Technology Decisions**:
- MCP SDK: mcp-python 0.1.0+ with @Tool decorator pattern
- Service Layer: Direct function calls to existing TaskService (Spec 001)
- Schemas: Pydantic models for input/output validation
- Error Handling: Structured responses (ValidationError, AuthorizationError, NotFoundError, ServerError)
- Logging: JSON-structured logs with tool name, user_id, parameters, result, execution time

**Phase 1: Design & Contracts** (data-model.md, contracts/mcp-tools.yaml, quickstart.md):

1. **Tool Schemas** (data-model.md):
   - AddTaskInput/Output: Create tasks with validation
   - ListTasksInput/Output: Retrieve tasks with status filtering
   - UpdateTaskInput/Output: Modify task details with ownership validation
   - DeleteTaskInput/Output: Remove tasks with authorization
   - GetTaskInput/Output: Fetch single task details
   - ToolError: Standardized error response

2. **Tool Contracts** (contracts/mcp-tools.yaml):
   - OpenAPI 3.0.3 specification for all 5 MCP tools
   - Complete input/output schemas with examples
   - Error response definitions
   - Tool descriptions with authorization and delegation notes

3. **Development Guide** (quickstart.md):
   - Architecture overview (Agent → Tools → Service → Database)
   - Existing code review (TaskService from Spec 001)
   - Tool implementation pattern (validate → delegate → log → return)
   - Testing strategies (unit tests, integration tests, end-to-end)
   - Troubleshooting common issues

**Constitution Check**: All 11 principles pass
- Principle VII (Agent Behavior Constraints): Agents decide, tools execute
- Principle VIII (MCP Tool Design): Tools validate authorization, are stateless, persist to database
- Principle V (Separation of Concerns): MCP tools isolated from agent reasoning
- Principle VI (Stateless Architecture): No in-memory state between tool calls
- Principle X (Backward Compatibility): Existing REST APIs and services unchanged

**Project Structure**:
- Backend extension: New mcp_tools.py (tool handlers), mcp_schemas.py (schemas)
- Update existing: mcp_client.py (replace placeholder with production tools)
- Tests: test_mcp_tools.py (unit tests), test_mcp_integration.py (integration tests)

**Performance Goals**:
- Tool response time: <500ms for 95% of requests
- Concurrent tool calls: 100 simultaneous without degradation
- Tool invocation logging: <10ms overhead per call

**Security Requirements**:
- All tools receive user_id from authenticated chat layer (JWT token)
- User ownership validated before mutations
- Cross-user data access prevented at tool level
- Input sanitization for injection attacks
- Structured error responses (no internal details exposed)

## Outcome

- ✅ Impact: Created production-ready implementation plan for MCP Task Tools enabling AI agent to interact with task system through secure, stateless, auditable tools
- 🧪 Tests: N/A (planning artifact) - Test strategy defined for implementation phase
- 📁 Files: Created plan.md (technical plan), research.md (Phase 0 research), data-model.md (tool schemas), contracts/mcp-tools.yaml (OpenAPI spec), quickstart.md (development guide)
- 🔁 Next prompts: Ready for `/sp.tasks` to generate testable tasks, then use `fastapi-backend` agent for implementation
- 🧠 Reflection: Plan successfully bridges AI agent (Spec 005) with task service layer (Spec 001) through production-grade MCP tools. All Phase 0 research decisions documented with rationale and alternatives considered. Tool schemas provide complete validation and type safety. OpenAPI contract enables clear documentation and testing. Quickstart guide enables rapid development. Constitutional principles VII and VIII fully satisfied with stateless, delegating tool architecture.

## Evaluation notes (flywheel)

- Failure modes observed: None - plan generation successful, all constitutional principles pass, all Phase 0 and Phase 1 artifacts complete
- Graders run and results (PASS/FAIL): PASS - Constitution check passes all 11 principles, tool schemas complete with validation, OpenAPI contract follows standards, performance goals measurable, security requirements explicit
- Prompt variant (if applicable): N/A - Standard planning workflow with Phase III constitutional principles
- Next experiment (smallest change to try): Proceed with `/sp.tasks` to validate plan completeness through task breakdown, particularly tool handler implementation, service layer integration, and error handling patterns
