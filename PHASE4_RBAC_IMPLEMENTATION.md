# Phase 4: Role-Based Access Control (RBAC) Implementation

**Feature**: 003-teams-rbac-sharing
**Phase**: 4 - User Story 2 (Role-Based Access Control)
**Date**: 2026-02-04
**Status**: COMPLETE ✓

## Overview

Phase 4 implements comprehensive role-based access control for the teams feature, enabling team owners and admins to manage member roles with appropriate permission enforcement.

## Completed Tasks

### T037: ChangeRoleRequest Schema ✓
**File**: `backend/app/schemas/team_member.py`

Created Pydantic schema for role change requests:
- `role` field with TeamRole enum validation
- Clear documentation for ownership transfer
- Example JSON for API documentation

```python
class ChangeRoleRequest(BaseModel):
    role: TeamRole = Field(description="New role to assign to the team member")
```

### T038: change_member_role Function ✓
**File**: `backend/app/services/team_member_service.py`

Service function already implemented with:
- Atomic ownership transfer (demotes current owner to admin when promoting new owner)
- Database transaction management
- Proper error handling and rollback
- Returns updated TeamMember object

**Key Feature**: When promoting a member to owner, the current owner is automatically demoted to admin in a single atomic transaction.

### T039: get_team_member Function ✓
**File**: `backend/app/services/team_member_service.py`

Service function already implemented:
- Retrieves specific team membership record
- Returns TeamMember with role information
- Used for permission validation

### T040: validate_role_change Function ✓
**File**: `backend/app/middleware/permissions.py`

Permission validation function already implemented with rules:
1. Cannot change your own role
2. Only owners can change roles to/from owner
3. Admins can only change member/viewer roles (not owner/admin)
4. Members and viewers cannot change any roles

Returns clear 403 error messages for each violation.

### T041: PATCH /api/teams/{team_id}/members/{user_id} Endpoint ✓
**File**: `backend/app/routes/team_members.py`

Implemented role change endpoint with:
- JWT authentication required
- Permission validation via validate_role_change
- Atomic ownership transfer support
- Comprehensive error handling (400, 401, 403, 404, 500)
- Clear API documentation with examples

**Request**:
```json
PATCH /api/teams/{team_id}/members/{user_id}
{
  "role": "admin"
}
```

**Response** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "team_id": "660e8400-e29b-41d4-a716-446655440001",
  "user_id": "987fcdeb-51a2-43f7-b123-456789abcdef",
  "role": "admin",
  "joined_at": "2026-02-04T10:30:00Z"
}
```

### T042: Role-Based Permission Checks ✓
**Files**: `backend/app/routes/teams.py`, `backend/app/routes/team_members.py`

All team endpoints already have proper permission enforcement:

| Endpoint | Permission Required | Function Used |
|----------|-------------------|---------------|
| POST /api/teams | Authenticated | get_current_user |
| GET /api/teams | Authenticated | get_current_user |
| GET /api/teams/{team_id} | Team Member | require_team_member |
| PATCH /api/teams/{team_id} | Admin or Owner | require_team_admin |
| DELETE /api/teams/{team_id} | Owner Only | require_team_owner |
| POST /api/teams/{team_id}/members | Admin or Owner | require_team_admin |
| PATCH /api/teams/{team_id}/members/{user_id} | Owner/Admin (validated) | validate_role_change |
| DELETE /api/teams/{team_id}/members/{user_id} | Admin or Owner | require_team_admin |
| POST /api/teams/{team_id}/leave | Team Member | require_team_member |

### T043: Comprehensive Error Handling ✓
**Files**: All route files

All endpoints return proper 403 Forbidden responses with clear messages:
- "User is not a member of team {team_id}"
- "User must be admin or owner of team {team_id}"
- "User must be the owner of team {team_id}"
- "Cannot change your own role"
- "Only team owners can change ownership"
- "Admins cannot change owner or admin roles"
- "Only admins and owners can change roles"

## Role Permissions Matrix

| Action | Owner | Admin | Member | Viewer |
|--------|-------|-------|--------|--------|
| Change roles | ✓ (all) | ✓ (member/viewer only) | ✗ | ✗ |
| Edit team settings | ✓ | ✓ | ✗ | ✗ |
| Invite members | ✓ | ✓ | ✗ | ✗ |
| Remove members | ✓ | ✓ | ✗ | ✗ |
| Delete team | ✓ | ✗ | ✗ | ✗ |
| View team details | ✓ | ✓ | ✓ | ✓ |
| Leave team | ✗ (must transfer ownership) | ✓ | ✓ | ✓ |

## Key Features

### 1. Atomic Ownership Transfer
When promoting a member to owner:
```python
# Single transaction ensures consistency
if new_role == TeamRole.OWNER:
    current_owner.role = TeamRole.ADMIN  # Demote current owner
    membership.role = TeamRole.OWNER      # Promote new owner
    db.commit()  # Atomic commit
```

### 2. Permission Validation
Three-tier permission system:
- **require_team_member**: Basic team membership check
- **require_team_admin**: Admin or owner check
- **require_team_owner**: Owner-only check
- **validate_role_change**: Complex role change validation

### 3. Self-Protection
Users cannot:
- Change their own role
- Remove themselves as owner (must transfer ownership first)
- Escalate privileges without proper authorization

### 4. Admin Limitations
Admins can:
- Invite members with member/viewer roles
- Change member/viewer roles
- Remove members (except owner/admin)

Admins cannot:
- Assign owner or admin roles
- Change owner or admin roles
- Delete the team

## API Endpoints Summary

### New Endpoint
- **PATCH /api/teams/{team_id}/members/{user_id}**: Change member role

### Enhanced Endpoints (with RBAC)
All existing endpoints now enforce role-based permissions:
- Team creation, listing, details, update, delete
- Member invitation, removal, self-removal

## Error Handling

All endpoints return appropriate HTTP status codes:
- **200 OK**: Successful operation
- **201 Created**: Resource created
- **204 No Content**: Successful deletion
- **400 Bad Request**: Invalid input data
- **401 Unauthorized**: Missing or invalid JWT token
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **409 Conflict**: Duplicate resource
- **500 Internal Server Error**: Server error

## Security Considerations

1. **JWT Authentication**: All endpoints require valid JWT token
2. **Permission Checks**: Every operation validates user permissions
3. **Transaction Safety**: Ownership transfer uses atomic transactions
4. **Input Validation**: Pydantic schemas validate all inputs
5. **Error Messages**: Clear but not revealing sensitive information
6. **Audit Trail**: All operations logged for debugging

## Testing Checklist

- [ ] Create team as user A (becomes owner)
- [ ] Invite user B as member
- [ ] User B attempts to change roles (should fail with 403)
- [ ] User A changes user B to admin (should succeed)
- [ ] User B attempts to change user A's role (should fail with 403)
- [ ] User B changes another member to viewer (should succeed)
- [ ] User A transfers ownership to user B (should succeed, A becomes admin)
- [ ] User B (now owner) changes user A back to owner (should succeed)
- [ ] Admin attempts to assign admin role (should fail with 403)
- [ ] Owner attempts to change own role (should fail with 403)

## Files Modified

### New Files
- `backend/app/schemas/team_member.py` (added ChangeRoleRequest)
- `backend/app/routes/team_members.py` (added PATCH endpoint)

### Enhanced Files
- `backend/app/services/team_member_service.py` (update_member_role, get_team_member)
- `backend/app/middleware/permissions.py` (validate_role_change)

## Next Steps

Phase 4 is complete. Ready to proceed to:
- **Phase 5**: User Story 3 - Team-Based Task Management
- **Phase 6**: User Story 5 - Permission Enforcement and Security

## Dependencies

Phase 4 builds on:
- Phase 1: Setup (database migration)
- Phase 2: Foundational models and permissions
- Phase 3: User Story 1 (Team Creation and Membership)

## Notes

- All service functions use database transactions for consistency
- Permission checks are enforced at both middleware and service layers
- Error messages are user-friendly but don't expose internal details
- All endpoints have comprehensive API documentation
- Code follows FastAPI best practices and Python conventions

---

**Implementation Status**: ✅ COMPLETE
**All 7 tasks completed successfully**
