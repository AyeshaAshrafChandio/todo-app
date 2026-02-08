# Phase 5: Team-Based Task Management Implementation

**Feature**: 003-teams-rbac-sharing (User Story 3)
**Date**: 2026-02-04
**Status**: Complete ✅

## Overview

Phase 5 extends the existing task system to support team-based task management with role-based access control. This implementation enables users to create tasks associated with teams, with visibility and permissions based on team membership and roles.

## Implementation Summary

### Tasks Completed: 12/12 (100%)

**Pydantic Schemas (T044-T045)**: ✅
- Extended `TaskCreate` schema to accept optional `team_id` field
- Extended `TaskResponse` schema to include `team_id` and `access_type` fields

**Service Layer (T046-T050)**: ✅
- Extended `create_task()` to validate team membership and prevent viewers from creating tasks
- Extended `get_tasks_by_user()` to return union of personal, team, and shared tasks
- Extended `get_task_by_id()` to check team access permissions
- Extended `update_task()` to enforce team role permissions
- Extended `delete_task()` to enforce team role permissions

**API Routes (T051-T055)**: ✅
- Extended POST `/api/{user_id}/tasks` to accept team_id and validate membership
- Extended GET `/api/{user_id}/tasks` to support team_id filter and return accessible tasks
- Extended GET `/api/{user_id}/tasks/{id}` to check team access permissions
- Extended PATCH `/api/{user_id}/tasks/{id}` to enforce team role permissions
- Extended DELETE `/api/{user_id}/tasks/{id}` to enforce team role permissions

## Key Features Implemented

### 1. Team Task Creation
- Users can create tasks associated with teams by providing `team_id`
- System validates team membership before allowing task creation
- Viewers cannot create team tasks (403 Forbidden)
- Personal tasks remain unchanged (team_id=null)

### 2. Access Control Hierarchy
Tasks are accessible through three mechanisms:
1. **Task Ownership**: User created the task
2. **Team Membership**: User is a member of the task's team
3. **Direct Sharing**: Task is shared with user (Phase 6)

### 3. Role-Based Permissions

**View Permission**:
- Task owner: ✅
- Team owner/admin/member/viewer: ✅
- Shared users: ✅

**Edit Permission**:
- Task owner: ✅
- Team owner/admin: ✅ (all team tasks)
- Team member: ✅ (own tasks only)
- Team viewer: ❌
- Shared with edit permission: ✅

**Delete Permission**:
- Task owner: ✅
- Team owner/admin: ✅ (all team tasks)
- Team member: ❌
- Team viewer: ❌
- Shared users: ❌ (even with edit permission)

### 4. Access Type Indicators

The `access_type` field in `TaskResponse` indicates the user's permission level:
- `"owner"` - User owns the task
- `"team_owner"` - User is team owner
- `"team_admin"` - User is team admin
- `"team_member"` - User is team member
- `"team_viewer"` - User is team viewer
- `"shared_view"` - Task shared with view permission
- `"shared_edit"` - Task shared with edit permission

### 5. Task Filtering

GET `/api/{user_id}/tasks` supports:
- **No filter**: Returns all accessible tasks (personal + team + shared)
- **team_id filter**: Returns only tasks from specified team (validates membership)

## Files Modified

### Schemas
- `backend/app/schemas/task.py`
  - Added `team_id` field to `TaskCreate` schema
  - Added `team_id` and `access_type` fields to `TaskResponse` schema

### Service Layer
- `backend/app/services/task_service.py`
  - Added imports for team models and permission functions
  - Extended `create_task()` with team membership validation
  - Extended `get_tasks_by_user()` to return union of accessible tasks
  - Extended `get_task_by_id()` with team access checking
  - Extended `update_task()` with team role permission enforcement
  - Extended `delete_task()` with team role permission enforcement

### API Routes
- `backend/app/routes/tasks.py`
  - Added imports for Query parameter and permission functions
  - Extended POST endpoint to accept and validate team_id
  - Extended GET list endpoint to support team_id filter
  - Extended GET single endpoint to check team access
  - Extended PATCH endpoint to enforce team role permissions
  - Extended DELETE endpoint to enforce team role permissions
  - All endpoints now return access_type in responses

### Task Tracking
- `specs/003-teams-rbac-sharing/tasks.md`
  - Marked T044-T055 as complete

## Backward Compatibility

✅ **Personal tasks remain fully functional**:
- Tasks with `team_id=null` work exactly as before
- No breaking changes to existing personal task functionality
- All existing API contracts maintained

## API Examples

### Create Personal Task
```bash
POST /api/user123/tasks
{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "team_id": null
}

Response (201):
{
  "id": 1,
  "title": "Buy groceries",
  "user_id": "user123",
  "team_id": null,
  "access_type": "owner",
  ...
}
```

### Create Team Task
```bash
POST /api/user123/tasks
{
  "title": "Sprint planning",
  "description": "Plan next sprint",
  "team_id": "team456"
}

Response (201):
{
  "id": 2,
  "title": "Sprint planning",
  "user_id": "user123",
  "team_id": "team456",
  "access_type": "team_member",
  ...
}
```

### List All Accessible Tasks
```bash
GET /api/user123/tasks

Response (200):
[
  {
    "id": 1,
    "title": "Buy groceries",
    "team_id": null,
    "access_type": "owner",
    ...
  },
  {
    "id": 2,
    "title": "Sprint planning",
    "team_id": "team456",
    "access_type": "team_member",
    ...
  }
]
```

### Filter by Team
```bash
GET /api/user123/tasks?team_id=team456

Response (200):
[
  {
    "id": 2,
    "title": "Sprint planning",
    "team_id": "team456",
    "access_type": "team_member",
    ...
  }
]
```

## Permission Enforcement Examples

### Viewer Cannot Create Task
```bash
POST /api/viewer123/tasks
{
  "title": "New task",
  "team_id": "team456"
}

Response (403):
{
  "detail": "Viewers cannot create team tasks"
}
```

### Member Cannot Edit Other's Task
```bash
PATCH /api/member123/tasks/5
{
  "title": "Updated title"
}

Response (403):
{
  "detail": "You do not have permission to edit this task"
}
```

### Admin Can Delete Team Task
```bash
DELETE /api/admin123/tasks/5

Response (204):
(No content - task deleted successfully)
```

## Testing Recommendations

### Unit Tests
1. Test team task creation with different roles
2. Test task visibility based on team membership
3. Test permission enforcement for edit/delete operations
4. Test backward compatibility with personal tasks
5. Test team_id filter functionality

### Integration Tests
1. Create team → Add members → Create team tasks → Verify visibility
2. Test role changes and permission updates
3. Test task access after leaving team
4. Test task access after team deletion

### Edge Cases
1. User is member of multiple teams
2. Task shared AND team-owned (Phase 6)
3. Team deleted while tasks exist
4. User removed from team while viewing task

## Dependencies

**Required Models**:
- `Task` (with team_id field) ✅
- `Team` ✅
- `TeamMember` ✅
- `TeamRole` enum ✅

**Required Middleware**:
- `can_access_task()` ✅
- `can_edit_task()` ✅
- `can_delete_task()` ✅
- `require_team_member()` ✅

## Next Steps (Phase 6)

Phase 6 will implement User Story 4 (Direct Task Sharing):
- Create task sharing endpoints
- Implement share permission management
- Add shared task visibility to queries
- Handle conflicts between team and share permissions

## Technical Notes

### Query Optimization
The `get_tasks_by_user()` function performs three separate queries:
1. Personal tasks (user_id match, team_id NULL)
2. Team tasks (team membership lookup)
3. Shared tasks (task_share lookup)

**Future Optimization**: Consider using UNION queries or subqueries for better performance with large datasets.

### Access Type Calculation
Access type is calculated on-demand using `can_access_task()` for each task in responses. This ensures real-time permission checking but may impact performance with large result sets.

**Future Optimization**: Consider caching access types or using database views.

### Transaction Safety
All database operations use proper transaction handling:
- Rollback on errors
- Commit only on success
- Refresh to get updated timestamps

## Validation

✅ All 12 tasks completed
✅ Backward compatibility maintained
✅ Permission functions integrated
✅ API contracts followed
✅ Error handling implemented
✅ Documentation updated

## Summary

Phase 5 successfully extends the task system to support team-based task management with comprehensive role-based access control. The implementation maintains backward compatibility with personal tasks while adding powerful team collaboration features. All permission checks are enforced at both the service and API layers, ensuring security and data isolation.

**Status**: Ready for testing and Phase 6 implementation (Direct Task Sharing)
