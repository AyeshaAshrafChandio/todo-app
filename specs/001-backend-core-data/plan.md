# Implementation Plan: Todo Backend Core & Data Layer

**Branch**: `001-backend-core-data` | **Date**: 2026-01-20 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-backend-core-data/spec.md`

## Summary

Build a production-ready FastAPI backend with persistent PostgreSQL storage for a Todo application. This phase (Spec-1) implements core CRUD operations for tasks without authentication enforcement. The backend will provide 6 REST API endpoints for task management, use SQLModel ORM for database operations, and connect to Neon Serverless PostgreSQL for data persistence. Authentication and user isolation will be added in Spec-2.

**Primary Requirement**: Create a stateless REST API that allows task creation, retrieval, updating, deletion, and completion toggling with automatic timestamp management and proper error handling.

**Technical Approach**: Use FastAPI's async capabilities with SQLModel for type-safe database operations, implement proper separation between models, routes, and database logic, and leverage FastAPI's automatic OpenAPI documentation generation.

## Technical Context

**Language/Version**: Python 3.10+
**Primary Dependencies**: FastAPI (latest stable), SQLModel (latest stable), Uvicorn (ASGI server), python-dotenv (environment management)
**Storage**: Neon Serverless PostgreSQL with connection pooling
**Testing**: pytest with pytest-asyncio for async tests
**Target Platform**: Linux server (containerizable)
**Project Type**: Web backend (REST API)
**Performance Goals**: <500ms response time for single operations, 100+ concurrent requests
**Constraints**: No authentication in this phase, user_id is placeholder only, stateless backend
**Scale/Scope**: Single backend service, 6 API endpoints, 1 database table (tasks)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Spec-Driven Development
- ✅ **PASS**: Complete specification exists at `specs/001-backend-core-data/spec.md`
- ✅ **PASS**: All 18 functional requirements are clearly defined
- ✅ **PASS**: API contracts are fully specified with request/response formats
- ✅ **PASS**: Success criteria are measurable and testable

### Principle II: Agentic Workflow Integrity
- ✅ **PASS**: Following spec → plan → tasks → implement workflow
- ✅ **PASS**: Will use `fastapi-backend` agent for implementation
- ✅ **PASS**: Will use `neon-db-architect` agent for database setup
- ⚠️ **NOTE**: No manual coding will be performed; all code generated via Claude Code

### Principle III: Correctness & Consistency
- ✅ **PASS**: API contracts explicitly defined in spec (6 endpoints with full details)
- ✅ **PASS**: Data model clearly specified (Task entity with 7 fields)
- ✅ **PASS**: Error handling specified for all edge cases
- ✅ **PASS**: HTTP status codes defined for all scenarios

### Principle IV: Security by Design
- ⚠️ **DEFERRED**: Authentication and authorization explicitly out of scope for Spec-1
- ✅ **PASS**: Input validation required (FR-011, FR-018)
- ✅ **PASS**: SQL injection prevention via SQLModel parameterized queries
- ✅ **PASS**: No sensitive data in error messages (specified in spec)
- 📋 **NOTE**: Full security implementation will be added in Spec-2 (Authentication & Security)

**Justification for Deferral**: The constitution's Security by Design principle will be fully implemented in Spec-2. Spec-1 focuses on core backend functionality without authentication to enable independent testing of CRUD operations. This is an intentional phased approach documented in the project constitution under "Functional Scope."

### Principle V: Separation of Concerns
- ✅ **PASS**: Backend will be stateless (no session state)
- ✅ **PASS**: Database access abstracted through SQLModel ORM
- ✅ **PASS**: Clear separation planned: models/ (SQLModel), routes/ (API endpoints), database/ (connection)
- ✅ **PASS**: Business logic will reside in service layer, not in routes

**Constitution Check Result**: ✅ **APPROVED** with documented deferral of authentication to Spec-2

## Project Structure

### Documentation (this feature)

```text
specs/001-backend-core-data/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (in progress)
├── research.md          # Phase 0 output (to be created)
├── data-model.md        # Phase 1 output (to be created)
├── quickstart.md        # Phase 1 output (to be created)
├── contracts/           # Phase 1 output (to be created)
│   └── openapi.yaml     # OpenAPI 3.0 specification
├── checklists/          # Quality validation
│   └── requirements.md  # Spec quality checklist (completed)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration and environment variables
│   ├── models/              # SQLModel database models
│   │   ├── __init__.py
│   │   └── task.py          # Task model definition
│   ├── schemas/             # Pydantic request/response schemas
│   │   ├── __init__.py
│   │   └── task.py          # Task schemas (create, update, response)
│   ├── routes/              # API route handlers
│   │   ├── __init__.py
│   │   └── tasks.py         # Task CRUD endpoints
│   ├── database/            # Database connection and session management
│   │   ├── __init__.py
│   │   └── connection.py    # Database engine and session factory
│   └── services/            # Business logic layer
│       ├── __init__.py
│       └── task_service.py  # Task operations logic
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Pytest fixtures and configuration
│   ├── test_tasks_api.py    # API endpoint tests
│   └── test_task_service.py # Service layer tests
├── .env.example             # Environment variable template
├── requirements.txt         # Python dependencies
└── README.md                # Backend setup and usage instructions
```

**Structure Decision**: Using a web backend structure with clear separation of concerns. The `backend/` directory contains the FastAPI application with layered architecture:
- **models/**: SQLModel classes representing database tables
- **schemas/**: Pydantic models for API request/response validation
- **routes/**: API endpoint definitions (thin layer, delegates to services)
- **services/**: Business logic and data operations
- **database/**: Database connection management and session handling

This structure follows FastAPI best practices and enables easy addition of authentication layer in Spec-2.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Security by Design (partial deferral) | Phased implementation approach: Spec-1 focuses on core CRUD, Spec-2 adds authentication | Implementing auth in Spec-1 would create a monolithic spec that's harder to test and validate independently. Phased approach enables incremental verification. |

## Phase 0: Research & Technology Validation

### Research Questions

All technical decisions are clearly specified in the feature spec and project constitution. No research phase is required as:

1. **Framework Choice**: FastAPI is mandated by project constitution
2. **ORM Choice**: SQLModel is mandated by project constitution
3. **Database**: Neon Serverless PostgreSQL is mandated by project constitution
4. **Testing Framework**: pytest is the standard for Python projects
5. **Project Structure**: FastAPI best practices are well-documented

### Technology Validation

**FastAPI + SQLModel + Neon PostgreSQL**:
- ✅ Proven combination for serverless environments
- ✅ SQLModel provides type-safe ORM with Pydantic integration
- ✅ Neon's connection pooling works well with FastAPI's async model
- ✅ Automatic OpenAPI documentation generation included

**Decision**: Proceed directly to Phase 1 (Design) without additional research.

## Phase 1: Design & Contracts

### 1.1 Data Model Design

**Entity**: Task

**Fields**:
- `id`: Integer, primary key, auto-increment
- `title`: String, required, non-empty, max length 200
- `description`: String, optional, nullable, max length 1000
- `completed`: Boolean, default False, required
- `created_at`: DateTime, auto-generated on creation, timezone-aware (UTC)
- `updated_at`: DateTime, auto-generated on creation, auto-updated on modification, timezone-aware (UTC)
- `user_id`: String, required (placeholder for Spec-2), max length 100

**Indexes**:
- Primary key on `id`
- Index on `user_id` (for future filtering in Spec-2)
- Composite index on `(user_id, created_at)` for efficient listing

**Constraints**:
- `title` must not be empty string
- `completed` defaults to False
- Timestamps are immutable (managed by database triggers or ORM)

**State Transitions**:
- Task creation: `completed = False`, timestamps set
- Task update: `updated_at` refreshed automatically
- Task completion toggle: `completed` flips, `updated_at` refreshed
- Task deletion: Hard delete (no soft delete in Spec-1)

### 1.2 API Contract Design

**Base Path**: `/api/{user_id}/tasks`

**Endpoints**:

1. **Create Task**
   - Method: POST
   - Path: `/api/{user_id}/tasks`
   - Request: `TaskCreate` schema (title, description)
   - Response: 201 Created, `TaskResponse` schema
   - Errors: 422 (validation)

2. **List Tasks**
   - Method: GET
   - Path: `/api/{user_id}/tasks`
   - Request: None
   - Response: 200 OK, array of `TaskResponse`
   - Errors: None (empty array if no tasks)

3. **Get Task**
   - Method: GET
   - Path: `/api/{user_id}/tasks/{id}`
   - Request: None
   - Response: 200 OK, `TaskResponse` schema
   - Errors: 404 (not found)

4. **Update Task**
   - Method: PUT
   - Path: `/api/{user_id}/tasks/{id}`
   - Request: `TaskUpdate` schema (title, description, completed)
   - Response: 200 OK, `TaskResponse` schema
   - Errors: 404 (not found), 422 (validation)

5. **Delete Task**
   - Method: DELETE
   - Path: `/api/{user_id}/tasks/{id}`
   - Request: None
   - Response: 204 No Content
   - Errors: 404 (not found)

6. **Toggle Completion**
   - Method: PATCH
   - Path: `/api/{user_id}/tasks/{id}/complete`
   - Request: None
   - Response: 200 OK, `TaskResponse` schema
   - Errors: 404 (not found)

**Schemas**:

```python
# TaskCreate (request body for POST)
{
  "title": str,        # required, min_length=1, max_length=200
  "description": str?  # optional, max_length=1000
}

# TaskUpdate (request body for PUT)
{
  "title": str,        # required, min_length=1, max_length=200
  "description": str?, # optional, max_length=1000
  "completed": bool?   # optional
}

# TaskResponse (response for all endpoints)
{
  "id": int,
  "title": str,
  "description": str?,
  "completed": bool,
  "created_at": str,   # ISO 8601 format
  "updated_at": str,   # ISO 8601 format
  "user_id": str
}
```

### 1.3 Database Connection Strategy

**Connection Management**:
- Use SQLModel's `create_engine()` with connection pooling
- Pool size: 5 connections (suitable for development, adjustable for production)
- Pool recycle: 3600 seconds (1 hour) to prevent stale connections
- Echo SQL: Enabled in development, disabled in production

**Session Management**:
- Use dependency injection for database sessions
- Session per request pattern (FastAPI dependency)
- Automatic session cleanup via context manager
- Transaction support for data integrity

**Environment Configuration**:
```
DATABASE_URL=postgresql://user:password@host:5432/dbname
DATABASE_POOL_SIZE=5
DATABASE_POOL_RECYCLE=3600
DATABASE_ECHO=false
```

### 1.4 Error Handling Strategy

**HTTP Status Codes**:
- 200 OK: Successful GET, PUT, PATCH
- 201 Created: Successful POST
- 204 No Content: Successful DELETE
- 400 Bad Request: Malformed JSON
- 404 Not Found: Resource doesn't exist
- 422 Unprocessable Entity: Validation errors
- 500 Internal Server Error: Database or server errors

**Error Response Format**:
```json
{
  "detail": "Human-readable error message"
}
```

**Validation Error Format** (422):
```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "Error description",
      "type": "error_type"
    }
  ]
}
```

**Error Handling Layers**:
1. **Pydantic Validation**: Automatic request validation
2. **Service Layer**: Business logic errors (e.g., task not found)
3. **Database Layer**: Connection errors, constraint violations
4. **Global Exception Handler**: Catch-all for unexpected errors

### 1.5 Testing Strategy

**Test Levels**:

1. **Unit Tests** (`tests/test_task_service.py`):
   - Test service layer logic in isolation
   - Mock database interactions
   - Verify business logic correctness

2. **Integration Tests** (`tests/test_tasks_api.py`):
   - Test API endpoints end-to-end
   - Use test database (SQLite in-memory or separate PostgreSQL)
   - Verify request/response formats
   - Test all success and error scenarios

**Test Coverage Requirements**:
- Minimum 80% code coverage
- All API endpoints must have tests
- All error scenarios must be tested
- Edge cases from spec must be covered

**Test Fixtures** (`tests/conftest.py`):
- Test database setup/teardown
- Test client fixture
- Sample task data fixtures

### 1.6 Development Workflow

**Setup Steps**:
1. Create virtual environment
2. Install dependencies from `requirements.txt`
3. Configure `.env` file with database credentials
4. Run database migrations (create tables)
5. Start development server with `uvicorn`

**Development Commands**:
```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest tests/ -v --cov=app

# Access API documentation
# http://localhost:8000/docs (Swagger UI)
# http://localhost:8000/redoc (ReDoc)
```

## Phase 1 Outputs

The following artifacts will be created during Phase 1:

1. **data-model.md**: Detailed data model documentation with SQLModel schema definitions
2. **contracts/openapi.yaml**: Complete OpenAPI 3.0 specification for all 6 endpoints
3. **quickstart.md**: Developer guide for setting up and running the backend

## Architectural Decisions

### AD-001: Layered Architecture Pattern

**Decision**: Implement a layered architecture with clear separation between routes, services, and models.

**Rationale**:
- Enables independent testing of each layer
- Facilitates addition of authentication middleware in Spec-2
- Follows FastAPI best practices
- Improves code maintainability and readability

**Alternatives Considered**:
- **Flat structure with routes only**: Rejected because it mixes concerns and makes testing harder
- **Repository pattern**: Rejected as unnecessary complexity for this simple CRUD application

### AD-002: Automatic Timestamp Management

**Decision**: Use SQLModel's `default` and `onupdate` parameters for timestamp management.

**Rationale**:
- Prevents manual timestamp errors
- Ensures consistency across all operations
- Reduces boilerplate code
- Aligns with spec requirement (FR-003, FR-008)

**Alternatives Considered**:
- **Database triggers**: Rejected to keep logic in application layer
- **Manual timestamp setting**: Rejected due to error-prone nature

### AD-003: Stateless Backend Design

**Decision**: Backend will not maintain any session state; all requests are independent.

**Rationale**:
- Aligns with constitution principle V (Separation of Concerns)
- Enables horizontal scaling in future
- Simplifies testing and debugging
- Prepares for JWT-based authentication in Spec-2

**Alternatives Considered**:
- **Session-based state**: Rejected as it conflicts with JWT authentication planned for Spec-2

### AD-004: User ID as Path Parameter

**Decision**: Include `user_id` in URL path (`/api/{user_id}/tasks`) rather than query parameter or request body.

**Rationale**:
- RESTful design principle (resource hierarchy)
- Prepares for authentication in Spec-2 (user_id will be validated against JWT)
- Makes API more intuitive and self-documenting
- Aligns with spec requirement (FR-016)

**Alternatives Considered**:
- **Query parameter**: Rejected as less RESTful
- **Request header**: Rejected as less discoverable in API documentation

## Implementation Readiness

### Prerequisites Checklist

- ✅ Specification approved and locked
- ✅ Constitution check passed (with documented deferral)
- ✅ Technical stack validated
- ✅ Project structure defined
- ✅ API contracts designed
- ✅ Data model designed
- ✅ Error handling strategy defined
- ✅ Testing strategy defined

### Next Steps

1. **Run `/sp.tasks`**: Generate detailed implementation tasks from this plan
2. **Use `neon-db-architect` agent**: Set up database schema and connection
3. **Use `fastapi-backend` agent**: Implement API endpoints and business logic
4. **Validate against spec**: Ensure all 18 functional requirements are met
5. **Run tests**: Verify all acceptance scenarios pass
6. **Generate documentation**: Create quickstart guide and API documentation

### Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Database connection issues with Neon | High | Test connection early, implement retry logic, use connection pooling |
| Timestamp management inconsistencies | Medium | Use ORM-level defaults, add integration tests for timestamp behavior |
| Validation errors not matching spec | Medium | Implement comprehensive test suite covering all edge cases |
| Performance degradation under load | Low | Use async FastAPI features, implement connection pooling, load test early |

## Success Validation

This implementation will be considered successful when:

1. ✅ All 6 API endpoints are functional and return correct responses
2. ✅ All 18 functional requirements from spec are implemented
3. ✅ All acceptance scenarios from user stories pass
4. ✅ Test coverage is ≥80%
5. ✅ API documentation is auto-generated and accessible
6. ✅ Database connection is stable and uses connection pooling
7. ✅ Error handling matches specification for all edge cases
8. ✅ Response times are <500ms for single operations
9. ✅ System handles 100+ concurrent requests without errors
10. ✅ Code is generated entirely through Claude Code agents (no manual edits)

---

**Plan Status**: ✅ **COMPLETE** - Ready for task generation (`/sp.tasks`)

**Approval**: This plan aligns with the feature specification and project constitution. Proceed to task breakdown phase.
