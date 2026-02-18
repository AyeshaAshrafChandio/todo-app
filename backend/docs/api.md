# API Documentation - Todo Backend

**Version**: 0.1.0
**Base URL**: `http://localhost:8000`
**Authentication**: JWT Bearer Token

---

## Table of Contents

1. [Authentication](#authentication)
2. [Tasks API](#tasks-api)
3. [Teams API](#teams-api)
4. [Team Members API](#team-members-api)
5. [Task Sharing API](#task-sharing-api)
6. [Dashboard API](#dashboard-api)
7. [Chat API](#chat-api)
8. [Error Codes](#error-codes)
9. [Rate Limiting](#rate-limiting)

---

## Authentication

All API endpoints (except `/api/auth/*`) require JWT authentication via the `Authorization` header.

### Header Format
```
Authorization: Bearer <jwt_token>
```

### Authentication Endpoints

#### POST /api/auth/signup
Create a new user account.

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "name": "John Doe"
}
```

**Response** (201 Created):
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "John Doe",
  "created_at": "2026-02-07T20:00:00Z"
}
```

**Error Responses**:
- `400 Bad Request`: Invalid email format or password too short
- `409 Conflict`: Email already registered

---

#### POST /api/auth/signin
Authenticate and receive JWT token.

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

**Error Responses**:
- `401 Unauthorized`: Invalid credentials
- `404 Not Found`: User not found

---

## Tasks API

### GET /api/{user_id}/tasks
Get all tasks for authenticated user.

**Path Parameters**:
- `user_id` (integer): User ID (must match authenticated user)

**Query Parameters**:
- `status` (string, optional): Filter by status (`pending`, `completed`)
- `limit` (integer, optional): Maximum number of tasks (default: 100)
- `offset` (integer, optional): Pagination offset (default: 0)

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "user_id": 1,
    "title": "Complete project documentation",
    "description": "Write comprehensive API docs",
    "status": "pending",
    "created_at": "2026-02-07T10:00:00Z",
    "updated_at": "2026-02-07T10:00:00Z"
  }
]
```

**Error Responses**:
- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: User ID mismatch

---

### POST /api/{user_id}/tasks
Create a new task.

**Path Parameters**:
- `user_id` (integer): User ID (must match authenticated user)

**Request Body**:
```json
{
  "title": "New task title",
  "description": "Task description (optional)",
  "status": "pending"
}
```

**Response** (201 Created):
```json
{
  "id": 2,
  "user_id": 1,
  "title": "New task title",
  "description": "Task description (optional)",
  "status": "pending",
  "created_at": "2026-02-07T11:00:00Z",
  "updated_at": "2026-02-07T11:00:00Z"
}
```

**Error Responses**:
- `400 Bad Request`: Invalid request body
- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: User ID mismatch

---

### GET /api/{user_id}/tasks/{task_id}
Get a specific task by ID.

**Path Parameters**:
- `user_id` (integer): User ID
- `task_id` (integer): Task ID

**Response** (200 OK):
```json
{
  "id": 1,
  "user_id": 1,
  "title": "Complete project documentation",
  "description": "Write comprehensive API docs",
  "status": "pending",
  "created_at": "2026-02-07T10:00:00Z",
  "updated_at": "2026-02-07T10:00:00Z"
}
```

**Error Responses**:
- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: User doesn't have access to this task
- `404 Not Found`: Task not found

---

### PUT /api/{user_id}/tasks/{task_id}
Update an existing task.

**Path Parameters**:
- `user_id` (integer): User ID
- `task_id` (integer): Task ID

**Request Body**:
```json
{
  "title": "Updated task title",
  "description": "Updated description",
  "status": "completed"
}
```

**Response** (200 OK):
```json
{
  "id": 1,
  "user_id": 1,
  "title": "Updated task title",
  "description": "Updated description",
  "status": "completed",
  "created_at": "2026-02-07T10:00:00Z",
  "updated_at": "2026-02-07T12:00:00Z"
}
```

**Error Responses**:
- `400 Bad Request`: Invalid request body
- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: User doesn't have permission to update
- `404 Not Found`: Task not found

---

### DELETE /api/{user_id}/tasks/{task_id}
Delete a task.

**Path Parameters**:
- `user_id` (integer): User ID
- `task_id` (integer): Task ID

**Response** (204 No Content)

**Error Responses**:
- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: User doesn't have permission to delete
- `404 Not Found`: Task not found

---

## Teams API

### GET /api/teams
Get all teams for authenticated user.

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "name": "Development Team",
    "owner_id": 1,
    "created_at": "2026-02-07T09:00:00Z",
    "updated_at": "2026-02-07T09:00:00Z"
  }
]
```

---

### POST /api/teams
Create a new team.

**Request Body**:
```json
{
  "name": "Marketing Team"
}
```

**Response** (201 Created):
```json
{
  "id": 2,
  "name": "Marketing Team",
  "owner_id": 1,
  "created_at": "2026-02-07T13:00:00Z",
  "updated_at": "2026-02-07T13:00:00Z"
}
```

---

### GET /api/teams/{team_id}
Get team details.

**Path Parameters**:
- `team_id` (integer): Team ID

**Response** (200 OK):
```json
{
  "id": 1,
  "name": "Development Team",
  "owner_id": 1,
  "created_at": "2026-02-07T09:00:00Z",
  "updated_at": "2026-02-07T09:00:00Z"
}
```

---

## Dashboard API

### GET /api/dashboard/statistics
Get task statistics for authenticated user.

**Response** (200 OK):
```json
{
  "statistics": {
    "total_tasks": 15,
    "pending_tasks": 8,
    "completed_tasks": 7,
    "shared_tasks": 3
  },
  "computed_at": "2026-02-07T20:30:00Z",
  "cached": false
}
```

**Performance**: Optimized with COUNT queries. Expected response time: <50ms

---

### GET /api/dashboard/activity
Get activity metrics for authenticated user.

**Response** (200 OK):
```json
{
  "tasks_created_today": 2,
  "tasks_completed_today": 3,
  "tasks_created_this_week": 8,
  "tasks_completed_this_week": 12,
  "completion_rate": 60.5
}
```

---

### GET /api/dashboard/breakdown
Get task breakdown by status.

**Response** (200 OK):
```json
{
  "pending": 8,
  "completed": 7,
  "total": 15
}
```

---

### GET /api/dashboard/shared
Get shared task details.

**Response** (200 OK):
```json
{
  "total_shared": 5,
  "view_only": 3,
  "can_edit": 2
}
```

---

## Chat API

### POST /api/chat/conversations
Create a new conversation.

**Request Body**:
```json
{
  "title": "Project Planning Discussion"
}
```

**Response** (201 Created):
```json
{
  "id": 1,
  "user_id": 1,
  "title": "Project Planning Discussion",
  "created_at": "2026-02-07T14:00:00Z",
  "updated_at": "2026-02-07T14:00:00Z"
}
```

---

### POST /api/chat/conversations/{conversation_id}/messages
Send a message in a conversation.

**Path Parameters**:
- `conversation_id` (integer): Conversation ID

**Request Body**:
```json
{
  "content": "What tasks do I have pending?"
}
```

**Response** (200 OK):
```json
{
  "user_message": {
    "id": 1,
    "conversation_id": 1,
    "role": "user",
    "content": "What tasks do I have pending?",
    "created_at": "2026-02-07T14:05:00Z"
  },
  "assistant_message": {
    "id": 2,
    "conversation_id": 1,
    "role": "assistant",
    "content": "You have 8 pending tasks...",
    "created_at": "2026-02-07T14:05:01Z"
  }
}
```

---

## Error Codes

All error responses follow this format:

```json
{
  "error": "Error Type",
  "detail": "Detailed error message",
  "code": "ERROR_CODE"
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `UNAUTHORIZED` | 401 | Missing or invalid authentication token |
| `FORBIDDEN` | 403 | User doesn't have permission for this resource |
| `NOT_FOUND` | 404 | Resource not found |
| `VALIDATION_ERROR` | 422 | Request validation failed |
| `INTERNAL_ERROR` | 500 | Internal server error |
| `DATABASE_ERROR` | 500 | Database operation failed |

---

## Rate Limiting

**Current Status**: Not implemented (planned for future release)

**Planned Limits**:
- 100 requests per minute per user
- 1000 requests per hour per user
- Burst allowance: 20 requests

**Rate Limit Headers** (future):
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1675789200
```

---

## Performance Headers

All responses include performance headers:

```
X-Response-Time: 0.045s
```

---

## OpenAPI Documentation

Interactive API documentation is available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

## Best Practices

### Authentication
- Always include the `Authorization` header with valid JWT token
- Tokens expire after 24 hours (configurable)
- Store tokens securely (never in localStorage for production)

### Error Handling
- Check HTTP status codes before parsing response
- Handle 401 errors by redirecting to login
- Implement retry logic for 5xx errors

### Performance
- Use pagination for large result sets
- Cache dashboard statistics on client side
- Implement request debouncing for real-time updates

### Security
- Never expose JWT tokens in URLs
- Validate user_id matches authenticated user
- Use HTTPS in production

---

## Support

For issues or questions:
- GitHub Issues: [Repository URL]
- Email: support@example.com
- Documentation: http://localhost:8000/docs
