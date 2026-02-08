# Tasks API Contract

**Feature**: Frontend Full-Stack UI (004-frontend-fullstack-ui)
**Date**: 2026-02-05
**Backend Feature**: 001-backend-core-data

## Overview

This document defines the tasks API endpoints that the frontend will consume. All endpoints require authentication and enforce user isolation.

## Base URL

```
{NEXT_PUBLIC_API_URL}/api/users/{user_id}/tasks
```

## Authentication

All endpoints require JWT token in Authorization header:
```
Authorization: Bearer {token}
```

## Endpoints

### 1. List User Tasks

**Endpoint**: `GET /api/users/{user_id}/tasks`

**Description**: Get all tasks belonging to the authenticated user

**Path Parameters**:
- `user_id` (string, required): User ID (must match authenticated user)

**Query Parameters**: None

**Success Response** (200 OK):
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Complete project documentation",
    "description": "Write comprehensive docs for the new feature",
    "completed": false,
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "team_id": null,
    "created_at": "2026-02-05T10:30:00Z",
    "updated_at": "2026-02-05T10:30:00Z"
  },
  {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "title": "Review pull requests",
    "description": null,
    "completed": true,
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "team_id": null,
    "created_at": "2026-02-04T09:00:00Z",
    "updated_at": "2026-02-05T11:00:00Z"
  }
]
```

**Error Responses**:

401 Unauthorized:
```json
{
  "error": "Unauthorized",
  "detail": "Invalid or expired token"
}
```

403 Forbidden - User ID mismatch:
```json
{
  "error": "Access denied",
  "detail": "Cannot access tasks for another user"
}
```

---

### 2. Create Task

**Endpoint**: `POST /api/users/{user_id}/tasks`

**Description**: Create a new task for the authenticated user

**Path Parameters**:
- `user_id` (string, required): User ID (must match authenticated user)

**Request Body**:
```json
{
  "title": "Complete project documentation",
  "description": "Write comprehensive docs for the new feature",
  "team_id": null
}
```

**Request Schema**:
```typescript
{
  title: string           // Required, max 200 characters
  description?: string    // Optional
  team_id?: string        // Optional, for team tasks
}
```

**Success Response** (201 Created):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Complete project documentation",
  "description": "Write comprehensive docs for the new feature",
  "completed": false,
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "team_id": null,
  "created_at": "2026-02-05T10:30:00Z",
  "updated_at": "2026-02-05T10:30:00Z"
}
```

**Error Responses**:

400 Bad Request - Invalid input:
```json
{
  "error": "Invalid input",
  "detail": "Title is required and cannot be empty"
}
```

401 Unauthorized:
```json
{
  "error": "Unauthorized",
  "detail": "Invalid or expired token"
}
```

403 Forbidden:
```json
{
  "error": "Access denied",
  "detail": "Cannot create tasks for another user"
}
```

---

### 3. Get Task Details

**Endpoint**: `GET /api/users/{user_id}/tasks/{task_id}`

**Description**: Get details of a specific task

**Path Parameters**:
- `user_id` (string, required): User ID (must match authenticated user)
- `task_id` (string, required): Task ID

**Success Response** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Complete project documentation",
  "description": "Write comprehensive docs for the new feature",
  "completed": false,
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "team_id": null,
  "created_at": "2026-02-05T10:30:00Z",
  "updated_at": "2026-02-05T10:30:00Z"
}
```

**Error Responses**:

404 Not Found:
```json
{
  "error": "Task not found",
  "detail": "Task does not exist or you don't have access"
}
```

401 Unauthorized:
```json
{
  "error": "Unauthorized",
  "detail": "Invalid or expired token"
}
```

403 Forbidden:
```json
{
  "error": "Access denied",
  "detail": "Cannot access tasks for another user"
}
```

---

### 4. Update Task

**Endpoint**: `PUT /api/users/{user_id}/tasks/{task_id}`

**Description**: Update an existing task

**Path Parameters**:
- `user_id` (string, required): User ID (must match authenticated user)
- `task_id` (string, required): Task ID

**Request Body**:
```json
{
  "title": "Updated task title",
  "description": "Updated description",
  "completed": false
}
```

**Request Schema**:
```typescript
{
  title?: string        // Optional, max 200 characters
  description?: string  // Optional
  completed?: boolean   // Optional
}
```

**Note**: At least one field must be provided

**Success Response** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Updated task title",
  "description": "Updated description",
  "completed": false,
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "team_id": null,
  "created_at": "2026-02-05T10:30:00Z",
  "updated_at": "2026-02-05T12:00:00Z"
}
```

**Error Responses**:

400 Bad Request:
```json
{
  "error": "Invalid input",
  "detail": "At least one field must be provided"
}
```

404 Not Found:
```json
{
  "error": "Task not found",
  "detail": "Task does not exist or you don't have access"
}
```

401 Unauthorized:
```json
{
  "error": "Unauthorized",
  "detail": "Invalid or expired token"
}
```

403 Forbidden:
```json
{
  "error": "Access denied",
  "detail": "Cannot update tasks for another user"
}
```

---

### 5. Delete Task

**Endpoint**: `DELETE /api/users/{user_id}/tasks/{task_id}`

**Description**: Delete a task

**Path Parameters**:
- `user_id` (string, required): User ID (must match authenticated user)
- `task_id` (string, required): Task ID

**Success Response** (204 No Content):
No response body

**Error Responses**:

404 Not Found:
```json
{
  "error": "Task not found",
  "detail": "Task does not exist or you don't have access"
}
```

401 Unauthorized:
```json
{
  "error": "Unauthorized",
  "detail": "Invalid or expired token"
}
```

403 Forbidden:
```json
{
  "error": "Access denied",
  "detail": "Cannot delete tasks for another user"
}
```

---

### 6. Toggle Task Completion

**Endpoint**: `PATCH /api/users/{user_id}/tasks/{task_id}/toggle`

**Description**: Toggle the completion status of a task

**Path Parameters**:
- `user_id` (string, required): User ID (must match authenticated user)
- `task_id` (string, required): Task ID

**Request Body**: None

**Success Response** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Complete project documentation",
  "description": "Write comprehensive docs for the new feature",
  "completed": true,
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "team_id": null,
  "created_at": "2026-02-05T10:30:00Z",
  "updated_at": "2026-02-05T12:30:00Z"
}
```

**Error Responses**:

404 Not Found:
```json
{
  "error": "Task not found",
  "detail": "Task does not exist or you don't have access"
}
```

401 Unauthorized:
```json
{
  "error": "Unauthorized",
  "detail": "Invalid or expired token"
}
```

403 Forbidden:
```json
{
  "error": "Access denied",
  "detail": "Cannot toggle tasks for another user"
}
```

---

## Security & Validation

### User Isolation
- All endpoints enforce that `user_id` in path matches authenticated user ID from JWT token
- Backend filters all queries by authenticated user ID
- Cross-user access attempts return 403 Forbidden

### Input Validation
- Title: Required, non-empty, max 200 characters
- Description: Optional, max 1000 characters
- Task ID: Must be valid UUID format
- User ID: Must be valid UUID format

### Rate Limiting
- Backend implements rate limiting per user
- Typical limit: 100 requests per minute per user

## Frontend Implementation Example

```typescript
// lib/api/tasks.ts
import { apiClient } from './client'
import type { Task, CreateTaskInput, UpdateTaskInput } from '@/lib/types'

export async function getTasks(userId: string): Promise<Task[]> {
  return apiClient<Task[]>(`/api/users/${userId}/tasks`)
}

export async function createTask(userId: string, data: CreateTaskInput): Promise<Task> {
  return apiClient<Task>(`/api/users/${userId}/tasks`, {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function getTask(userId: string, taskId: string): Promise<Task> {
  return apiClient<Task>(`/api/users/${userId}/tasks/${taskId}`)
}

export async function updateTask(
  userId: string,
  taskId: string,
  data: UpdateTaskInput
): Promise<Task> {
  return apiClient<Task>(`/api/users/${userId}/tasks/${taskId}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}

export async function deleteTask(userId: string, taskId: string): Promise<void> {
  await apiClient(`/api/users/${userId}/tasks/${taskId}`, {
    method: 'DELETE',
  })
}

export async function toggleTask(userId: string, taskId: string): Promise<Task> {
  return apiClient<Task>(`/api/users/${userId}/tasks/${taskId}/toggle`, {
    method: 'PATCH',
  })
}
```

## Testing Checklist

- [ ] List tasks returns only authenticated user's tasks
- [ ] Create task with valid data succeeds
- [ ] Create task with empty title fails with 400
- [ ] Get task details for owned task succeeds
- [ ] Get task details for non-existent task fails with 404
- [ ] Update task with valid data succeeds
- [ ] Update task with no fields fails with 400
- [ ] Delete task succeeds and returns 204
- [ ] Toggle task changes completion status
- [ ] All endpoints reject requests without JWT token (401)
- [ ] All endpoints reject requests with mismatched user_id (403)
- [ ] Completed tasks display with appropriate styling
- [ ] Task list updates after create/update/delete operations
