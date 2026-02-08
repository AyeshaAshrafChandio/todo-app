# API Contracts: Teams, RBAC, and Task Sharing

**Feature**: 003-teams-rbac-sharing
**Date**: 2026-02-04
**API Version**: v1
**Base URL**: `/api`

## Authentication

All endpoints require JWT authentication via `Authorization: Bearer <token>` header unless explicitly marked as public.

**Authentication Header**:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Error Responses**:
- `401 Unauthorized`: Missing or invalid JWT token
- `403 Forbidden`: Valid token but insufficient permissions

---

## Team Endpoints

### POST /api/teams

Create a new team. The authenticated user becomes the owner.

**Authentication**: Required

**Request Body**:
```json
{
  "name": "string (required, 1-255 chars, unique)",
  "description": "string (optional, max 5000 chars)"
}
```

**Success Response** (201 Created):
```json
{
  "id": "uuid",
  "name": "string",
  "description": "string | null",
  "owner_id": "uuid",
  "created_at": "ISO 8601 timestamp",
  "updated_at": "ISO 8601 timestamp"
}
```

**Error Responses**:
- `400 Bad Request`: Invalid request data (missing name, name too long, etc.)
- `409 Conflict`: Team name already exists
- `401 Unauthorized`: Not authenticated

**Example**:
```bash
curl -X POST https://api.example.com/api/teams \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Engineering Team",
    "description": "Core engineering team for product development"
  }'
```

---

### GET /api/teams

List all teams the authenticated user is a member of.

**Authentication**: Required

**Query Parameters**: None

**Success Response** (200 OK):
```json
[
  {
    "id": "uuid",
    "name": "string",
    "description": "string | null",
    "role": "owner | admin | member | viewer",
    "member_count": "integer",
    "created_at": "ISO 8601 timestamp"
  }
]
```

**Error Responses**:
- `401 Unauthorized`: Not authenticated

**Example**:
```bash
curl -X GET https://api.example.com/api/teams \
  -H "Authorization: Bearer <token>"
```

---

### GET /api/teams/{team_id}

Get detailed information about a specific team, including all members.

**Authentication**: Required

**Permission**: Must be a team member

**Path Parameters**:
- `team_id` (uuid, required): Team identifier

**Success Response** (200 OK):
```json
{
  "id": "uuid",
  "name": "string",
  "description": "string | null",
  "owner_id": "uuid",
  "created_at": "ISO 8601 timestamp",
  "updated_at": "ISO 8601 timestamp",
  "members": [
    {
      "user_id": "uuid",
      "email": "string",
      "role": "owner | admin | member | viewer",
      "joined_at": "ISO 8601 timestamp"
    }
  ]
}
```

**Error Responses**:
- `401 Unauthorized`: Not authenticated
- `403 Forbidden`: Not a team member
- `404 Not Found`: Team does not exist

**Example**:
```bash
curl -X GET https://api.example.com/api/teams/123e4567-e89b-12d3-a456-426614174000 \
  -H "Authorization: Bearer <token>"
```

---

### PATCH /api/teams/{team_id}

Update team settings (name and/or description).

**Authentication**: Required

**Permission**: Owner or Admin

**Path Parameters**:
- `team_id` (uuid, required): Team identifier

**Request Body**:
```json
{
  "name": "string (optional, 1-255 chars, unique)",
  "description": "string (optional, max 5000 chars)"
}
```

**Success Response** (200 OK):
```json
{
  "id": "uuid",
  "name": "string",
  "description": "string | null",
  "updated_at": "ISO 8601 timestamp"
}
```

**Error Responses**:
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Not authenticated
- `403 Forbidden`: Not owner or admin
- `404 Not Found`: Team does not exist
- `409 Conflict`: New name already exists

**Example**:
```bash
curl -X PATCH https://api.example.com/api/teams/123e4567-e89b-12d3-a456-426614174000 \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Updated team description"
  }'
```

---

### DELETE /api/teams/{team_id}

Delete a team. All team members are removed, and team tasks are converted to personal tasks.

**Authentication**: Required

**Permission**: Owner only

**Path Parameters**:
- `team_id` (uuid, required): Team identifier

**Success Response** (204 No Content):
```
(empty body)
```

**Error Responses**:
- `401 Unauthorized`: Not authenticated
- `403 Forbidden`: Not the team owner
- `404 Not Found`: Team does not exist

**Example**:
```bash
curl -X DELETE https://api.example.com/api/teams/123e4567-e89b-12d3-a456-426614174000 \
  -H "Authorization: Bearer <token>"
```

---

## Team Membership Endpoints

### POST /api/teams/{team_id}/members

Invite a user to join the team with a specific role.

**Authentication**: Required

**Permission**: Owner or Admin

**Path Parameters**:
- `team_id` (uuid, required): Team identifier

**Request Body**:
```json
{
  "user_id": "uuid (required)",
  "role": "admin | member | viewer (required)"
}
```

**Note**: Owners and admins cannot assign the "owner" role via this endpoint. Ownership transfer is done via PATCH /api/teams/{team_id}/members/{user_id}.

**Success Response** (201 Created):
```json
{
  "id": "uuid",
  "team_id": "uuid",
  "user_id": "uuid",
  "role": "admin | member | viewer",
  "joined_at": "ISO 8601 timestamp"
}
```

**Error Responses**:
- `400 Bad Request`: Invalid request data or invalid role
- `401 Unauthorized`: Not authenticated
- `403 Forbidden`: Not owner or admin
- `404 Not Found`: Team or user does not exist
- `409 Conflict`: User is already a team member

**Example**:
```bash
curl -X POST https://api.example.com/api/teams/123e4567-e89b-12d3-a456-426614174000/members \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "987fcdeb-51a2-43f7-b123-456789abcdef",
    "role": "member"
  }'
```

---

### PATCH /api/teams/{team_id}/members/{user_id}

Change a team member's role.

**Authentication**: Required

**Permission**:
- Owner: Can assign any role (including transferring ownership)
- Admin: Can only assign "member" or "viewer" roles

**Path Parameters**:
- `team_id` (uuid, required): Team identifier
- `user_id` (uuid, required): User identifier

**Request Body**:
```json
{
  "role": "owner | admin | member | viewer (required)"
}
```

**Note**: Promoting a member to "owner" automatically demotes the current owner to "admin" (atomic operation).

**Success Response** (200 OK):
```json
{
  "team_id": "uuid",
  "user_id": "uuid",
  "role": "owner | admin | member | viewer",
  "updated_at": "ISO 8601 timestamp"
}
```

**Error Responses**:
- `400 Bad Request`: Invalid role
- `401 Unauthorized`: Not authenticated
- `403 Forbidden`: Insufficient permissions for requested role change
- `404 Not Found`: Team or user does not exist

**Example**:
```bash
curl -X PATCH https://api.example.com/api/teams/123e4567-e89b-12d3-a456-426614174000/members/987fcdeb-51a2-43f7-b123-456789abcdef \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "admin"
  }'
```

---

### DELETE /api/teams/{team_id}/members/{user_id}

Remove a member from the team.

**Authentication**: Required

**Permission**: Owner or Admin

**Restrictions**: Cannot remove the team owner

**Path Parameters**:
- `team_id` (uuid, required): Team identifier
- `user_id` (uuid, required): User identifier

**Success Response** (204 No Content):
```
(empty body)
```

**Error Responses**:
- `401 Unauthorized`: Not authenticated
- `403 Forbidden`: Not owner/admin, or attempting to remove owner
- `404 Not Found`: Team or user does not exist

**Example**:
```bash
curl -X DELETE https://api.example.com/api/teams/123e4567-e89b-12d3-a456-426614174000/members/987fcdeb-51a2-43f7-b123-456789abcdef \
  -H "Authorization: Bearer <token>"
```

---

### POST /api/teams/{team_id}/leave

Leave a team (self-removal).

**Authentication**: Required

**Permission**: Any team member except owner

**Restrictions**: Team owner cannot leave (must transfer ownership first)

**Path Parameters**:
- `team_id` (uuid, required): Team identifier

**Success Response** (204 No Content):
```
(empty body)
```

**Error Responses**:
- `401 Unauthorized`: Not authenticated
- `403 Forbidden`: User is the team owner
- `404 Not Found`: Team does not exist or user is not a member

**Example**:
```bash
curl -X POST https://api.example.com/api/teams/123e4567-e89b-12d3-a456-426614174000/leave \
  -H "Authorization: Bearer <token>"
```

---

## Extended Task Endpoints

### POST /api/tasks

Create a new task (personal or team-owned).

**Authentication**: Required

**Permission**: If team_id is provided, must be a team member with create permission (owner, admin, or member)

**Request Body**:
```json
{
  "title": "string (required, 1-255 chars)",
  "description": "string (optional, max 5000 chars)",
  "completed": "boolean (optional, default: false)",
  "team_id": "uuid (optional, null for personal task)"
}
```

**Success Response** (201 Created):
```json
{
  "id": "uuid",
  "title": "string",
  "description": "string | null",
  "completed": "boolean",
  "user_id": "uuid",
  "team_id": "uuid | null",
  "created_at": "ISO 8601 timestamp",
  "updated_at": "ISO 8601 timestamp"
}
```

**Error Responses**:
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Not authenticated
- `403 Forbidden`: Not a team member or insufficient role (viewer cannot create)
- `404 Not Found`: Team does not exist

**Example**:
```bash
curl -X POST https://api.example.com/api/tasks \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Implement authentication",
    "description": "Add JWT-based authentication to the API",
    "team_id": "123e4567-e89b-12d3-a456-426614174000"
  }'
```

---

### GET /api/tasks

List all tasks accessible to the authenticated user (personal + team + shared).

**Authentication**: Required

**Query Parameters**:
- `team_id` (uuid, optional): Filter by specific team
- `shared` (boolean, optional): If true, only return shared tasks

**Success Response** (200 OK):
```json
[
  {
    "id": "uuid",
    "title": "string",
    "description": "string | null",
    "completed": "boolean",
    "user_id": "uuid",
    "team_id": "uuid | null",
    "is_shared": "boolean",
    "access_type": "owner | team_owner | team_admin | team_member | team_viewer | shared_view | shared_edit",
    "created_at": "ISO 8601 timestamp",
    "updated_at": "ISO 8601 timestamp"
  }
]
```

**Error Responses**:
- `401 Unauthorized`: Not authenticated
- `404 Not Found`: Team does not exist (if team_id filter provided)

**Example**:
```bash
# Get all accessible tasks
curl -X GET https://api.example.com/api/tasks \
  -H "Authorization: Bearer <token>"

# Get tasks for specific team
curl -X GET "https://api.example.com/api/tasks?team_id=123e4567-e89b-12d3-a456-426614174000" \
  -H "Authorization: Bearer <token>"

# Get only shared tasks
curl -X GET "https://api.example.com/api/tasks?shared=true" \
  -H "Authorization: Bearer <token>"
```

---

### GET /api/tasks/{task_id}

Get detailed information about a specific task, including sharing information.

**Authentication**: Required

**Permission**: Owner, team member, or has share access

**Path Parameters**:
- `task_id` (uuid, required): Task identifier

**Success Response** (200 OK):
```json
{
  "id": "uuid",
  "title": "string",
  "description": "string | null",
  "completed": "boolean",
  "user_id": "uuid",
  "team_id": "uuid | null",
  "created_at": "ISO 8601 timestamp",
  "updated_at": "ISO 8601 timestamp",
  "shared_with": [
    {
      "user_id": "uuid",
      "email": "string",
      "permission": "view | edit",
      "shared_at": "ISO 8601 timestamp"
    }
  ]
}
```

**Error Responses**:
- `401 Unauthorized`: Not authenticated
- `403 Forbidden`: No access to this task
- `404 Not Found`: Task does not exist

**Example**:
```bash
curl -X GET https://api.example.com/api/tasks/456e7890-e12b-34d5-a678-901234567890 \
  -H "Authorization: Bearer <token>"
```

---

### PATCH /api/tasks/{task_id}

Update a task's details.

**Authentication**: Required

**Permission**: Owner, team owner/admin, or has "edit" share permission

**Path Parameters**:
- `task_id` (uuid, required): Task identifier

**Request Body**:
```json
{
  "title": "string (optional, 1-255 chars)",
  "description": "string (optional, max 5000 chars)",
  "completed": "boolean (optional)"
}
```

**Success Response** (200 OK):
```json
{
  "id": "uuid",
  "title": "string",
  "description": "string | null",
  "completed": "boolean",
  "updated_at": "ISO 8601 timestamp"
}
```

**Error Responses**:
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Not authenticated
- `403 Forbidden`: Insufficient permissions to edit
- `404 Not Found`: Task does not exist

**Example**:
```bash
curl -X PATCH https://api.example.com/api/tasks/456e7890-e12b-34d5-a678-901234567890 \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "completed": true
  }'
```

---

### DELETE /api/tasks/{task_id}

Delete a task.

**Authentication**: Required

**Permission**: Owner only (team admins/owners can delete team tasks)

**Path Parameters**:
- `task_id` (uuid, required): Task identifier

**Success Response** (204 No Content):
```
(empty body)
```

**Error Responses**:
- `401 Unauthorized`: Not authenticated
- `403 Forbidden`: Not the task owner or team admin/owner
- `404 Not Found`: Task does not exist

**Example**:
```bash
curl -X DELETE https://api.example.com/api/tasks/456e7890-e12b-34d5-a678-901234567890 \
  -H "Authorization: Bearer <token>"
```

---

## Task Sharing Endpoints

### POST /api/tasks/{task_id}/share

Share a task with another user.

**Authentication**: Required

**Permission**: Task owner only

**Path Parameters**:
- `task_id` (uuid, required): Task identifier

**Request Body**:
```json
{
  "user_id": "uuid (required)",
  "permission": "view | edit (required)"
}
```

**Success Response** (201 Created):
```json
{
  "id": "uuid",
  "task_id": "uuid",
  "shared_with_user_id": "uuid",
  "shared_by_user_id": "uuid",
  "permission": "view | edit",
  "shared_at": "ISO 8601 timestamp"
}
```

**Error Responses**:
- `400 Bad Request`: Invalid request data or attempting to share with self
- `401 Unauthorized`: Not authenticated
- `403 Forbidden`: Not the task owner
- `404 Not Found`: Task or user does not exist
- `409 Conflict`: Task already shared with this user

**Example**:
```bash
curl -X POST https://api.example.com/api/tasks/456e7890-e12b-34d5-a678-901234567890/share \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "789abcde-f012-3456-7890-abcdef123456",
    "permission": "edit"
  }'
```

---

### DELETE /api/tasks/{task_id}/share/{user_id}

Revoke task sharing access from a user.

**Authentication**: Required

**Permission**: Task owner only

**Path Parameters**:
- `task_id` (uuid, required): Task identifier
- `user_id` (uuid, required): User to revoke access from

**Success Response** (204 No Content):
```
(empty body)
```

**Error Responses**:
- `401 Unauthorized`: Not authenticated
- `403 Forbidden`: Not the task owner
- `404 Not Found`: Task, user, or share does not exist

**Example**:
```bash
curl -X DELETE https://api.example.com/api/tasks/456e7890-e12b-34d5-a678-901234567890/share/789abcde-f012-3456-7890-abcdef123456 \
  -H "Authorization: Bearer <token>"
```

---

### GET /api/tasks/shared-with-me

List all tasks that have been shared with the authenticated user.

**Authentication**: Required

**Success Response** (200 OK):
```json
[
  {
    "id": "uuid",
    "title": "string",
    "description": "string | null",
    "completed": "boolean",
    "owner_email": "string",
    "permission": "view | edit",
    "shared_at": "ISO 8601 timestamp",
    "created_at": "ISO 8601 timestamp",
    "updated_at": "ISO 8601 timestamp"
  }
]
```

**Error Responses**:
- `401 Unauthorized`: Not authenticated

**Example**:
```bash
curl -X GET https://api.example.com/api/tasks/shared-with-me \
  -H "Authorization: Bearer <token>"
```

---

## Error Response Format

All error responses follow a consistent format:

```json
{
  "error": "Brief error message",
  "detail": "Detailed explanation (optional)"
}
```

**Common HTTP Status Codes**:
- `200 OK`: Successful GET, PATCH
- `201 Created`: Successful POST creating new resource
- `204 No Content`: Successful DELETE
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: Valid auth but insufficient permissions
- `404 Not Found`: Resource does not exist
- `409 Conflict`: Resource conflict (duplicate name, already exists)
- `500 Internal Server Error`: Unexpected server error

---

## Rate Limiting

**Not implemented in this specification**. Future consideration for production deployment.

---

## Versioning

**Current Version**: v1

API version is included in the base URL path: `/api/v1/...` (optional for v1, can use `/api/...`)

Breaking changes will require a new API version (v2, v3, etc.).

---

## CORS Configuration

The API supports CORS for frontend integration. Allowed origins are configured via `CORS_ORIGINS` environment variable.

**Allowed Methods**: GET, POST, PATCH, DELETE, OPTIONS
**Allowed Headers**: Authorization, Content-Type
**Credentials**: Allowed (for cookie-based auth if needed)

---

## Summary

**Total Endpoints**: 18

| Category | Endpoints |
|----------|-----------|
| Teams | 5 (POST, GET, GET/:id, PATCH/:id, DELETE/:id) |
| Team Members | 4 (POST, PATCH, DELETE, POST/leave) |
| Tasks (Extended) | 5 (POST, GET, GET/:id, PATCH/:id, DELETE/:id) |
| Task Sharing | 3 (POST/share, DELETE/share, GET/shared-with-me) |

All endpoints require JWT authentication except public auth endpoints (signup, signin) from Spec 002.
