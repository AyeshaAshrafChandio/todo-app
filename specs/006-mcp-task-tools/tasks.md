# Tasks: MCP Task Tools

**Input**: Design documents from `/specs/006-mcp-task-tools/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/mcp-tools.yaml

**Tests**: Not explicitly requested in specification - focusing on implementation tasks only

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each tool.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Backend: `backend/app/`
- Tests: `backend/tests/`
- All paths relative to repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and verification of existing structure

- [x] T001 Verify MCP SDK (mcp-python 0.1.0+) is installed in backend environment
- [x] T002 Verify existing task service layer is accessible at backend/app/services/task_service.py
- [x] T003 Verify existing database connection utilities at backend/app/database/connection.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core schemas that MUST be complete before ANY tool can be implemented

**⚠️ CRITICAL**: No tool implementation can begin until this phase is complete

- [x] T004 Create tool input/output schemas in backend/app/schemas/mcp_schemas.py
  - AddTaskInput, AddTaskOutput
  - ListTasksInput, ListTasksOutput, TaskItem, TaskStatus enum
  - UpdateTaskInput, UpdateTaskOutput, TaskUpdates
  - DeleteTaskInput, DeleteTaskOutput
  - GetTaskInput, GetTaskOutput
  - ToolError, ToolErrorType enum
  - All Pydantic models with validators per data-model.md

**Checkpoint**: Foundation ready - tool implementation can now begin in parallel

---

## Phase 3: User Story 1 - Task Creation via MCP Tool (Priority: P1) 🎯 MVP

**Goal**: Enable AI agent to create tasks through secure, auditable add_task tool that delegates to existing task service

**Independent Test**: Agent calls add_task(user_id="123", title="Buy groceries", description="Milk, eggs, bread"). Tool validates inputs, delegates to TaskService.create_task(), persists to database, returns {task_id: 1, status: "created", title: "Buy groceries"}. Task appears in database and existing REST API responses.

### Implementation for User Story 1

- [x] T005 [US1] Implement add_task tool handler in backend/app/services/mcp_tools.py
  - @Tool decorator with name="add_task", description, parameters
  - Async handler function: validate input with AddTaskInput schema
  - Get database session via get_db()
  - Delegate to TaskService.create_task(db, user_id, title, description)
  - Format response with AddTaskOutput schema
  - JSON-structured logging (invocation, success/error, execution time)
  - Error handling: ValidationError, ServerError with ToolError responses
  - Return dict response

- [x] T006 [US1] Update MCP client registration in backend/app/services/mcp_client.py
  - Import add_task from mcp_tools
  - Register add_task tool in _register_tools() method
  - Verify tool is callable via call_tool("add_task", **kwargs)

**Checkpoint**: At this point, User Story 1 (add_task tool) should be fully functional and testable independently

---

## Phase 4: User Story 5 - Task Retrieval via MCP Tool (Priority: P2)

**Goal**: Enable AI agent to retrieve single task details through secure get_task tool for validation before updates/deletions

**Independent Test**: Agent calls get_task(user_id="123", task_id=1). Tool validates ownership, queries TaskService.get_task(), returns complete task details {id, title, description, completed, created_at, updated_at}. Authorization errors returned for cross-user access attempts.

### Implementation for User Story 5

- [x] T007 [P] [US5] Implement get_task tool handler in backend/app/services/mcp_tools.py
  - @Tool decorator with name="get_task", description, parameters
  - Async handler: validate input with GetTaskInput schema
  - Get database session
  - Delegate to TaskService.get_task(db, user_id, task_id)
  - Handle ValueError (not found/unauthorized) → NotFoundError or AuthorizationError
  - Format response with GetTaskOutput schema
  - JSON-structured logging
  - Return dict response

- [x] T008 [US5] Update MCP client registration in backend/app/services/mcp_client.py
  - Import get_task from mcp_tools
  - Register get_task tool in _register_tools() method

**Checkpoint**: At this point, User Stories 1 AND 5 should both work independently

---

## Phase 5: User Story 2 - Task Listing via MCP Tool (Priority: P2)

**Goal**: Enable AI agent to retrieve user's tasks through secure list_tasks tool with optional status filtering

**Independent Test**: Agent calls list_tasks(user_id="123", status="all"). Tool queries TaskService.list_tasks(), filters by authenticated user, returns structured list [{id, title, description, completed, created_at, updated_at}, ...]. Empty array returned for users with no tasks.

### Implementation for User Story 2

- [x] T009 [P] [US2] Implement list_tasks tool handler in backend/app/services/mcp_tools.py
  - @Tool decorator with name="list_tasks", description, parameters
  - Async handler: validate input with ListTasksInput schema
  - Get database session
  - Delegate to TaskService.list_tasks(db, user_id, status)
  - Convert Task models to TaskItem schemas
  - Format response with ListTasksOutput schema (tasks array, count)
  - JSON-structured logging
  - Return dict response

- [x] T010 [US2] Update MCP client registration in backend/app/services/mcp_client.py
  - Import list_tasks from mcp_tools
  - Register list_tasks tool in _register_tools() method

**Checkpoint**: At this point, User Stories 1, 2, AND 5 should all work independently

---

## Phase 6: User Story 3 - Task Update via MCP Tool (Priority: P3)

**Goal**: Enable AI agent to update task details (title, description, completion status) through secure update_task tool

**Independent Test**: Agent calls update_task(user_id="123", task_id=1, updates={completed: true}). Tool validates ownership, delegates to TaskService.update_task(), persists changes, returns updated task details. Authorization errors returned for cross-user access attempts.

### Implementation for User Story 3

- [x] T011 [P] [US3] Implement update_task tool handler in backend/app/services/mcp_tools.py
  - @Tool decorator with name="update_task", description, parameters
  - Async handler: validate input with UpdateTaskInput schema
  - Get database session
  - Delegate to TaskService.update_task(db, user_id, task_id, updates.dict(exclude_unset=True))
  - Handle ValueError (not found/unauthorized) → NotFoundError or AuthorizationError
  - Format response with UpdateTaskOutput schema
  - JSON-structured logging
  - Return dict response

- [x] T012 [US3] Update MCP client registration in backend/app/services/mcp_client.py
  - Import update_task from mcp_tools
  - Register update_task tool in _register_tools() method

**Checkpoint**: At this point, User Stories 1, 2, 3, AND 5 should all work independently

---

## Phase 7: User Story 4 - Task Deletion via MCP Tool (Priority: P4)

**Goal**: Enable AI agent to delete tasks through secure delete_task tool with ownership validation

**Independent Test**: Agent calls delete_task(user_id="123", task_id=1). Tool validates ownership, delegates to TaskService.delete_task(), removes from database, returns {status: "deleted", task_id: 1}. Authorization errors returned for cross-user access attempts. Idempotent (deleting already-deleted task returns not found).

### Implementation for User Story 4

- [x] T013 [P] [US4] Implement delete_task tool handler in backend/app/services/mcp_tools.py
  - @Tool decorator with name="delete_task", description, parameters
  - Async handler: validate input with DeleteTaskInput schema
  - Get database session
  - Delegate to TaskService.delete_task(db, user_id, task_id)
  - Handle ValueError (not found/unauthorized) → NotFoundError or AuthorizationError
  - Format response with DeleteTaskOutput schema
  - JSON-structured logging
  - Return dict response

- [x] T014 [US4] Update MCP client registration in backend/app/services/mcp_client.py
  - Import delete_task from mcp_tools
  - Register delete_task tool in _register_tools() method

**Checkpoint**: All 5 tools should now be independently functional

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple tools and ensure production readiness

- [x] T015 [P] Add comprehensive docstrings to all tool handlers in backend/app/services/mcp_tools.py
- [x] T016 [P] Verify JSON-structured logging format matches specification for all tools
- [x] T017 [P] Review error handling consistency across all 5 tools
- [x] T018 [P] Verify all tools return structured ToolError responses for failures
- [x] T019 Validate quickstart.md instructions work end-to-end
- [x] T020 Update backend/README.md with MCP tools documentation (if applicable)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all tool implementations
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - Tools can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4)
- **Polish (Phase 8)**: Depends on all desired tools being complete

### User Story Dependencies

- **User Story 1 (P1) - add_task**: Can start after Foundational (Phase 2) - No dependencies on other tools
- **User Story 5 (P2) - get_task**: Can start after Foundational (Phase 2) - No dependencies on other tools
- **User Story 2 (P2) - list_tasks**: Can start after Foundational (Phase 2) - No dependencies on other tools
- **User Story 3 (P3) - update_task**: Can start after Foundational (Phase 2) - No dependencies on other tools
- **User Story 4 (P4) - delete_task**: Can start after Foundational (Phase 2) - No dependencies on other tools

### Within Each User Story

- Tool handler implementation before MCP client registration
- MCP client registration depends on tool handler being complete
- All tools are independent and can be implemented in parallel after Phase 2

### Parallel Opportunities

- All Setup tasks (T001-T003) can run in parallel
- Phase 2 (T004) is single task - must complete before any tool work
- Once Phase 2 completes, all tool implementations can start in parallel:
  - T005 (add_task handler) || T007 (get_task handler) || T009 (list_tasks handler) || T011 (update_task handler) || T013 (delete_task handler)
- MCP client registration tasks (T006, T008, T010, T012, T014) must follow their respective handlers but can be batched
- All Polish tasks (T015-T018) can run in parallel

---

## Parallel Example: All Tools After Foundation

```bash
# After Phase 2 (T004) completes, launch all tool handlers in parallel:
Task: "Implement add_task tool handler in backend/app/services/mcp_tools.py"
Task: "Implement get_task tool handler in backend/app/services/mcp_tools.py"
Task: "Implement list_tasks tool handler in backend/app/services/mcp_tools.py"
Task: "Implement update_task tool handler in backend/app/services/mcp_tools.py"
Task: "Implement delete_task tool handler in backend/app/services/mcp_tools.py"

# Then batch all MCP client registrations:
Task: "Update MCP client registration for add_task"
Task: "Update MCP client registration for get_task"
Task: "Update MCP client registration for list_tasks"
Task: "Update MCP client registration for update_task"
Task: "Update MCP client registration for delete_task"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004) - CRITICAL
3. Complete Phase 3: User Story 1 (T005-T006)
4. **STOP and VALIDATE**: Test add_task tool independently
   - Agent can create tasks via tool
   - Tasks persist to database
   - Tasks appear in existing REST API
   - Authorization enforced
   - Errors handled gracefully
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 (add_task) → Test independently → Deploy/Demo (MVP!)
3. Add User Story 5 (get_task) → Test independently → Deploy/Demo
4. Add User Story 2 (list_tasks) → Test independently → Deploy/Demo
5. Add User Story 3 (update_task) → Test independently → Deploy/Demo
6. Add User Story 4 (delete_task) → Test independently → Deploy/Demo
7. Each tool adds value without breaking previous tools

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T004)
2. Once Foundational is done:
   - Developer A: User Story 1 (add_task) - T005-T006
   - Developer B: User Story 5 (get_task) - T007-T008
   - Developer C: User Story 2 (list_tasks) - T009-T010
   - Developer D: User Story 3 (update_task) - T011-T012
   - Developer E: User Story 4 (delete_task) - T013-T014
3. Tools complete and integrate independently
4. Team collaborates on Polish phase (T015-T020)

---

## Notes

- [P] tasks = different files or independent sections, no dependencies
- [Story] label maps task to specific user story for traceability
- Each tool should be independently completable and testable
- All tools delegate to existing TaskService (Spec 001) - no direct database access
- All tools enforce authorization at tool level (user_id validation)
- All tools return structured responses (success or ToolError)
- All tools log invocations with JSON-structured format
- Commit after each task or logical group
- Stop at any checkpoint to validate tool independently
- Avoid: vague tasks, same file conflicts, cross-tool dependencies that break independence
