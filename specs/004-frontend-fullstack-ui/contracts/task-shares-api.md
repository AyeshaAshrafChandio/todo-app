# Task Shares API Contract

**Feature**: Frontend Full-Stack UI (004-frontend-fullstack-ui)
**Date**: 2026-02-05
**Backend Feature**: 003-roles-teams-and-task-sharing

## Overview

This document defines the task sharing API endpoints that the frontend will consume. These endpoints enable users to share tasks with other users with specific permission levels.

## Base URL

```
{NEXT_PUBLIC_API_URL}/api/task-shares
```

## Authentication

All endpoints require JWT token in Authorization header:
```
Authorization: Bearer {token}
```

## Endpoints

### 1. List Shared Tasks

**Endpoint**: `GET /api/task-shares`

**Description**: Get all tasks shared with the authenticated user

**Query Parameters**: None

**Success Response** (200 OK):
```json
[
  {
    "id": "share-id-1",
    "task_id": "task-id-1",
    "shared_with_user_id": "current-user-id",
    "permission": "edit",
    "shared_at": "2026-02-05T10:00:00Z",
    "task": {
      "id": "task-id-1",
      "title": "Review design mockups",
      "description": "Provide feedback on new UI designs",
      "completed": false,
      "user_id": "owner-user-id",
      "team_id": null,
      "created_at": "2026-02-04T14:00:00Z",
      "updated_at": "2026-02-04T14:00:00Z"
    },
    "shared_with_user": {
      "id": "current-user-id",
      "email": "currentuser@example.com",
      "created_at": "2026-01-15T09:00:00Z"
    }
  },
  {
    "id": "share-id-2",
    "task_id": "task-id-2",
    "shared_with_user_id": "current-user-id",
    "permission": "view",
    "shared_at": "2026-02-03T11:30:00Z",
    "task": {
      "id": "task-id-2",
      "title": "Project roadmap",
      "description": "Q1 2026 roadmap",
      "completed": false,
      "user_id": "owner-user-id-2",
      "team_id": null,
      "created_at": "2026-02-01T10:00:00Z",
      "updated_at": "2026-02-03T09:00:00Z"
    },
    "shared_with_user": {
      "id": "current-user-id",
      "email": "currentuser@example.com",
      "created_at": "2026-01-15T09:00:00Z"
    }
  }
]
```

**Response Schema**:
```typescript
Array<{
  id: string
  task_id: string
  shared_with_user_id: string
  permission: 'view' | 'edit'
  shared_at: string
  task: {
    id: string
    title: string
    description: string | null
    completed: boolean
    user_id: string
    team_id: string | null
    created_at: string
    updated_at: string
  }
  shared_with_user: {
    id: string
    email: string
    created_at: string
  }
}>
```

**Error Responses**:

401 Unauthorized:
```json
{
  "error": "Unauthorized",
  "detail": "Invalid or expired token"
}
```

---

### 2. Share Task

**Endpoint**: `POST /api/task-shares`

**Description**: Share a task with another user (requires task ownership)

**Request Body**:
```json
{
  "task_id": "task-id-1",
  "shared_with_user_email": "colleague@example.com",
  "permission": "edit"
}
```

**Request Schema**:
```typescript
{
  task_id: string                    // Required, must be owned by authenticated user
  shared_with_user_email: string     // Required, valid email
  permission: 'view' | 'edit'        // Required
}
```

**Success Response** (201 Created):
```json
{
  "id": "share-id-3",
  "task_id": "task-id-1",
  "shared_with_user_id": "user-id-3",
  "permission": "edit",
  "shared_at": "2026-02-05T12:00:00Z",
  "task": {
    "id": "task-id-1",
    "title": "Review design mockups",
    "description": "Provide feedback on new UI designs",
    "completed": false,
    "user_id": "current-user-id",
    "team_id": null,
    "created_at": "2026-02-04T14:00:00Z",
    "updated_at": "2026-02-04T14:00:00Z"
  },
  "shared_with_user": {
    "id": "user-id-3",
    "email": "colleague@example.com",
    "created_at": "2026-01-20T10:00:00Z"
  }
}
```

**Error Responses**:

400 Bad Request - Invalid input:
```json
{
  "error": "Invalid input",
  "detail": "Task ID and user email are required"
}
```

404 Not Found - Task not found:
```json
{
  "error": "Task not found",
  "detail": "Task does not exist or you don't own it"
}
```

404 Not Found - User not found:
```json
{
  "error": "User not found",
  "detail": "No user exists with this email"
}
```

409 Conflict - Already shared:
```json
{
  "error": "Task already shared",
  "detail": "This task is already shared with this user"
}
```

401 Unauthorized:
```json
{
  "error": "Unauthorized",
  "detail": "Invalid or expired token"
}
```

403 Forbidden - Not task owner:
```json
{
  "error": "Access denied",
  "detail": "Only task owners can share tasks"
}
```

---

### 3. Revoke Task Share

**Endpoint**: `DELETE /api/task-shares/{share_id}`

**Description**: Revoke access to a shared task (requires task ownership)

**Path Parameters**:
- `share_id` (string, required): Task share ID

**Success Response** (204 No Content):
No response body

**Error Responses**:

404 Not Found:
```json
{
  "error": "Share not found",
  "detail": "Task share does not exist or you don't own the task"
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
  "detail": "Only task owners can revoke shares"
}
```

---

## Permission Levels

### View Permission
- User can see the task in their shared tasks list
- User can view task title, description, and completion status
- User **cannot** edit task details
- User **cannot** toggle completion status
- User **cannot** delete the task
- User **cannot** share the task with others

### Edit Permission
- User can see the task in their shared tasks list
- User can view task title, description, and completion status
- User **can** edit task title and description
- User **can** toggle completion status
- User **cannot** delete the task (only owner can delete)
- User **cannot** share the task with others (only owner can share)

## Frontend Implementation

### Permission-Based UI Controls

```typescript
function canEditSharedTask(permission: PermissionLevel): boolean {
  return permission === 'edit'
}

function canViewSharedTask(permission: PermissionLevel): boolean {
  return permission === 'view' || permission === 'edit'
}

// Example usage in component
<TaskCard
  task={sharedTask.task}
  onEdit={canEditSharedTask(sharedTask.permission) ? handleEdit : undefined}
  onToggle={canEditSharedTask(sharedTask.permission) ? handleToggle : undefined}
  onDelete={undefined} // Never allow delete for shared tasks
  disabled={!canEditSharedTask(sharedTask.permission)}
/>
```

### Displaying Shared Tasks

Shared tasks should be clearly distinguished from owned tasks:
- Display permission badge (View/Edit)
- Show original owner's email
- Disable actions based on permission level
- Indicate that task is shared (icon or label)

## Security & Validation

### Access Control
- Only task owners can share tasks
- Only task owners can revoke shares
- Users can only view tasks shared with them
- Backend enforces all permission checks

### Input Validation
- Task ID: Must be valid UUID format
- User email: Must be valid email format
- Permission: Must be 'view' or 'edit'
- Share ID: Must be valid UUID format

### Business Rules
- Cannot share task with yourself
- Cannot share same task with same user twice
- Cannot share team tasks (team membership controls access)
- Deleting a task automatically deletes all shares

## Frontend Implementation Example

```typescript
// lib/api/shares.ts
import { apiClient } from './client'
import type {
  TaskShareResponse,
  CreateTaskShareInput
} from '@/lib/types'

export async function getSharedTasks(): Promise<TaskShareResponse[]> {
  return apiClient<TaskShareResponse[]>('/api/task-shares')
}

export async function shareTask(
  data: CreateTaskShareInput
): Promise<TaskShareResponse> {
  return apiClient<TaskShareResponse>('/api/task-shares', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function revokeShare(shareId: string): Promise<void> {
  await apiClient(`/api/task-shares/${shareId}`, {
    method: 'DELETE',
  })
}
```

## UI Components

### SharedTaskList Component

```typescript
interface SharedTaskListProps {
  shares: TaskShareResponse[]
  onEdit?: (taskId: string) => void
  onToggle?: (taskId: string) => void
}

export function SharedTaskList({ shares, onEdit, onToggle }: SharedTaskListProps) {
  return (
    <div>
      {shares.map(share => (
        <div key={share.id}>
          <TaskCard
            task={share.task}
            onEdit={share.permission === 'edit' ? onEdit : undefined}
            onToggle={share.permission === 'edit' ? onToggle : undefined}
            disabled={share.permission === 'view'}
          />
          <PermissionBadge permission={share.permission} />
          <span>Shared by: {share.task.user_id}</span>
        </div>
      ))}
    </div>
  )
}
```

### ShareTaskModal Component

```typescript
interface ShareTaskModalProps {
  taskId: string
  onClose: () => void
  onSuccess: () => void
}

export function ShareTaskModal({ taskId, onClose, onSuccess }: ShareTaskModalProps) {
  const [email, setEmail] = useState('')
  const [permission, setPermission] = useState<PermissionLevel>('view')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      await shareTask({
        task_id: taskId,
        shared_with_user_email: email,
        permission,
      })
      onSuccess()
      onClose()
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Modal onClose={onClose}>
      <form onSubmit={handleSubmit}>
        <Input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="colleague@example.com"
          required
        />
        <select
          value={permission}
          onChange={(e) => setPermission(e.target.value as PermissionLevel)}
        >
          <option value="view">View only</option>
          <option value="edit">Can edit</option>
        </select>
        {error && <Alert type="error">{error}</Alert>}
        <Button type="submit" disabled={loading}>
          {loading ? 'Sharing...' : 'Share Task'}
        </Button>
      </form>
    </Modal>
  )
}
```

## Testing Checklist

- [ ] List shared tasks returns only tasks shared with authenticated user
- [ ] Share task with valid email and permission succeeds
- [ ] Share task with invalid email fails with 404
- [ ] Share task not owned by user fails with 403
- [ ] Share same task with same user twice fails with 409
- [ ] Revoke share succeeds and returns 204
- [ ] Revoke share for non-owned task fails with 403
- [ ] View permission disables edit/toggle actions in UI
- [ ] Edit permission enables edit/toggle actions in UI
- [ ] Delete action always disabled for shared tasks
- [ ] Permission badges display correctly
- [ ] Shared tasks clearly distinguished from owned tasks
- [ ] All endpoints reject requests without JWT token (401)

## Notes

- Task sharing is independent of team membership
- Shared tasks appear in a separate section on the dashboard
- Original task owner retains full control (edit, delete, share, revoke)
- Shared task permissions do not cascade (sharing with A doesn't let A share with B)
- Deleting a task automatically removes all shares
