---
id: 005
title: Implement User Story 1 Create Retrieve Tasks
stage: green
date: 2026-02-03
surface: agent
model: claude-sonnet-4-5-20250929
feature: 001-backend-core-data
branch: 001-backend-core-data
user: Ali Haider
command: none
labels: ["implementation", "user-story-1", "fastapi", "rest-api", "service-layer", "testing"]
links:
  spec: specs/001-backend-core-data/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/app/services/task_service.py
  - backend/app/routes/tasks.py
  - backend/app/main.py
  - backend/app/database/connection.py
  - backend/.env
  - backend/tests/test_user_story_1.py
tests:
  - test_create_task_success
  - test_create_task_without_description
  - test_create_task_empty_title_returns_422
  - test_create_task_missing_title_returns_422
  - test_list_tasks_returns_all_user_tasks
  - test_list_tasks_empty_array_for_nonexistent_user
  - test_list_tasks_filters_by_user_id
  - test_get_task_by_id_success
  - test_get_task_nonexistent_id_returns_404
  - test_get_task_wrong_user_returns_404
  - test_created_task_persists_across_requests
  - test_multiple_tasks_persist_in_list
---

## Prompt

Implement User Story 1 (Create and Retrieve Tasks) for the Todo Backend Core & Data Layer feature.

**Context**:
- Feature: 001-backend-core-data
- Branch: 001-backend-core-data
- Spec: specs/001-backend-core-data/spec.md
- Data Model: specs/001-backend-core-data/data-model.md
- Plan: specs/001-backend-core-data/plan.md
- Tasks: specs/001-backend-core-data/tasks.md

**Current State**:
- ✅ Phase 1 (Setup) complete
- ✅ Phase 2 (Foundational) complete
- Database layer implemented (connection.py, Task model)
- Pydantic schemas implemented (TaskCreate, TaskUpdate, TaskResponse)
- FastAPI application initialized (main.py)

**Tasks to Implement (T019-T027)**:

**Service Layer (T019-T021)** - backend/app/services/task_service.py:

**T019**: Implement create_task function:
- Accept: db session, user_id, TaskCreate schema
- Validate: title is not empty (Pydantic handles this)
- Create: Task instance with user_id from path parameter
- Set: completed=False, auto-generate timestamps
- Save: to database and commit
- Return: created Task instance
- Error handling: database errors

**T020**: Implement get_tasks_by_user function:
- Accept: db session, user_id
- Query: all tasks where user_id matches
- Return: list of Task instances (can be empty)
- No error for empty list (return [])

**T021**: Implement get_task_by_id function:
- Accept: db session, user_id, task_id
- Query: task where id=task_id AND user_id=user_id
- Return: Task instance if found
- Raise: HTTPException(404) if not found
- Error message: "Task not found"

**API Routes (T022-T024)** - backend/app/routes/tasks.py:

**T022**: POST /api/{user_id}/tasks endpoint:
- Path parameter: user_id (str)
- Request body: TaskCreate schema
- Dependency: get_db for database session
- Call: create_task service function
- Response: 201 Created with TaskResponse schema
- Error handling: 422 for validation errors (automatic)

**T023**: GET /api/{user_id}/tasks endpoint:
- Path parameter: user_id (str)
- Dependency: get_db for database session
- Call: get_tasks_by_user service function
- Response: 200 OK with List[TaskResponse]
- Return empty array if no tasks

**T024**: GET /api/{user_id}/tasks/{id} endpoint:
- Path parameters: user_id (str), id (int)
- Dependency: get_db for database session
- Call: get_task_by_id service function
- Response: 200 OK with TaskResponse
- Error handling: 404 if task not found (service raises HTTPException)

**Route Registration & Error Handling (T025-T027)**:

**T025**: Register task routes in backend/app/main.py:
- Import: APIRouter from routes.tasks
- Include: app.include_router(router)
- No prefix needed (routes already have /api/{user_id}/tasks)

**T026**: Add HTTPException handling for 404 Not Found:
- Already handled in service layer (get_task_by_id raises HTTPException)
- Ensure proper error response format: {"detail": "Task not found"}

**T027**: Add validation error handling for 422 Unprocessable Entity:
- FastAPI handles this automatically via Pydantic validation
- Ensure proper error response format with field locations

**Requirements**:

1. **Service Layer Design**:
   - Pure business logic, no HTTP concerns
   - Accept database session as first parameter
   - Return domain objects (Task instances)
   - Raise HTTPException for errors (404)
   - Use SQLModel select() for queries

2. **API Routes Design**:
   - Use FastAPI APIRouter
   - Proper HTTP status codes (200, 201, 404, 422)
   - Dependency injection for database session
   - Convert Task instances to TaskResponse schemas
   - Proper path parameters and request bodies

3. **Error Handling**:
   - 404: Task not found (HTTPException in service)
   - 422: Validation errors (automatic via Pydantic)
   - Proper error response format: {"detail": "message"}

4. **Database Operations**:
   - Use SQLModel select() for queries
   - Use session.add() for inserts
   - Use session.commit() to persist
   - Use session.refresh() to get auto-generated values

5. **Validation**:
   - Title validation (min_length=1) handled by Pydantic
   - User_id from path parameter (no validation in Spec-1)
   - Timestamps auto-generated by SQLModel defaults

**Acceptance Criteria** (from spec.md):
- POST /api/user123/tasks with title "Buy groceries" returns 201 with auto-generated id and timestamps
- GET /api/user123/tasks returns 200 with array of all tasks for user123
- GET /api/user123/tasks/5 returns 200 with complete task details or 404 if not found
- POST with empty title returns 422 validation error
- GET for non-existent user returns 200 with empty array

**Testing**:
- Create integration tests for all three endpoints
- Test success scenarios (201, 200)
- Test error scenarios (404, 422)
- Test empty list scenario

Please implement these tasks following the spec-driven approach. Generate all code - no manual edits allowed.

## Response snapshot

Successfully implemented User Story 1 (Create and Retrieve Tasks) with complete service layer, API routes, and comprehensive integration tests.

**Implementation Summary**:

1. **Service Layer** (backend/app/services/task_service.py):
   - `create_task()`: Creates tasks with auto-generated ID/timestamps, handles database errors
   - `get_tasks_by_user()`: Retrieves all tasks for a user, returns empty list if none exist
   - `get_task_by_id()`: Retrieves single task with user_id filtering, raises 404 if not found

2. **API Routes** (backend/app/routes/tasks.py):
   - POST /api/{user_id}/tasks: Creates task, returns 201 Created
   - GET /api/{user_id}/tasks: Lists all tasks, returns 200 OK
   - GET /api/{user_id}/tasks/{id}: Gets single task, returns 200 OK or 404 Not Found

3. **Route Registration** (backend/app/main.py):
   - Registered task router with app.include_router()

4. **Database Enhancement** (backend/app/database/connection.py):
   - Added SQLite support for local development/testing
   - Maintains PostgreSQL configuration for production

5. **Integration Tests** (backend/tests/test_user_story_1.py):
   - 12 comprehensive test cases covering all scenarios
   - Tests for success cases, error cases, and data persistence
   - All tests passing (12/12)

**Test Results**: All 12 tests passed successfully, validating all acceptance criteria.

**Key Design Decisions**:
- Separation of concerns: Service layer handles business logic, routes handle HTTP
- Dependency injection for database sessions
- HTTPException raised in service layer for 404 errors
- Pydantic handles validation automatically (422 errors)
- SQLite support added for testing without PostgreSQL dependency

## Outcome

- ✅ Impact: User Story 1 fully implemented and tested - API consumers can now create and retrieve tasks via REST API
- 🧪 Tests: 12 integration tests created and passing (100% success rate)
- 📁 Files: 4 new files created, 2 files modified (service layer, routes, tests, config)
- 🔁 Next prompts: Implement User Story 2 (Update and Delete Tasks - T028-T033) or User Story 3 (Toggle Completion - T034-T036)
- 🧠 Reflection: Clean implementation following FastAPI best practices with proper separation of concerns. SQLite support enables testing without PostgreSQL dependency. All acceptance criteria validated.

## Evaluation notes (flywheel)

- Failure modes observed: Initial psycopg2 installation failure on Windows (resolved by using SQLite for testing), database connection at import time required flexible configuration
- Graders run and results (PASS/FAIL): All 12 integration tests PASS, server startup successful, database initialization successful
- Prompt variant (if applicable): Standard implementation prompt with detailed task breakdown
- Next experiment (smallest change to try): Consider async database operations for improved performance in User Story 2
