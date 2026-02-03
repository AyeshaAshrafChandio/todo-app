# Tasks: Todo Backend Core & Data Layer

**Input**: Design documents from `/specs/001-backend-core-data/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/openapi.yaml

**Tests**: Tests are NOT included in this task list as they were not explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

All paths are relative to repository root: `backend/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create backend directory structure with app/, tests/, and configuration files
- [x] T002 Create requirements.txt with FastAPI, SQLModel, Uvicorn, python-dotenv, psycopg2-binary, pytest dependencies
- [x] T003 [P] Create .env.example file with DATABASE_URL, DATABASE_POOL_SIZE, DATABASE_POOL_RECYCLE, DATABASE_ECHO template
- [x] T004 [P] Create backend/README.md with project overview and setup instructions
- [x] T005 [P] Create backend/app/__init__.py as empty module initializer

**Checkpoint**: ✅ Project structure ready for foundational implementation

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T006 Create backend/app/config.py with Settings class for environment variable management using pydantic-settings
- [x] T007 Create backend/app/database/__init__.py as empty module initializer
- [x] T008 Create backend/app/database/connection.py with SQLModel engine, session factory, and get_db dependency function
- [x] T009 Create backend/app/models/__init__.py as empty module initializer
- [x] T010 Create backend/app/models/task.py with Task SQLModel class including all 7 fields (id, title, description, completed, created_at, updated_at, user_id) and validation rules
- [x] T011 Create backend/app/schemas/__init__.py as empty module initializer
- [x] T012 [P] Create backend/app/schemas/task.py with TaskCreate Pydantic schema (title, description)
- [x] T013 [P] Create backend/app/schemas/task.py with TaskUpdate Pydantic schema (title, description, completed)
- [x] T014 [P] Create backend/app/schemas/task.py with TaskResponse Pydantic schema (all fields with from_attributes=True)
- [x] T015 Create backend/app/services/__init__.py as empty module initializer
- [x] T016 Create backend/app/routes/__init__.py as empty module initializer
- [x] T017 Create backend/app/main.py with FastAPI application instance, CORS middleware, and startup/shutdown events for database
- [x] T018 Add database initialization logic to backend/app/main.py startup event to create tables using SQLModel.metadata.create_all()

**Checkpoint**: ✅ Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Create and Retrieve Tasks (Priority: P1) 🎯 MVP

**Goal**: Enable API consumers to create new tasks and retrieve all tasks for a user, providing foundational CRUD functionality

**Independent Test**: Make POST requests to create tasks and GET requests to retrieve them, verifying data persistence across requests

**Functional Requirements**: FR-001, FR-002, FR-003, FR-004, FR-005, FR-006, FR-011, FR-012, FR-013, FR-014, FR-015, FR-016, FR-017, FR-018

### Implementation for User Story 1

- [x] T019 [P] [US1] Implement create_task function in backend/app/services/task_service.py with validation, timestamp generation, and database persistence
- [x] T020 [P] [US1] Implement get_tasks_by_user function in backend/app/services/task_service.py to retrieve all tasks for a user_id
- [x] T021 [P] [US1] Implement get_task_by_id function in backend/app/services/task_service.py to retrieve single task with 404 handling
- [x] T022 [US1] Create POST /api/{user_id}/tasks endpoint in backend/app/routes/tasks.py that calls create_task service and returns 201 with TaskResponse
- [x] T023 [US1] Create GET /api/{user_id}/tasks endpoint in backend/app/routes/tasks.py that calls get_tasks_by_user service and returns 200 with list of TaskResponse
- [x] T024 [US1] Create GET /api/{user_id}/tasks/{id} endpoint in backend/app/routes/tasks.py that calls get_task_by_id service and returns 200 with TaskResponse or 404
- [x] T025 [US1] Register task routes in backend/app/main.py using app.include_router() with /api prefix
- [x] T026 [US1] Add HTTPException handling for 404 Not Found in backend/app/routes/tasks.py for non-existent tasks
- [x] T027 [US1] Add validation error handling for 422 Unprocessable Entity in backend/app/routes/tasks.py for invalid request data

**Checkpoint**: ✅ User Story 1 is fully functional - users can create tasks and retrieve them via API

**Acceptance Validation**:
- POST /api/user123/tasks with title "Buy groceries" returns 201 with auto-generated id and timestamps
- GET /api/user123/tasks returns 200 with array of all tasks for user123
- GET /api/user123/tasks/5 returns 200 with complete task details or 404 if not found
- POST with empty title returns 422 validation error
- GET for non-existent user returns 200 with empty array

---

## Phase 4: User Story 2 - Update and Delete Tasks (Priority: P2)

**Goal**: Enable API consumers to update existing task details and delete tasks, completing the CRUD experience

**Independent Test**: Create a task using US1 functionality, update its properties and verify persistence, then delete it and confirm removal

**Functional Requirements**: FR-007, FR-008, FR-009, FR-012, FR-013, FR-014, FR-017, FR-018

### Implementation for User Story 2

- [x] T028 [P] [US2] Implement update_task function in backend/app/services/task_service.py with validation, updated_at refresh, and 404 handling
- [x] T029 [P] [US2] Implement delete_task function in backend/app/services/task_service.py with 404 handling and hard delete
- [x] T030 [US2] Create PUT /api/{user_id}/tasks/{id} endpoint in backend/app/routes/tasks.py that calls update_task service and returns 200 with updated TaskResponse or 404
- [x] T031 [US2] Create DELETE /api/{user_id}/tasks/{id} endpoint in backend/app/routes/tasks.py that calls delete_task service and returns 204 No Content or 404
- [x] T032 [US2] Add validation to ensure updated_at timestamp is automatically refreshed on task updates in backend/app/services/task_service.py
- [x] T033 [US2] Add error handling for database constraint violations in backend/app/routes/tasks.py

**Checkpoint**: ✅ User Stories 1 AND 2 are both working independently - full CRUD operations are available

**Acceptance Validation**:
- PUT /api/user123/tasks/5 with new title and description returns 200 with updated task and refreshed updated_at
- DELETE /api/user123/tasks/5 returns 204, subsequent GET returns 404
- PUT for non-existent task returns 404
- PUT with invalid data returns 422 validation error

---

## Phase 5: User Story 3 - Toggle Task Completion (Priority: P3)

**Goal**: Provide a dedicated endpoint to toggle task completion status for better UX and semantic clarity

**Independent Test**: Create a task using US1, use PATCH endpoint to toggle completion multiple times, verify boolean state changes correctly

**Functional Requirements**: FR-010, FR-008, FR-012, FR-013, FR-017

### Implementation for User Story 3

- [x] T034 [US3] Implement toggle_task_completion function in backend/app/services/task_service.py that flips completed boolean, refreshes updated_at, and handles 404
- [x] T035 [US3] Create PATCH /api/{user_id}/tasks/{id}/complete endpoint in backend/app/routes/tasks.py that calls toggle_task_completion service and returns 200 with TaskResponse or 404
- [x] T036 [US3] Add logic to ensure toggle works correctly for both completed=true and completed=false states in backend/app/services/task_service.py

**Checkpoint**: ✅ All user stories are independently functional - complete task management API is available

**Acceptance Validation**:
- PATCH /api/user123/tasks/5/complete on task with completed=false returns 200 with completed=true and refreshed updated_at
- PATCH /api/user123/tasks/5/complete on task with completed=true returns 200 with completed=false (toggle behavior)
- PATCH for non-existent task returns 404
- Completion status persists across requests

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final validation

- [x] T037 [P] Add global exception handler in backend/app/main.py for 500 Internal Server Error with appropriate error messages
- [x] T038 [P] Add database connection error handling in backend/app/database/connection.py with retry logic
- [x] T039 [P] Verify FastAPI auto-generated OpenAPI documentation is accessible at /docs and /redoc endpoints
- [x] T040 [P] Add health check endpoint GET /health in backend/app/main.py that returns database connection status
- [x] T041 Validate all 18 functional requirements from spec.md are implemented correctly
- [x] T042 Validate all 3 user story acceptance scenarios pass end-to-end
- [x] T043 Validate all edge cases from spec.md are handled correctly (404, 422, 500, empty arrays, malformed JSON)
- [x] T044 Run manual API tests using quickstart.md examples to verify all endpoints work correctly
- [x] T045 Verify response times are under 500ms for single operations
- [x] T046 [P] Update backend/README.md with final API documentation and usage examples

**Checkpoint**: ✅ All phases complete - production-ready backend implementation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Uses US1 for testing but is independently implementable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Uses US1 for testing but is independently implementable

### Within Each User Story

- Service layer functions before route endpoints
- Route endpoints before error handling
- Core implementation before validation
- Story complete before moving to next priority

### Parallel Opportunities

- **Phase 1 Setup**: T003, T004, T005 can run in parallel (different files)
- **Phase 2 Foundational**: T012, T013, T014 can run in parallel (different schemas in same file)
- **Phase 3 US1**: T019, T020, T021 can run in parallel (different service functions)
- **Phase 4 US2**: T028, T029 can run in parallel (different service functions)
- **Phase 6 Polish**: T037, T038, T039, T040, T046 can run in parallel (different files)
- **User Stories**: Once Foundational completes, US1, US2, and US3 can be worked on in parallel by different developers

---

## Parallel Example: User Story 1

```bash
# Launch all service functions for User Story 1 together:
Task: "Implement create_task function in backend/app/services/task_service.py"
Task: "Implement get_tasks_by_user function in backend/app/services/task_service.py"
Task: "Implement get_task_by_id function in backend/app/services/task_service.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Foundational (T006-T018) - CRITICAL, blocks all stories
3. Complete Phase 3: User Story 1 (T019-T027)
4. **STOP and VALIDATE**: Test User Story 1 independently using acceptance scenarios
5. Deploy/demo if ready - you now have a working task creation and retrieval API

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP! ✅)
3. Add User Story 2 → Test independently → Deploy/Demo (Full CRUD ✅)
4. Add User Story 3 → Test independently → Deploy/Demo (Complete API ✅)
5. Add Polish → Final validation → Production ready
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T018)
2. Once Foundational is done:
   - Developer A: User Story 1 (T019-T027)
   - Developer B: User Story 2 (T028-T033)
   - Developer C: User Story 3 (T034-T036)
3. Stories complete and integrate independently
4. Team completes Polish together (T037-T046)

---

## Task Summary

**Total Tasks**: 46
**Setup Tasks**: 5 (T001-T005)
**Foundational Tasks**: 13 (T006-T018)
**User Story 1 Tasks**: 9 (T019-T027)
**User Story 2 Tasks**: 6 (T028-T033)
**User Story 3 Tasks**: 3 (T034-T036)
**Polish Tasks**: 10 (T037-T046)

**Parallel Opportunities**: 15 tasks marked [P] can run in parallel
**Independent Stories**: All 3 user stories can be implemented and tested independently after Foundational phase

**Suggested MVP Scope**: Phase 1 + Phase 2 + Phase 3 (User Story 1 only) = 27 tasks

---

## Notes

- [P] tasks = different files or independent functions, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All code must be generated via Claude Code agents (fastapi-backend, neon-db-architect)
- No manual coding allowed per project constitution
- Validate against spec.md functional requirements after each phase
