# Frontend Data Model

**Feature**: Frontend Full-Stack UI (004-frontend-fullstack-ui)
**Date**: 2026-02-05
**Phase**: Phase 1 - Design

## Overview

This document defines all TypeScript types and interfaces used in the frontend application. These types match the backend schemas and provide type safety for API interactions.

## Core Entity Types

### User

Represents an authenticated user in the system.

```typescript
export interface User {
  id: string
  email: string
  created_at: string // ISO 8601 timestamp
}
```

**Usage**: Authentication state, task ownership, team membership

### Task

Represents a todo item that can be personal or team-based.

```typescript
export interface Task {
  id: string
  title: string
  description: string | null
  completed: boolean
  user_id: string
  team_id: string | null
  created_at: string // ISO 8601 timestamp
  updated_at: string // ISO 8601 timestamp
}
```

**Usage**: Task lists, task detail pages, CRUD operations

### Team

Represents a collaborative group of users.

```typescript
export interface Team {
  id: string
  name: string
  created_at: string // ISO 8601 timestamp
}
```

**Usage**: Team lists, team detail pages

### TeamMember

Represents a user's membership in a team with a specific role.

```typescript
export type TeamRole = 'owner' | 'admin' | 'member' | 'viewer'

export interface TeamMember {
  id: string
  team_id: string
  user_id: string
  role: TeamRole
  joined_at: string // ISO 8601 timestamp
}
```

**Usage**: Member lists, role-based UI controls

### TaskShare

Represents a task shared with another user with specific permissions.

```typescript
export type PermissionLevel = 'view' | 'edit'

export interface TaskShare {
  id: string
  task_id: string
  shared_with_user_id: string
  permission: PermissionLevel
  shared_at: string // ISO 8601 timestamp
}
```

**Usage**: Shared task lists, task sharing UI

## API Response Types

### AuthResponse

Response from authentication endpoints (signup, signin).

```typescript
export interface AuthResponse {
  token: string
  user: User
}
```

**Endpoints**: POST /api/auth/signup, POST /api/auth/signin

### SessionResponse

Response from session validation endpoint.

```typescript
export interface SessionResponse {
  user: User
  expires_at: string // ISO 8601 timestamp
}
```

**Endpoints**: GET /api/auth/session

### TaskResponse

Extended task information with optional owner and team details.

```typescript
export interface TaskResponse extends Task {
  owner?: User
  team?: Team
  shared_with_count?: number
}
```

**Endpoints**: GET /api/users/{user_id}/tasks/{task_id}

### TeamResponse

Extended team information with member count.

```typescript
export interface TeamResponse extends Team {
  member_count: number
  user_role: TeamRole // Current user's role in this team
}
```

**Endpoints**: GET /api/teams, GET /api/teams/{team_id}

### TeamMemberResponse

Extended team member information with user details.

```typescript
export interface TeamMemberResponse extends TeamMember {
  user: User
}
```

**Endpoints**: GET /api/teams/{team_id}/members

### TaskShareResponse

Extended task share information with user and task details.

```typescript
export interface TaskShareResponse extends TaskShare {
  task: Task
  shared_with_user: User
}
```

**Endpoints**: GET /api/task-shares

### ErrorResponse

Standard error response from API.

```typescript
export interface ErrorResponse {
  error: string
  detail?: string
  status_code?: number
}
```

**Usage**: Error handling in API client

## API Request Types

### CreateTaskInput

Input for creating a new task.

```typescript
export interface CreateTaskInput {
  title: string
  description?: string
  team_id?: string // Optional: for team tasks
}
```

**Endpoints**: POST /api/users/{user_id}/tasks

### UpdateTaskInput

Input for updating an existing task.

```typescript
export interface UpdateTaskInput {
  title?: string
  description?: string
  completed?: boolean
}
```

**Endpoints**: PUT /api/users/{user_id}/tasks/{task_id}

### CreateTeamInput

Input for creating a new team.

```typescript
export interface CreateTeamInput {
  name: string
}
```

**Endpoints**: POST /api/teams

### InviteMemberInput

Input for inviting a user to a team.

```typescript
export interface InviteMemberInput {
  user_email: string
  role: TeamRole
}
```

**Endpoints**: POST /api/teams/{team_id}/members

### CreateTaskShareInput

Input for sharing a task with another user.

```typescript
export interface CreateTaskShareInput {
  task_id: string
  shared_with_user_email: string
  permission: PermissionLevel
}
```

**Endpoints**: POST /api/task-shares

### SignupInput

Input for user registration.

```typescript
export interface SignupInput {
  email: string
  password: string
}
```

**Endpoints**: POST /api/auth/signup

### SigninInput

Input for user login.

```typescript
export interface SigninInput {
  email: string
  password: string
}
```

**Endpoints**: POST /api/auth/signin

## UI State Types

### LoadingState

Represents the loading state of an async operation.

```typescript
export type LoadingState = 'idle' | 'loading' | 'success' | 'error'
```

**Usage**: Form submissions, data fetching

### FormState

Generic form state with loading and error handling.

```typescript
export interface FormState<T = any> {
  loading: boolean
  error: string | null
  data: T | null
}
```

**Usage**: Form components

### PaginationState

State for paginated lists (future enhancement).

```typescript
export interface PaginationState {
  page: number
  page_size: number
  total_count: number
  has_next: boolean
  has_previous: boolean
}
```

**Usage**: Task lists, team lists (if pagination is added)

## Component Prop Types

### TaskCardProps

Props for TaskCard component.

```typescript
export interface TaskCardProps {
  task: Task
  onToggle?: (taskId: string) => void
  onDelete?: (taskId: string) => void
  onEdit?: (taskId: string) => void
  showActions?: boolean
  disabled?: boolean
}
```

### TeamCardProps

Props for TeamCard component.

```typescript
export interface TeamCardProps {
  team: TeamResponse
  onClick?: (teamId: string) => void
}
```

### RoleBadgeProps

Props for RoleBadge component.

```typescript
export interface RoleBadgeProps {
  role: TeamRole
  size?: 'sm' | 'md' | 'lg'
}
```

### PermissionBadgeProps

Props for PermissionBadge component.

```typescript
export interface PermissionBadgeProps {
  permission: PermissionLevel
  size?: 'sm' | 'md' | 'lg'
}
```

## Utility Types

### ApiResult

Generic result type for API calls.

```typescript
export type ApiResult<T> =
  | { success: true; data: T }
  | { success: false; error: ErrorResponse }
```

**Usage**: API client return types

### Optional

Makes all properties of a type optional.

```typescript
export type Optional<T> = {
  [P in keyof T]?: T[P]
}
```

**Usage**: Partial updates

### RequireAtLeastOne

Requires at least one property from a type.

```typescript
export type RequireAtLeastOne<T, Keys extends keyof T = keyof T> =
  Pick<T, Exclude<keyof T, Keys>> &
  {
    [K in Keys]-?: Required<Pick<T, K>> & Partial<Pick<T, Exclude<Keys, K>>>
  }[Keys]
```

**Usage**: Update operations where at least one field must be provided

## Type Guards

### isErrorResponse

Type guard to check if a response is an error.

```typescript
export function isErrorResponse(response: any): response is ErrorResponse {
  return response && typeof response.error === 'string'
}
```

### isTask

Type guard to check if an object is a Task.

```typescript
export function isTask(obj: any): obj is Task {
  return (
    obj &&
    typeof obj.id === 'string' &&
    typeof obj.title === 'string' &&
    typeof obj.completed === 'boolean' &&
    typeof obj.user_id === 'string'
  )
}
```

## Validation Schemas

### Email Validation

```typescript
export const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

export function isValidEmail(email: string): boolean {
  return EMAIL_REGEX.test(email)
}
```

### Password Validation

```typescript
export const PASSWORD_MIN_LENGTH = 8

export function isValidPassword(password: string): boolean {
  return password.length >= PASSWORD_MIN_LENGTH
}

export function getPasswordStrength(password: string): 'weak' | 'medium' | 'strong' {
  if (password.length < 8) return 'weak'
  if (password.length < 12) return 'medium'
  return 'strong'
}
```

### Task Title Validation

```typescript
export const TASK_TITLE_MAX_LENGTH = 200

export function isValidTaskTitle(title: string): boolean {
  return title.trim().length > 0 && title.length <= TASK_TITLE_MAX_LENGTH
}
```

### Team Name Validation

```typescript
export const TEAM_NAME_MAX_LENGTH = 100

export function isValidTeamName(name: string): boolean {
  return name.trim().length > 0 && name.length <= TEAM_NAME_MAX_LENGTH
}
```

## Constants

### API Endpoints

```typescript
export const API_ENDPOINTS = {
  AUTH: {
    SIGNUP: '/api/auth/signup',
    SIGNIN: '/api/auth/signin',
    SIGNOUT: '/api/auth/signout',
    SESSION: '/api/auth/session',
  },
  TASKS: {
    LIST: (userId: string) => `/api/users/${userId}/tasks`,
    CREATE: (userId: string) => `/api/users/${userId}/tasks`,
    GET: (userId: string, taskId: string) => `/api/users/${userId}/tasks/${taskId}`,
    UPDATE: (userId: string, taskId: string) => `/api/users/${userId}/tasks/${taskId}`,
    DELETE: (userId: string, taskId: string) => `/api/users/${userId}/tasks/${taskId}`,
    TOGGLE: (userId: string, taskId: string) => `/api/users/${userId}/tasks/${taskId}/toggle`,
  },
  TEAMS: {
    LIST: '/api/teams',
    CREATE: '/api/teams',
    GET: (teamId: string) => `/api/teams/${teamId}`,
    MEMBERS: (teamId: string) => `/api/teams/${teamId}/members`,
    INVITE: (teamId: string) => `/api/teams/${teamId}/members`,
    TASKS: (teamId: string) => `/api/teams/${teamId}/tasks`,
  },
  TASK_SHARES: {
    LIST: '/api/task-shares',
    CREATE: '/api/task-shares',
    DELETE: (shareId: string) => `/api/task-shares/${shareId}`,
  },
} as const
```

### UI Constants

```typescript
export const UI_CONSTANTS = {
  TOAST_DURATION: 3000, // milliseconds
  DEBOUNCE_DELAY: 300, // milliseconds
  MAX_MOBILE_WIDTH: 768, // pixels
  MIN_TOUCH_TARGET: 44, // pixels
} as const
```

## Type Exports

All types should be exported from a central location:

```typescript
// lib/types/index.ts
export * from './models'
export * from './api'
export * from './ui'
export * from './validation'
export * from './constants'
```

## Usage Examples

### API Call with Type Safety

```typescript
import { getTasks } from '@/lib/api/tasks'
import type { Task } from '@/lib/types'

async function loadTasks(userId: string): Promise<Task[]> {
  const tasks = await getTasks(userId)
  return tasks
}
```

### Form with Type Safety

```typescript
import type { CreateTaskInput } from '@/lib/types'

function TaskForm() {
  const [formData, setFormData] = useState<CreateTaskInput>({
    title: '',
    description: '',
  })

  // TypeScript ensures formData matches CreateTaskInput
}
```

### Component with Type Safety

```typescript
import type { TaskCardProps } from '@/lib/types'

export function TaskCard({ task, onToggle, disabled }: TaskCardProps) {
  // TypeScript ensures all props are correctly typed
}
```

## Notes

- All timestamps use ISO 8601 format (e.g., "2026-02-05T10:30:00Z")
- All IDs are strings (UUIDs from backend)
- Optional fields use `| null` or `?` depending on context
- Enums use string literal unions for better type safety
- Type guards provide runtime type checking
- Validation functions ensure data integrity before API calls
