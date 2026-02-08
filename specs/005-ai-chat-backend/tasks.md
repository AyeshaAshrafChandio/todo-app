# Tasks: AI Chat Backend

**Input**: Design documents from `/specs/005-ai-chat-backend/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/chat-api.yaml

**Tests**: Tests are NOT requested in the specification, so test tasks are omitted.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Web app structure: `backend/app/` for source code
- Tests: `backend/tests/`
- Migrations: `backend/alembic/versions/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Environment configuration and dependency installation

- [ ] T001 Add OpenAI API key configuration to backend/.env file (OPENAI_API_KEY, OPENAI_MODEL, OPENAI_MAX_TOKENS)
- [ ] T002 [P] Update backend/requirements.txt with openai==1.6.1 and mcp-python==0.1.0 dependencies
- [ ] T003 [P] Update backend/app/config.py to load OpenAI API key and model settings from environment
- [ ] T004 Install new dependencies with pip install -r backend/requirements.txt

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core data models and database schema that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T005 [P] Create Conversation model in backend/app/models/conversation.py with id, user_id, created_at, updated_at fields
- [ ] T006 [P] Create Message model in backend/app/models/message.py with id, conversation_id, user_id, role, content, created_at fields
- [ ] T007 [P] Create MessageRole enum in backend/app/models/message.py with USER and ASSISTANT values
- [ ] T008 [P] Update User model in backend/app/models/user.py to add conversations and messages relationships
- [ ] T009 Create Alembic migration script in backend/alembic/versions/xxx_add_conversation_message_tables.py for conversations and messages tables
- [ ] T010 Run Alembic migration with alembic upgrade head to create database tables
- [ ] T011 [P] Create ConversationSchema in backend/app/schemas/conversation.py for API responses
- [ ] T012 [P] Create MessageSchema in backend/app/schemas/message.py for API responses
- [ ] T013 Implement ConversationService in backend/app/services/conversation_service.py with create_conversation, get_conversation, load_messages, add_message methods

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Natural Language Task Creation (Priority: P1) 🎯 MVP

**Goal**: Enable users to create tasks using natural language commands like "Add buy groceries to my list"

**Independent Test**: User sends "Add buy groceries to my list" via POST /api/chat. System creates task, persists conversation, and responds with confirmation. Task appears in existing REST API responses.

### Implementation for User Story 1

- [ ] T014 [P] [US1] Create ChatRequest schema in backend/app/schemas/chat.py with conversation_id (nullable int) and message (string) fields
- [ ] T015 [P] [US1] Create ChatResponse schema in backend/app/schemas/chat.py with conversation_id, response, and tool_calls fields
- [ ] T016 [P] [US1] Create ToolCall schema in backend/app/schemas/chat.py with tool (string) and arguments (dict) fields
- [ ] T017 [US1] Implement MCPClient in backend/app/services/mcp_client.py with placeholder tool registration (create_task, list_tasks, update_task, delete_task, get_task)
- [ ] T018 [US1] Implement AgentService in backend/app/services/agent_service.py with OpenAI AsyncClient initialization and assistant configuration
- [ ] T019 [US1] Add build_agent_context method to AgentService in backend/app/services/agent_service.py to reconstruct conversation history from messages
- [ ] T020 [US1] Add run_agent method to AgentService in backend/app/services/agent_service.py to process user message and invoke MCP tools
- [ ] T021 [US1] Add system prompt configuration to AgentService in backend/app/services/agent_service.py with task management capabilities and behavior guidelines
- [ ] T022 [US1] Implement POST /api/chat endpoint in backend/app/routes/chat.py with JWT authentication, conversation loading, agent invocation, and response persistence
- [ ] T023 [US1] Add chat router registration to backend/app/main.py to expose /api/chat endpoint
- [ ] T024 [US1] Add error handling to chat endpoint in backend/app/routes/chat.py for validation errors (400), unauthorized (401), forbidden (403), not found (404), and server errors (500)
- [ ] T025 [US1] Add logging to AgentService in backend/app/services/agent_service.py for tool invocations (tool name, arguments, user_id, timestamp)

**Checkpoint**: At this point, User Story 1 should be fully functional - users can create tasks via natural language

---

## Phase 4: User Story 2 - Natural Language Task Querying (Priority: P2)

**Goal**: Enable users to view their tasks using natural language queries like "Show me my tasks" or "What do I need to do today?"

**Independent Test**: User sends "Show me my tasks" via POST /api/chat. System retrieves user's tasks via MCP tool, formats response naturally, and returns task list.

### Implementation for User Story 2

- [ ] T026 [US2] Enhance MCPClient in backend/app/services/mcp_client.py to implement list_tasks tool invocation with user_id filtering
- [ ] T027 [US2] Update AgentService system prompt in backend/app/services/agent_service.py to include task querying examples and natural language formatting guidelines
- [ ] T028 [US2] Add response formatting logic to AgentService in backend/app/services/agent_service.py to convert task lists into natural language (e.g., "You have 3 tasks: 1. Buy groceries (pending)...")
- [ ] T029 [US2] Test chat endpoint with task querying commands to verify list_tasks tool invocation and natural language response formatting

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - users can create and view tasks

---

## Phase 5: User Story 5 - Conversation Resume (Priority: P2)

**Goal**: Enable users to continue previous conversations after closing chat or restarting server (validates stateless architecture)

**Independent Test**: User starts conversation, creates task, closes chat. User reopens chat with same conversation_id. System loads conversation history and maintains context.

### Implementation for User Story 5

- [ ] T030 [US5] Add conversation_id validation to chat endpoint in backend/app/routes/chat.py to verify conversation belongs to authenticated user
- [ ] T031 [US5] Add conversation history loading to chat endpoint in backend/app/routes/chat.py when conversation_id is provided
- [ ] T032 [US5] Add token limit management to AgentService in backend/app/services/agent_service.py to truncate conversation history if exceeds ~100k tokens (keep last 50 messages)
- [ ] T033 [US5] Add conversation context reconstruction to AgentService in backend/app/services/agent_service.py to build agent context from loaded messages
- [ ] T034 [US5] Test conversation resume by creating conversation, restarting backend server, and sending new message with conversation_id

**Checkpoint**: At this point, User Stories 1, 2, AND 5 should work - users can create/view tasks and resume conversations after server restart

---

## Phase 6: User Story 3 - Natural Language Task Updates (Priority: P3)

**Goal**: Enable users to mark tasks as complete or update task details using natural language commands like "Mark buy groceries as done"

**Independent Test**: User sends "Mark buy groceries as done" via POST /api/chat. System updates task status, persists conversation, and confirms action.

### Implementation for User Story 3

- [ ] T035 [US3] Enhance MCPClient in backend/app/services/mcp_client.py to implement update_task tool invocation with task_id and updates parameters
- [ ] T036 [US3] Enhance MCPClient in backend/app/services/mcp_client.py to implement get_task tool invocation for task lookup by title or reference
- [ ] T037 [US3] Update AgentService system prompt in backend/app/services/agent_service.py to include task update examples and confirmation patterns for destructive actions
- [ ] T038 [US3] Add confirmation logic to AgentService in backend/app/services/agent_service.py to ask user for confirmation before updating tasks (e.g., "Do you want to mark 'buy groceries' as complete?")
- [ ] T039 [US3] Test chat endpoint with task update commands to verify update_task tool invocation and confirmation workflow

**Checkpoint**: At this point, User Stories 1, 2, 3, AND 5 should work - users can create, view, update tasks and resume conversations

---

## Phase 7: User Story 4 - Natural Language Task Deletion (Priority: P4)

**Goal**: Enable users to remove tasks from their list using natural language commands like "Delete buy groceries"

**Independent Test**: User sends "Delete buy groceries" via POST /api/chat. System removes task, persists conversation, and confirms deletion.

### Implementation for User Story 4

- [ ] T040 [US4] Enhance MCPClient in backend/app/services/mcp_client.py to implement delete_task tool invocation with task_id parameter
- [ ] T041 [US4] Update AgentService system prompt in backend/app/services/agent_service.py to include task deletion examples and mandatory confirmation patterns
- [ ] T042 [US4] Add deletion confirmation logic to AgentService in backend/app/services/agent_service.py to require explicit user confirmation before deleting tasks
- [ ] T043 [US4] Add bulk deletion handling to AgentService in backend/app/services/agent_service.py to list tasks and confirm before bulk operations (e.g., "Remove all completed tasks")
- [ ] T044 [US4] Test chat endpoint with task deletion commands to verify delete_task tool invocation and confirmation workflow

**Checkpoint**: All user stories should now be independently functional - full CRUD operations via natural language

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and production readiness

- [ ] T045 [P] Add rate limiting to chat endpoint in backend/app/routes/chat.py (60 requests per minute per user)
- [ ] T046 [P] Add input validation to chat endpoint in backend/app/routes/chat.py for message length (max 10,000 characters) and malicious content
- [ ] T047 [P] Add retry logic to AgentService in backend/app/services/agent_service.py for OpenAI API failures (3 retries with exponential backoff)
- [ ] T048 [P] Add retry logic to MCPClient in backend/app/services/mcp_client.py for tool invocation failures (2 retries with linear backoff)
- [ ] T049 [P] Add error sanitization to chat endpoint in backend/app/routes/chat.py to prevent leaking system internals in error messages
- [ ] T050 [P] Add comprehensive logging to ConversationService in backend/app/services/conversation_service.py for debugging (user_id, conversation_id, operation)
- [ ] T051 Add database query optimization to ConversationService in backend/app/services/conversation_service.py with proper indexing for conversation history queries
- [ ] T052 Validate quickstart.md by following setup steps and testing all user stories end-to-end
- [ ] T053 Update backend API documentation to include POST /api/chat endpoint with request/response examples
- [ ] T054 Verify backward compatibility by testing all Phase I & II REST endpoints remain unchanged and functional

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Builds on US1 but independently testable
- **User Story 5 (P2)**: Can start after US1 complete - Validates stateless architecture
- **User Story 3 (P3)**: Can start after US1 and US2 complete - Requires task lookup and update capabilities
- **User Story 4 (P4)**: Can start after US1 and US2 complete - Requires task lookup and deletion capabilities

### Within Each User Story

- Schemas before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T002, T003)
- All Foundational tasks marked [P] can run in parallel within their dependency groups:
  - Models: T005, T006, T007, T008 (parallel)
  - Schemas: T011, T012 (parallel, after models)
- Within User Story 1: T014, T015, T016 (schemas) can run in parallel
- Within Polish phase: T045, T046, T047, T048, T049, T050 can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all schemas for User Story 1 together:
Task: "Create ChatRequest schema in backend/app/schemas/chat.py"
Task: "Create ChatResponse schema in backend/app/schemas/chat.py"
Task: "Create ToolCall schema in backend/app/schemas/chat.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T004)
2. Complete Phase 2: Foundational (T005-T013) - CRITICAL - blocks all stories
3. Complete Phase 3: User Story 1 (T014-T025)
4. **STOP and VALIDATE**: Test User Story 1 independently
   - Send "Add buy groceries to my list"
   - Verify task created in database
   - Verify conversation persisted
   - Verify natural language response
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 5 → Test independently → Deploy/Demo (validates stateless architecture)
5. Add User Story 3 → Test independently → Deploy/Demo
6. Add User Story 4 → Test independently → Deploy/Demo
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (T014-T025)
   - Developer B: User Story 2 (T026-T029) - starts after US1 complete
   - Developer C: User Story 5 (T030-T034) - starts after US1 complete
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Tests are NOT included per specification (no TDD requested)
- MCP Tool Server implementation is out of scope (separate spec 006-mcp-tool-server)
- Frontend implementation is out of scope (separate spec 007-chat-frontend)
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

---

## Task Count Summary

- **Total Tasks**: 54
- **Setup (Phase 1)**: 4 tasks
- **Foundational (Phase 2)**: 9 tasks
- **User Story 1 (Phase 3)**: 12 tasks
- **User Story 2 (Phase 4)**: 4 tasks
- **User Story 5 (Phase 5)**: 5 tasks
- **User Story 3 (Phase 6)**: 5 tasks
- **User Story 4 (Phase 7)**: 5 tasks
- **Polish (Phase 8)**: 10 tasks

**Parallel Opportunities**: 15 tasks marked [P] can run in parallel within their phases

**MVP Scope**: Phase 1 (4 tasks) + Phase 2 (9 tasks) + Phase 3 (12 tasks) = 25 tasks for MVP
