# Feature Specification: Todo Backend Core & Data Layer

**Feature Branch**: `001-backend-core-data`
**Created**: 2026-01-20
**Status**: Draft
**Input**: User description: "Todo Full-Stack Web Application — Spec 1 (Backend Core & Data Layer): Building a production-ready FastAPI backend with persistent PostgreSQL storage, implementing all core Todo logic and REST APIs without authentication enforcement (authentication will be added in Spec-2)."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create and Retrieve Tasks (Priority: P1)

As an API consumer (frontend developer), I need to create new tasks and retrieve all tasks for a user so that I can build the basic todo list interface.

**Why this priority**: This is the foundational functionality - without the ability to create and view tasks, no other features can be demonstrated or tested. This represents the minimum viable backend.

**Independent Test**: Can be fully tested by making POST requests to create tasks and GET requests to retrieve them, verifying data persistence across requests.

**Acceptance Scenarios**:

1. **Given** no existing tasks for user_id "user123", **When** I POST a new task with title "Buy groceries" to `/api/user123/tasks`, **Then** the API returns 201 status with the created task including auto-generated id and timestamps
2. **Given** three tasks exist for user_id "user123", **When** I GET `/api/user123/tasks`, **Then** the API returns 200 status with an array of all three tasks in JSON format
3. **Given** a task exists with id 5 for user_id "user123", **When** I GET `/api/user123/tasks/5`, **Then** the API returns 200 status with the complete task details

---

### User Story 2 - Update and Delete Tasks (Priority: P2)

As an API consumer, I need to update existing task details and delete tasks so that users can modify their todo list.

**Why this priority**: Once basic create/read works, users need to manage their tasks. This builds on P1 functionality and enables a complete CRUD experience.

**Independent Test**: Can be tested independently by first creating a task (using P1 functionality), then updating its properties and verifying changes persist, and finally deleting it and confirming removal.

**Acceptance Scenarios**:

1. **Given** a task with id 5 exists for user_id "user123" with title "Old Title", **When** I PUT to `/api/user123/tasks/5` with title "New Title" and description "Updated description", **Then** the API returns 200 status with the updated task and updated_at timestamp is refreshed
2. **Given** a task with id 5 exists for user_id "user123", **When** I DELETE `/api/user123/tasks/5`, **Then** the API returns 204 status and subsequent GET requests for that task return 404
3. **Given** I update a task, **When** I retrieve it again, **Then** the changes are persisted in the database and returned correctly

---

### User Story 3 - Toggle Task Completion (Priority: P3)

As an API consumer, I need a dedicated endpoint to toggle task completion status so that users can mark tasks as done or undone with a single action.

**Why this priority**: This is a convenience feature that enhances UX but isn't essential for basic CRUD. The same result could be achieved with PUT, but a dedicated endpoint provides better semantics.

**Independent Test**: Can be tested by creating a task (P1), then using the PATCH endpoint to toggle completion status multiple times, verifying the boolean state changes correctly.

**Acceptance Scenarios**:

1. **Given** a task with id 5 exists for user_id "user123" with completed=false, **When** I PATCH `/api/user123/tasks/5/complete`, **Then** the API returns 200 status with completed=true and updated_at timestamp is refreshed
2. **Given** a task with id 5 exists with completed=true, **When** I PATCH `/api/user123/tasks/5/complete`, **Then** the API returns 200 status with completed=false (toggle behavior)
3. **Given** the completion status is toggled, **When** I retrieve the task, **Then** the new completion status is persisted

---

### Edge Cases

- What happens when a client requests a task ID that doesn't exist? (Expected: 404 Not Found)
- What happens when a client provides invalid data (missing required title, invalid user_id format)? (Expected: 422 Unprocessable Entity with validation errors)
- What happens when a client tries to create a task with an empty title? (Expected: 422 validation error)
- What happens when database connection fails during a request? (Expected: 500 Internal Server Error with appropriate error message)
- What happens when a client requests tasks for a user_id that has no tasks? (Expected: 200 OK with empty array)
- What happens when a client sends malformed JSON? (Expected: 400 Bad Request)
- What happens when updated_at and created_at timestamps need to be managed? (Expected: System automatically sets created_at on creation, updated_at on creation and updates)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a REST API endpoint to create new tasks with title (required), description (optional), and user_id
- **FR-002**: System MUST auto-generate unique task IDs when creating tasks
- **FR-003**: System MUST auto-generate created_at and updated_at timestamps when creating tasks
- **FR-004**: System MUST persist all task data to PostgreSQL database using SQLModel ORM
- **FR-005**: System MUST provide an endpoint to retrieve all tasks for a specific user_id
- **FR-006**: System MUST provide an endpoint to retrieve a single task by its ID and user_id
- **FR-007**: System MUST provide an endpoint to update task title, description, and completed status
- **FR-008**: System MUST update the updated_at timestamp whenever a task is modified
- **FR-009**: System MUST provide an endpoint to delete tasks by ID and user_id
- **FR-010**: System MUST provide a dedicated endpoint to toggle task completion status
- **FR-011**: System MUST validate that task title is not empty or null
- **FR-012**: System MUST return appropriate HTTP status codes (200, 201, 204, 404, 422, 500)
- **FR-013**: System MUST return consistent JSON response format for all endpoints
- **FR-014**: System MUST handle database connection errors gracefully with appropriate error messages
- **FR-015**: System MUST initialize completed status as false when creating new tasks
- **FR-016**: System MUST accept user_id as a path parameter (placeholder only, no validation or enforcement)
- **FR-017**: System MUST return 404 when requesting non-existent task IDs
- **FR-018**: System MUST return validation errors in a structured format when request data is invalid

### Key Entities

- **Task**: Represents a todo item with the following attributes:
  - id: Unique identifier (auto-generated integer)
  - title: Task name/description (required, non-empty string)
  - description: Optional detailed description (nullable string)
  - completed: Boolean flag indicating completion status (defaults to false)
  - created_at: Timestamp when task was created (auto-generated)
  - updated_at: Timestamp when task was last modified (auto-generated and auto-updated)
  - user_id: String identifier for the user who owns the task (placeholder, no enforcement)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: API consumers can create a new task and receive a response in under 500ms under normal load
- **SC-002**: All task data persists correctly across server restarts, with 100% data integrity
- **SC-003**: API returns correct HTTP status codes for all scenarios (success, not found, validation errors, server errors)
- **SC-004**: All six required API endpoints are functional and return consistent JSON responses
- **SC-005**: Task completion toggle works correctly, alternating between true and false states
- **SC-006**: Database connection is established successfully on application startup
- **SC-007**: Invalid requests (missing title, malformed JSON) return appropriate 4xx errors with helpful error messages
- **SC-008**: System handles at least 100 concurrent API requests without data corruption or errors
- **SC-009**: Timestamps (created_at, updated_at) are automatically managed without manual intervention
- **SC-010**: API documentation is auto-generated and accessible (FastAPI's built-in Swagger UI)

## Scope *(mandatory)*

### In Scope

- FastAPI application setup with proper project structure
- Database connection management to Neon Serverless PostgreSQL
- SQLModel schema definition for Task entity
- Six REST API endpoints for task CRUD operations:
  - GET /api/{user_id}/tasks (list all tasks)
  - POST /api/{user_id}/tasks (create task)
  - GET /api/{user_id}/tasks/{id} (get single task)
  - PUT /api/{user_id}/tasks/{id} (update task)
  - DELETE /api/{user_id}/tasks/{id} (delete task)
  - PATCH /api/{user_id}/tasks/{id}/complete (toggle completion)
- Request/response validation using Pydantic models
- Basic error handling for common scenarios (404, 422, 500)
- Automatic timestamp management (created_at, updated_at)
- Database session management and connection pooling

### Out of Scope

- User authentication or JWT token verification
- User signup, signin, or session management
- Authorization checks or user_id validation
- Frontend UI components
- Rate limiting or advanced API security
- Role-based access control (RBAC)
- API versioning strategy
- Deployment configuration or CI/CD pipelines
- Comprehensive logging and monitoring
- Task filtering, sorting, or pagination
- Task categories, tags, or priorities
- Task due dates or reminders
- Multi-user collaboration features

## Assumptions *(mandatory)*

1. **Database Availability**: Neon Serverless PostgreSQL instance is provisioned and connection string is available in environment variables
2. **Environment Configuration**: Database credentials and connection details will be provided via .env file
3. **Python Version**: Python 3.10+ is available in the development environment
4. **Package Management**: pip or poetry is available for dependency installation
5. **Development Workflow**: All code will be generated via Claude Code following the agentic workflow (spec → plan → tasks → implementation)
6. **API Consumers**: The primary consumers of this API will be frontend developers building the UI in a subsequent phase
7. **User ID Format**: user_id is treated as an opaque string identifier; no specific format validation is required in this phase
8. **Single Database**: All tasks are stored in a single PostgreSQL database; no sharding or multi-tenancy concerns
9. **Synchronous Operations**: All API operations are synchronous; no async task queues or background jobs
10. **Error Responses**: Standard FastAPI error response format is acceptable; no custom error response schema required

## Dependencies *(mandatory)*

### External Dependencies

- **Neon Serverless PostgreSQL**: Cloud database service for persistent storage
- **Python 3.10+**: Runtime environment
- **FastAPI**: Web framework for building the REST API
- **SQLModel**: ORM for database operations (combines SQLAlchemy and Pydantic)
- **Uvicorn**: ASGI server for running FastAPI application
- **Pydantic**: Data validation library (included with FastAPI)
- **python-dotenv**: Environment variable management

### Internal Dependencies

- None (this is the first feature/spec in the project)

### Blocking Dependencies

- Database connection string from Neon must be available before implementation can begin
- Python environment must be set up with required packages

## Non-Functional Requirements *(optional)*

### Performance

- API response time under 500ms for single task operations under normal load
- Support for at least 100 concurrent requests without degradation
- Database connection pooling to handle multiple simultaneous requests efficiently

### Reliability

- Graceful error handling for database connection failures
- Automatic timestamp management to prevent data inconsistencies
- Transaction support to ensure data integrity during updates

### Maintainability

- Clear separation between API routes, database models, and business logic
- Consistent code structure following FastAPI best practices
- Auto-generated API documentation via FastAPI's Swagger UI

### Security

- Input validation for all request payloads
- SQL injection prevention via SQLModel's parameterized queries
- No sensitive data in error messages returned to clients

## Open Questions *(optional)*

None - all requirements are sufficiently specified for implementation.

## API Contract *(mandatory for API features)*

### Endpoint Specifications

#### 1. Create Task
- **Method**: POST
- **Path**: `/api/{user_id}/tasks`
- **Request Body**:
  ```json
  {
    "title": "string (required, non-empty)",
    "description": "string (optional, nullable)"
  }
  ```
- **Success Response**: 201 Created
  ```json
  {
    "id": 1,
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": false,
    "created_at": "2026-01-20T10:30:00Z",
    "updated_at": "2026-01-20T10:30:00Z",
    "user_id": "user123"
  }
  ```
- **Error Responses**:
  - 422 Unprocessable Entity: Invalid request data (missing title, empty title)

#### 2. List All Tasks
- **Method**: GET
- **Path**: `/api/{user_id}/tasks`
- **Success Response**: 200 OK
  ```json
  [
    {
      "id": 1,
      "title": "Buy groceries",
      "description": "Milk, eggs, bread",
      "completed": false,
      "created_at": "2026-01-20T10:30:00Z",
      "updated_at": "2026-01-20T10:30:00Z",
      "user_id": "user123"
    }
  ]
  ```
- **Note**: Returns empty array if no tasks exist for user_id

#### 3. Get Single Task
- **Method**: GET
- **Path**: `/api/{user_id}/tasks/{id}`
- **Success Response**: 200 OK (same structure as create response)
- **Error Responses**:
  - 404 Not Found: Task with specified ID does not exist

#### 4. Update Task
- **Method**: PUT
- **Path**: `/api/{user_id}/tasks/{id}`
- **Request Body**:
  ```json
  {
    "title": "string (required, non-empty)",
    "description": "string (optional, nullable)",
    "completed": "boolean (optional)"
  }
  ```
- **Success Response**: 200 OK (returns updated task with refreshed updated_at)
- **Error Responses**:
  - 404 Not Found: Task does not exist
  - 422 Unprocessable Entity: Invalid request data

#### 5. Delete Task
- **Method**: DELETE
- **Path**: `/api/{user_id}/tasks/{id}`
- **Success Response**: 204 No Content
- **Error Responses**:
  - 404 Not Found: Task does not exist

#### 6. Toggle Task Completion
- **Method**: PATCH
- **Path**: `/api/{user_id}/tasks/{id}/complete`
- **Request Body**: None
- **Success Response**: 200 OK (returns task with toggled completed status and refreshed updated_at)
- **Error Responses**:
  - 404 Not Found: Task does not exist

### Common Error Response Format
```json
{
  "detail": "Error message describing what went wrong"
}
```

For validation errors (422):
```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```
