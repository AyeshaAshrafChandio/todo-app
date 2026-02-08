# Feature Specification: MCP Task Tools

**Feature Branch**: `006-mcp-task-tools`
**Created**: 2026-02-06
**Status**: Draft
**Input**: User description: "MCP Task Tools - Expose task operations as stateless MCP tools for AI agent integration"

**Phase**: III – AI Todo Chatbot (MCP Layer)
**Dependencies**:
- 001-backend-core-data (Task, User models, service layer)
- 002-authentication-and-api-security (JWT authentication)
- 005-ai-chat-backend (Agent orchestration, conversation management)

**Mode**: Additive only (no changes to existing REST APIs, auth logic, or task service behavior)

## Constitutional Alignment

This specification adheres to the following constitutional principles:

- **Principle VII (Agent Behavior Constraints)**: Agents decide actions but delegate execution to MCP tools
- **Principle VIII (MCP Tool Design)**: Tools validate authorization server-side, are stateless, and persist changes to database
- **Principle V (Separation of Concerns)**: MCP tools isolated from agent reasoning and business logic
- **Principle VI (Stateless Architecture)**: MCP server maintains no in-memory state between tool calls
- **Principle X (Backward Compatibility)**: Existing REST APIs and task services remain unchanged

## Problem Statement

The AI agent introduced in Phase III (Spec 005) must interact with the todo system in a secure, auditable, and deterministic way. Direct database access by the agent is forbidden.

**Current State**: AI agent has placeholder MCP tool implementations that simulate task operations but don't actually persist changes to the database.

**Desired State**: All task operations exposed as production-grade MCP tools that delegate to existing service layer, enforce permissions, and provide deterministic, auditable responses.

**Why This Matters**:
- Separates AI reasoning from business logic (constitutional requirement)
- Maintains security guarantees through service layer delegation
- Enables auditability of all agent actions
- Ensures deterministic tool behavior for testing and debugging
- Preserves backward compatibility with existing REST APIs

## Target Audience

- **Backend Engineers**: Implementing MCP server and tool handlers
- **AI Engineers**: Wiring OpenAI Agents SDK to MCP tools
- **System Architects**: Validating tool isolation and security patterns
- **Judges/Reviewers**: Assessing MCP correctness and constitutional compliance

## User Scenarios & Testing

### User Story 1 - Task Creation via MCP Tool (Priority: P1) 🎯 MVP

An AI agent needs to create a task on behalf of an authenticated user through a secure, auditable tool interface.

**Why this priority**: Core functionality that enables the AI chatbot to actually create tasks. Without this, the chatbot can only simulate task creation. This is the minimum viable tool to demonstrate agent-tool separation.

**Independent Test**: Agent calls `add_task` tool with user_id, title, and description. Tool validates inputs, delegates to existing task service, persists task to database, and returns structured response with task_id. Task appears in existing REST API responses and database.

**Acceptance Scenarios**:

1. **Given** authenticated user with user_id "123", **When** agent calls add_task(user_id="123", title="Buy groceries", description="Milk, eggs, bread"), **Then** tool creates task owned by user 123, returns {task_id: 1, status: "created", title: "Buy groceries"}
2. **Given** agent calls add_task with missing title, **When** tool validates input, **Then** tool returns validation error without creating task
3. **Given** agent calls add_task with user_id "456", **When** tool delegates to task service, **Then** task is created with completed=false by default
4. **Given** agent calls add_task with empty description, **When** tool processes request, **Then** tool creates task with empty description (description is optional)

---

### User Story 2 - Task Listing via MCP Tool (Priority: P2)

An AI agent needs to retrieve a user's tasks through a secure tool interface to answer queries like "Show me my tasks" or "What do I need to do today?"

**Why this priority**: Essential for conversational task management. Users need to see their tasks before updating or deleting them. Demonstrates read-only tool operations.

**Independent Test**: Agent calls `list_tasks` tool with user_id and optional status filter. Tool queries existing task service, filters by authenticated user, and returns structured list of tasks.

**Acceptance Scenarios**:

1. **Given** user "123" has 3 tasks (2 pending, 1 completed), **When** agent calls list_tasks(user_id="123", status="all"), **Then** tool returns all 3 tasks with id, title, description, completed status
2. **Given** user "123" has 3 tasks, **When** agent calls list_tasks(user_id="123", status="pending"), **Then** tool returns only 2 pending tasks
3. **Given** user "123" has no tasks, **When** agent calls list_tasks(user_id="123"), **Then** tool returns empty array []
4. **Given** agent calls list_tasks without status parameter, **When** tool processes request, **Then** tool defaults to status="all" and returns all tasks

---

### User Story 3 - Task Update via MCP Tool (Priority: P3)

An AI agent needs to update task details (title, description, completion status) through a secure tool interface to handle commands like "Mark buy groceries as done" or "Change task title to X".

**Why this priority**: Completes the CRUD workflow. Enables users to manage task lifecycle through natural language. Demonstrates tool handling of state mutations.

**Independent Test**: Agent calls `update_task` tool with user_id, task_id, and updates object. Tool validates ownership, delegates to task service, persists changes, and returns updated task details.

**Acceptance Scenarios**:

1. **Given** user "123" owns task 1, **When** agent calls update_task(user_id="123", task_id=1, updates={completed: true}), **Then** tool marks task as completed and returns updated task
2. **Given** user "123" owns task 1, **When** agent calls update_task(user_id="123", task_id=1, updates={title: "Buy milk"}), **Then** tool updates title and returns updated task
3. **Given** user "123" tries to update task 2 owned by user "456", **When** tool validates ownership, **Then** tool returns authorization error without updating task
4. **Given** agent calls update_task with invalid task_id, **When** tool queries database, **Then** tool returns not found error

---

### User Story 4 - Task Deletion via MCP Tool (Priority: P4)

An AI agent needs to delete tasks through a secure tool interface to handle commands like "Delete buy groceries" or "Remove completed tasks".

**Why this priority**: Completes full CRUD operations. Less critical than creation/viewing/updating but necessary for complete task management. Demonstrates tool handling of destructive operations.

**Independent Test**: Agent calls `delete_task` tool with user_id and task_id. Tool validates ownership, delegates to task service, removes task from database, and returns confirmation.

**Acceptance Scenarios**:

1. **Given** user "123" owns task 1, **When** agent calls delete_task(user_id="123", task_id=1), **Then** tool deletes task and returns {status: "deleted", task_id: 1}
2. **Given** user "123" tries to delete task 2 owned by user "456", **When** tool validates ownership, **Then** tool returns authorization error without deleting task
3. **Given** agent calls delete_task with non-existent task_id, **When** tool queries database, **Then** tool returns not found error
4. **Given** task 1 is deleted, **When** agent calls delete_task again for task 1, **Then** tool returns not found error (idempotent)

---

### User Story 5 - Task Retrieval via MCP Tool (Priority: P2)

An AI agent needs to retrieve a single task's details through a secure tool interface to answer specific queries or validate task references before updates/deletions.

**Why this priority**: Supports agent decision-making by providing detailed task information. Enables agent to confirm task identity before destructive operations. Demonstrates single-entity retrieval pattern.

**Independent Test**: Agent calls `get_task` tool with user_id and task_id. Tool validates ownership, queries task service, and returns complete task details.

**Acceptance Scenarios**:

1. **Given** user "123" owns task 1, **When** agent calls get_task(user_id="123", task_id=1), **Then** tool returns complete task details {id, title, description, completed, created_at, updated_at}
2. **Given** user "123" tries to get task 2 owned by user "456", **When** tool validates ownership, **Then** tool returns authorization error
3. **Given** agent calls get_task with non-existent task_id, **When** tool queries database, **Then** tool returns not found error
4. **Given** agent calls get_task for deleted task, **When** tool queries database, **Then** tool returns not found error

---

### Edge Cases

- **What happens when tool receives invalid user_id format?** Tool validates user_id format (UUID), returns validation error with clear message, does not attempt database query
- **What happens when tool receives malformed JSON input?** MCP SDK validates JSON schema before tool execution, returns schema validation error
- **What happens when database connection fails during tool execution?** Tool catches database error, logs error details, returns generic error message to agent without exposing internals
- **What happens when task service throws unexpected exception?** Tool catches exception, logs full stack trace, returns generic error message to agent
- **What happens when agent calls tool with user_id that doesn't exist?** Tool queries database, finds no user, returns authorization error (treat as unauthorized)
- **What happens when multiple agents call tools concurrently for same user?** Database handles concurrent writes with proper isolation, each tool call is independent transaction
- **What happens when tool response exceeds reasonable size (e.g., 10,000 tasks)?** Tool implements pagination or limits response size, returns error if limit exceeded
- **What happens when agent provides extra unexpected parameters?** MCP SDK validates against tool schema, ignores extra parameters or returns validation error

## Requirements

### Functional Requirements

#### MCP Server Setup

- **FR-001**: System MUST implement MCP server using official MCP SDK (mcp-python)
- **FR-002**: MCP server MUST be stateless (no in-memory session state between tool calls)
- **FR-003**: MCP server MUST register all 5 task tools (add_task, list_tasks, update_task, delete_task, get_task)
- **FR-004**: MCP server MUST validate all tool inputs against defined schemas before execution
- **FR-005**: MCP server MUST run as separate process or module from chat backend

#### Tool: add_task

- **FR-006**: Tool MUST accept user_id (string, required), title (string, required), description (string, optional)
- **FR-007**: Tool MUST validate user_id format (UUID) before processing
- **FR-008**: Tool MUST validate title is non-empty and <= 200 characters
- **FR-009**: Tool MUST delegate task creation to existing task service layer
- **FR-010**: Tool MUST set completed=false by default for new tasks
- **FR-011**: Tool MUST return structured response: {task_id: integer, status: "created", title: string}
- **FR-012**: Tool MUST return validation error if required parameters missing or invalid

#### Tool: list_tasks

- **FR-013**: Tool MUST accept user_id (string, required), status (string, optional: "all" | "pending" | "completed")
- **FR-014**: Tool MUST default status to "all" if not provided
- **FR-015**: Tool MUST filter tasks strictly by authenticated user_id
- **FR-016**: Tool MUST delegate task querying to existing task service layer
- **FR-017**: Tool MUST return array of tasks: [{id, title, description, completed, created_at, updated_at}]
- **FR-018**: Tool MUST return empty array [] if user has no tasks

#### Tool: update_task

- **FR-019**: Tool MUST accept user_id (string, required), task_id (integer, required), updates (object, required)
- **FR-020**: Tool MUST validate user owns task before allowing update
- **FR-021**: Tool MUST support updating title, description, and completed fields
- **FR-022**: Tool MUST delegate task update to existing task service layer
- **FR-023**: Tool MUST return updated task details after successful update
- **FR-024**: Tool MUST return authorization error if user doesn't own task
- **FR-025**: Tool MUST return not found error if task doesn't exist

#### Tool: delete_task

- **FR-026**: Tool MUST accept user_id (string, required), task_id (integer, required)
- **FR-027**: Tool MUST validate user owns task before allowing deletion
- **FR-028**: Tool MUST delegate task deletion to existing task service layer
- **FR-029**: Tool MUST return confirmation: {status: "deleted", task_id: integer}
- **FR-030**: Tool MUST return authorization error if user doesn't own task
- **FR-031**: Tool MUST return not found error if task doesn't exist
- **FR-032**: Tool MUST be idempotent (deleting already-deleted task returns not found, not error)

#### Tool: get_task

- **FR-033**: Tool MUST accept user_id (string, required), task_id (integer, required)
- **FR-034**: Tool MUST validate user owns task before returning details
- **FR-035**: Tool MUST delegate task retrieval to existing task service layer
- **FR-036**: Tool MUST return complete task details: {id, title, description, completed, created_at, updated_at}
- **FR-037**: Tool MUST return authorization error if user doesn't own task
- **FR-038**: Tool MUST return not found error if task doesn't exist

#### Security & Authorization

- **FR-039**: All tools MUST receive user_id from authenticated chat layer (never from agent reasoning)
- **FR-040**: All tools MUST validate user_id matches task owner before mutations
- **FR-041**: All tools MUST prevent cross-user data access at tool level
- **FR-042**: All tools MUST sanitize inputs to prevent injection attacks
- **FR-043**: All tools MUST NOT expose internal error details or stack traces to agent

#### Auditability & Logging

- **FR-044**: All tool invocations MUST be logged with: tool name, user_id, parameters, timestamp
- **FR-045**: All tool responses MUST be logged with: status, result summary, execution time
- **FR-046**: All tool errors MUST be logged with: error type, error message, stack trace (server-side only)
- **FR-047**: Tool logs MUST be structured (JSON) for easy parsing and analysis

#### Error Handling

- **FR-048**: Tools MUST return structured error responses: {error: string, detail: string}
- **FR-049**: Tools MUST distinguish between validation errors, authorization errors, not found errors, and server errors
- **FR-050**: Tools MUST handle database connection failures gracefully
- **FR-051**: Tools MUST handle service layer exceptions gracefully
- **FR-052**: Tools MUST provide user-friendly error messages suitable for agent to relay to user

### Key Entities

#### MCP Tool (Conceptual)
- **What it represents**: A callable function exposed to the AI agent for task operations
- **Key attributes**: Name, input schema, output schema, handler function
- **Relationships**: Invoked by Agent (Spec 005), delegates to Task Service (Spec 001)
- **Lifecycle**: Registered at MCP server startup, invoked per agent request, stateless between calls

#### Tool Request (Conceptual)
- **What it represents**: A structured call from agent to MCP tool
- **Key attributes**: Tool name, user_id, tool-specific parameters
- **Validation**: Schema-validated by MCP SDK before handler execution
- **Security**: user_id provided by chat layer from JWT, never from agent reasoning

#### Tool Response (Conceptual)
- **What it represents**: Structured result returned from MCP tool to agent
- **Key attributes**: Success data or error details, deterministic format
- **Purpose**: Enables agent to understand operation result and generate natural language response

## Success Criteria

### Measurable Outcomes

- **SC-001**: All 5 MCP tools (add_task, list_tasks, update_task, delete_task, get_task) successfully create, read, update, and delete tasks in database
- **SC-002**: 100% of tool invocations are logged with complete audit trail (tool name, user_id, parameters, timestamp, result)
- **SC-003**: Zero unauthorized cross-user data access attempts succeed (100% authorization enforcement)
- **SC-004**: Tool response time is under 500ms for 95% of requests (excluding database query time)
- **SC-005**: Agent can successfully complete full CRUD workflow via tools: create task → list tasks → update task → delete task
- **SC-006**: All tool errors return structured, user-friendly messages suitable for agent to relay to user
- **SC-007**: MCP server remains stateless (survives restart without losing functionality, no in-memory state)
- **SC-008**: All existing REST APIs remain functional and unchanged (100% backward compatibility)
- **SC-009**: Tool input validation catches 100% of malformed requests before database queries
- **SC-010**: Agent integration tests pass with 100% success rate (tools work correctly with OpenAI Agents SDK)

## Dependencies

### Required Specs (Must be implemented first)

- **001-backend-core-data**: Provides Task model, task service layer, database connection
- **002-authentication-and-api-security**: Provides JWT authentication, user_id extraction
- **005-ai-chat-backend**: Provides agent orchestration, conversation management, calls MCP tools

### External Dependencies

- **MCP SDK (mcp-python)**: Official MCP implementation for Python (already installed in Spec 005)
- **Existing Task Service**: Task CRUD operations in backend/app/services/ (from Spec 001)
- **Database**: PostgreSQL via Neon Serverless (from Spec 001)

## Assumptions

1. **MCP SDK Compatibility**: Assumes mcp-python 0.1.0+ is compatible with OpenAI Agents SDK integration patterns
2. **Service Layer Stability**: Assumes existing task service layer (Spec 001) is stable and provides all necessary CRUD operations
3. **User ID Format**: Assumes user_id is UUID format (consistent with Spec 001 and 002)
4. **Tool Invocation Pattern**: Assumes agent calls tools synchronously (no streaming or async chaining in MVP)
5. **Error Handling**: Assumes generic error messages are acceptable for MVP (detailed error codes can be added later)
6. **Performance**: Assumes 500ms tool response time is acceptable for conversational interface
7. **Concurrency**: Assumes database handles concurrent tool calls with proper isolation (no additional locking needed)
8. **Tool Registration**: Assumes MCP server registers tools at startup (no dynamic tool registration needed)
9. **Pagination**: Assumes users have reasonable number of tasks (<1000) for MVP (pagination can be added later if needed)
10. **Tool Versioning**: Assumes tool schemas are stable for MVP (versioning strategy out of scope)

## Out of Scope

The following are explicitly OUT OF SCOPE for this specification:

### AI Agent Logic
- Agent reasoning and decision-making (covered in Spec 005)
- Conversation persistence and context management (covered in Spec 005)
- Natural language understanding and response generation (covered in Spec 005)

### Frontend Implementation
- Chat UI components (covered in separate Chat Frontend spec)
- User interface for tool invocation monitoring
- Tool call visualization or debugging UI

### Advanced Features
- Streaming tool responses (real-time updates)
- Async tool chaining (tool A calls tool B)
- Tool composition or workflows
- Custom tool creation by users
- Tool versioning or deprecation strategy
- Tool rate limiting per user
- Tool usage analytics dashboard
- Tool performance monitoring UI

### Integration Features
- Webhook notifications for tool calls
- Third-party tool integrations
- Tool marketplace or discovery
- Tool sharing between users

### Business Logic Extensions
- New task fields or attributes (covered in Spec 001 if needed)
- Task relationships or dependencies
- Task templates or recurring tasks
- Task categories or tags

## Risks & Mitigations

### Risk 1: MCP SDK Compatibility Issues
**Impact**: Tools may not integrate correctly with OpenAI Agents SDK, breaking agent functionality
**Mitigation**: Test MCP SDK integration early with simple tool, validate tool registration and invocation patterns, have fallback to direct function calls if MCP SDK fails

### Risk 2: Service Layer Changes
**Impact**: If task service layer changes, tools may break or behave unexpectedly
**Mitigation**: Use stable service layer interfaces, add integration tests that validate tool-service interaction, document service layer dependencies clearly

### Risk 3: Authorization Bypass
**Impact**: Agent could potentially access or modify tasks belonging to other users
**Mitigation**: Enforce user_id validation at tool level, never trust agent-provided user_id, add authorization tests for all tools, log all authorization failures

### Risk 4: Tool Performance Degradation
**Impact**: Slow tool responses degrade conversational experience, users perceive chatbot as unresponsive
**Mitigation**: Optimize database queries, add caching if needed, implement timeout limits, monitor tool response times, add performance tests

### Risk 5: Error Handling Gaps
**Impact**: Unhandled exceptions crash MCP server or expose internal details to agent
**Mitigation**: Wrap all tool handlers in try-catch, return structured errors, log all exceptions server-side, test error scenarios thoroughly

## Next Steps

1. **Spec Approval**: Review and approve this specification
2. **Run /sp.plan**: Generate implementation plan with technical design
3. **Run /sp.tasks**: Break down into testable tasks
4. **Implementation**: Execute tasks via Claude Code agents (fastapi-backend agent)
5. **Integration Testing**: Validate tools work correctly with agent from Spec 005
6. **Update Spec 005**: Replace placeholder MCP client with real tool implementations
7. **End-to-End Testing**: Test full conversational workflow (user message → agent → tools → database → response)
