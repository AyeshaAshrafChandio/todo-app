# Teams API Contract

**Feature**: Frontend Full-Stack UI (004-frontend-fullstack-ui)
**Date**: 2026-02-05
**Backend Feature**: 003-roles-teams-and-task-sharing

## Overview

This document defines the teams API endpoints that the frontend will consume. All endpoints require authentication and enforce role-based access control.

## Base URL

```
{NEXT_PUBLIC_API_URL}/api/teams
```

## Authentication

All endpoints require JWT token in Authorization header:
```
Authorization: Bearer {token}
```

## Endpoints

### 1. List User Teams

**Endpoint**: `GET /api/teams`

**Description**: Get all teams the authenticated user belongs to

**Query Parameters**: None

**Success Response** (200 OK):
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Engineering Team",
    "created_at": "2026-02-01T10:00:00Z",
    "member_count": 5,
    "user_role": "owner"
  },
  {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "name": "Design Team",
    "created_at": "2026-02-03T14:30:00Z",
    "member_count": 3,
    "user_role": "member"
  }
]
```

**Response Schema**:
```typescript
Array<{
  id: string
  name: string
  created_at: string
  member_count: number
  user_role: 'owner' | 'admin' | 'member' | 'viewer'
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

### 2. Create Team

**Endpoint**: `POST /api/teams`

**Description**: Create a new team (user becomes owner)

**Request Body**:
```json
{
  "name": "Engineering Team"
}
```

**Request Schema**:
```typescript
{
  name: string  // Required, max 100 characters
}
```

**Success Response** (201 Created):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Engineering Team",
  "created_at": "2026-02-05T10:30:00Z",
  "member_count": 1,
  "user_role": "owner"
}
```

**Error Responses**:

400 Bad Request:
```json
{
  "error": "Invalid input",
  "detail": "Team name is required and cannot be empty"
}
```

401 Unauthorized:
```json
{
  "error": "Unauthorized",
  "detail": "Invalid or expired token"
}
```

---

### 3. Get Team Details

**Endpoint**: `GET /api/teams/{team_id}`

**Description**: Get details of a specific team

**Path Parameters**:
- `team_id` (string, required): Team ID

**Success Response** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Engineering Team",
  "created_at": "2026-02-01T10:00:00Z",
  "member_count": 5,
  "user_role": "owner"
}
```

**Error Responses**:

404 Not Found:
```json
{
  "error": "Team not found",
  "detail": "Team does not exist or you are not a member"
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
  "detail": "You are not a member of this team"
}
```

---

### 4. Get Team Members

**Endpoint**: `GET /api/teams/{team_id}/members`

**Description**: Get all members of a team

**Path Parameters**:
- `team_id` (string, required): Team ID

**Success Response** (200 OK):
```json
[
  {
    "id": "member-id-1",
    "team_id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "user-id-1",
    "role": "owner",
    "joined_at": "2026-02-01T10:00:00Z",
    "user": {
      "id": "user-id-1",
      "email": "owner@example.com",
      "created_at": "2026-01-15T09:00:00Z"
    }
  },
  {
    "id": "member-id-2",
    "team_id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "user-id-2",
    "role": "admin",
    "joined_at": "2026-02-02T11:00:00Z",
    "user": {
      "id": "user-id-2",
      "email": "admin@example.com",
      "created_at": "2026-01-20T10:00:00Z"
    }
  }
]
```

**Response Schema**:
```typescript
Array<{
  id: string
  team_id: string
  user_id: string
  role: 'owner' | 'admin' | 'member' | 'viewer'
  joined_at: string
  user: {
    id: string
    email: string
    created_at: string
  }
}>
```

**Error Responses**:

404 Not Found:
```json
{
  "error": "Team not found",
  "detail": "Team does not exist or you are not a member"
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
  "detail": "You are not a member of this team"
}
```

---

### 5. Invite Team Member

**Endpoint**: `POST /api/teams/{team_id}/members`

**Description**: Invite a user to join the team (requires owner or admin role)

**Path Parameters**:
- `team_id` (string, required): Team ID

**Request Body**:
```json
{
  "user_email": "newmember@example.com",
  "role": "member"
}
```

**Request Schema**:
```typescript
{
  user_email: string  // Required, valid email
  role: 'admin' | 'member' | 'viewer'  // Required, cannot be 'owner'
}
```

**Success Response** (201 Created):
```json
{
  "id": "member-id-3",
  "team_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user-id-3",
  "role": "member",
  "joined_at": "2026-02-05T12:00:00Z",
  "user": {
    "id": "user-id-3",
    "email": "newmember@example.com",
    "created_at": "2026-01-25T08:00:00Z"
  }
}
```

**Error Responses**:

400 Bad Request:
```json
{
  "error": "Invalid input",
  "detail": "User email is required"
}
```

404 Not Found - User not found:
```json
{
  "error": "User not found",
  "detail": "No user exists with this email"
}
```

409 Conflict - Already a member:
```json
{
  "error": "User already a member",
  "detail": "This user is already a member of the team"
}
```

401 Unauthorized:
```json
{
  "error": "Unauthorized",
  "detail": "Invalid or expired token"
}
```

403 Forbidden - Insufficient permissions:
```json
{
  "error": "Access denied",
  "detail": "Only owners and admins can invite members"
}
```

---

### 6. Get Team Tasks

**Endpoint**: `GET /api/teams/{team_id}/tasks`

**Description**: Get all tasks associated with a team

**Path Parameters**:
- `team_id` (string, required): Team ID

**Success Response** (200 OK):
```json
[
  {
    "id": "task-id-1",
    "title": "Team planning meeting",
    "description": "Quarterly planning session",
    "completed": false,
    "user_id": "user-id-1",
    "team_id": "550e8400-e29b-41d4-a716-446655440000",
    "created_at": "2026-02-05T10:00:00Z",
    "updated_at": "2026-02-05T10:00:00Z"
  },
  {
    "id": "task-id-2",
    "title": "Code review",
    "description": null,
    "completed": true,
    "user_id": "user-id-2",
    "team_id": "550e8400-e29b-41d4-a716-446655440000",
    "created_at": "2026-02-04T14:00:00Z",
    "updated_at": "2026-02-05T09:00:00Z"
  }
]
```

**Response Schema**:
```typescript
Array<{
  id: string
  title: string
  description: string | null
  completed: boolean
  user_id: string
  team_id: string
  created_at: string
  updated_at: string
}>
```

**Error Responses**:

404 Not Found:
```json
{
  "error": "Team not found",
  "detail": "Team does not exist or you are not a member"
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
  "detail": "You are not a member of this team"
}
```

---

## Role-Based Access Control (RBAC)

### Role Permissions

| Action | Owner | Admin | Member | Viewer |
|--------|-------|-------|--------|--------|
| View team details | ✅ | ✅ | ✅ | ✅ |
| View team members | ✅ | ✅ | ✅ | ✅ |
| View team tasks | ✅ | ✅ | ✅ | ✅ |
| Create team tasks | ✅ | ✅ | ✅ | ❌ |
| Edit team tasks | ✅ | ✅ | ✅ | ❌ |
| Delete team tasks | ✅ | ✅ | ✅ | ❌ |
| Invite members | ✅ | ✅ | ❌ | ❌ |
| Remove members | ✅ | ✅ | ❌ | ❌ |
| Change member roles | ✅ | ❌ | ❌ | ❌ |
| Delete team | ✅ | ❌ | ❌ | ❌ |

### Frontend Implementation

The frontend should:
1. Display user's role in each team
2. Disable/hide actions based on role
3. Trust backend for permission enforcement
4. Handle 403 errors gracefully

**Example**:
```typescript
function canInviteMembers(userRole: TeamRole): boolean {
  return userRole === 'owner' || userRole === 'admin'
}

function canEditTeamTask(userRole: TeamRole): boolean {
  return userRole !== 'viewer'
}
```

## Security & Validation

### Team Access Control
- Users can only access teams they are members of
- Backend enforces membership checks on all endpoints
- Cross-team access attempts return 403 Forbidden

### Input Validation
- Team name: Required, non-empty, max 100 characters
- User email: Required, valid email format
- Role: Must be one of: owner, admin, member, viewer
- Team ID: Must be valid UUID format

### Role Restrictions
- Only one owner per team (team creator)
- Owner role cannot be assigned via invite
- Owners cannot be removed from team
- Admins can invite but cannot change roles

## Frontend Implementation Example

```typescript
// lib/api/teams.ts
import { apiClient } from './client'
import type {
  Team,
  TeamResponse,
  TeamMemberResponse,
  Task,
  CreateTeamInput,
  InviteMemberInput
} from '@/lib/types'

export async function getTeams(): Promise<TeamResponse[]> {
  return apiClient<TeamResponse[]>('/api/teams')
}

export async function createTeam(data: CreateTeamInput): Promise<TeamResponse> {
  return apiClient<TeamResponse>('/api/teams', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function getTeam(teamId: string): Promise<TeamResponse> {
  return apiClient<TeamResponse>(`/api/teams/${teamId}`)
}

export async function getTeamMembers(teamId: string): Promise<TeamMemberResponse[]> {
  return apiClient<TeamMemberResponse[]>(`/api/teams/${teamId}/members`)
}

export async function inviteMember(
  teamId: string,
  data: InviteMemberInput
): Promise<TeamMemberResponse> {
  return apiClient<TeamMemberResponse>(`/api/teams/${teamId}/members`, {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function getTeamTasks(teamId: string): Promise<Task[]> {
  return apiClient<Task[]>(`/api/teams/${teamId}/tasks`)
}
```

## Testing Checklist

- [ ] List teams returns only teams user is a member of
- [ ] Create team succeeds and user becomes owner
- [ ] Get team details for member team succeeds
- [ ] Get team details for non-member team fails with 403
- [ ] Get team members shows all members with roles
- [ ] Invite member as owner/admin succeeds
- [ ] Invite member as member/viewer fails with 403
- [ ] Invite existing member fails with 409
- [ ] Get team tasks shows all team tasks
- [ ] Role badges display correctly for each member
- [ ] Action buttons disabled/hidden based on user role
- [ ] All endpoints reject requests without JWT token (401)
