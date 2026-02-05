# Feature Specification: Teams, RBAC, and Task Sharing

**Feature Branch**: `003-teams-rbac-sharing`
**Created**: 2026-02-04
**Status**: Draft
**Dependencies**: Spec 001 (backend-core-data), Spec 002 (auth-api-security)
**Input**: User description: "Teams, RBAC, and Task Sharing - Enable multi-user collaboration with team-based task management, role-based access control, and secure task sharing"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Team Creation and Membership Management (Priority: P1)

As a user, I want to create teams and invite other users to join them, so that I can collaborate with others on shared tasks.

**Why this priority**: This is the foundational capability that enables all other collaboration features. Without teams, there's no context for roles or sharing.

**Independent Test**: Can be fully tested by creating a team, inviting members, and verifying membership list. Delivers immediate value by establishing collaboration groups.

**Acceptance Scenarios**:

1. **Given** I am an authenticated user, **When** I create a new team with a name and description, **Then** the team is created with me as the owner
2. **Given** I am a team owner, **When** I invite a user by email to join my team, **Then** the user receives an invitation and can accept to become a member
3. **Given** I am a team owner or admin, **When** I view the team members list, **Then** I see all members with their roles and join dates
4. **Given** I am a team owner or admin, **When** I remove a member from the team, **Then** that user loses access to all team tasks
5. **Given** I am a team member, **When** I leave a team, **Then** I no longer have access to team tasks (unless I'm the owner)

---

### User Story 2 - Role-Based Access Control (Priority: P1)

As a team owner, I want to assign different roles to team members, so that I can control who can perform administrative actions versus who can only view or contribute.

**Why this priority**: RBAC is critical for security and proper team management. Without it, all members would have equal permissions, creating security and management issues.

**Independent Test**: Can be tested by assigning different roles to users and verifying that each role has appropriate permissions. Delivers value by enabling proper access control.

**Acceptance Scenarios**:

1. **Given** I am a team owner, **When** I assign the "admin" role to a member, **Then** that member can manage team settings and member roles (except owner)
2. **Given** I am a team owner, **When** I assign the "member" role to a user, **Then** that user can create, edit, and delete their own tasks within the team
3. **Given** I am a team owner, **When** I assign the "viewer" role to a user, **Then** that user can only view team tasks but cannot modify them
4. **Given** I am a team admin, **When** I try to change the owner's role, **Then** the system prevents this action
5. **Given** I am a team member with "member" role, **When** I try to change another member's role, **Then** the system denies the request

---

### User Story 3 - Team-Based Task Management (Priority: P1)

As a team member, I want to create tasks that belong to my team, so that all team members can see and collaborate on shared work.

**Why this priority**: This is the core value proposition - enabling collaborative task management. Without this, teams would be meaningless.

**Independent Test**: Can be tested by creating tasks associated with a team and verifying visibility based on team membership and roles.

**Acceptance Scenarios**:

1. **Given** I am a team member, **When** I create a task and assign it to my team, **Then** all team members can view the task
2. **Given** I am a team member, **When** I view my team's task list, **Then** I see all tasks created by any team member
3. **Given** I am a team member with "member" role, **When** I edit a task I created, **Then** the changes are saved and visible to all team members
4. **Given** I am a team viewer, **When** I try to edit a team task, **Then** the system prevents the modification
5. **Given** I am not a team member, **When** I try to access a team's tasks, **Then** the system denies access

---

### User Story 4 - Direct Task Sharing Between Users (Priority: P2)

As a user, I want to share specific tasks with other users outside my team, so that I can collaborate on individual tasks without requiring team membership.

**Why this priority**: Enables flexible collaboration for one-off tasks or cross-team work without the overhead of team management.

**Independent Test**: Can be tested by sharing a task with a specific user and verifying they can access it with the specified permission level.

**Acceptance Scenarios**:

1. **Given** I own a task, **When** I share it with another user with "edit" permission, **Then** that user can view and modify the task
2. **Given** I own a task, **When** I share it with another user with "view" permission, **Then** that user can only view the task
3. **Given** I have a task shared with me, **When** I view my shared tasks list, **Then** I see all tasks others have shared with me
4. **Given** I own a task, **When** I revoke sharing access from a user, **Then** that user can no longer access the task
5. **Given** I have "edit" permission on a shared task, **When** I try to delete the task, **Then** the system prevents deletion (only owner can delete)

---

### User Story 5 - Permission Enforcement and Security (Priority: P1)

As a system, I must enforce all role-based and sharing permissions at the API level, so that unauthorized access is prevented regardless of client implementation.

**Why this priority**: Security is non-negotiable. Without proper enforcement, the entire RBAC and sharing system would be vulnerable.

**Independent Test**: Can be tested by attempting unauthorized actions through direct API calls and verifying they are blocked.

**Acceptance Scenarios**:

1. **Given** I am not authenticated, **When** I try to access any team or shared task endpoint, **Then** the system returns 401 Unauthorized
2. **Given** I am authenticated but not a team member, **When** I try to access team tasks, **Then** the system returns 403 Forbidden
3. **Given** I am a team viewer, **When** I try to create a task via API, **Then** the system returns 403 Forbidden
4. **Given** I have "view" permission on a shared task, **When** I try to update it via API, **Then** the system returns 403 Forbidden
5. **Given** I am a team member, **When** I try to access another team's tasks, **Then** the system returns 403 Forbidden

---

### Edge Cases

- What happens when a team owner leaves the team? (System should prevent this or require ownership transfer)
- What happens when a user is removed from a team but has tasks shared directly with them? (Direct shares persist independently)
- How does the system handle circular permission scenarios? (e.g., User A shares with User B who shares with User A)
- What happens when a task is both team-owned and directly shared? (Team permissions take precedence for team members)
- How does the system handle role changes for users with active sessions? (Permissions should be re-validated on each request)
- What happens when a team is deleted? (All team tasks should be handled - either deleted or transferred)
- How does the system handle concurrent role changes? (Use database transactions to prevent race conditions)

## Requirements *(mandatory)*

### Functional Requirements

#### Team Management
- **FR-001**: System MUST allow authenticated users to create teams with a unique name and optional description
- **FR-002**: System MUST assign the creator as the team owner with full administrative privileges
- **FR-003**: System MUST allow team owners and admins to invite users to join teams by email or user ID
- **FR-004**: System MUST allow team owners and admins to remove members from teams
- **FR-005**: System MUST allow team members to leave teams (except owners must transfer ownership first)
- **FR-006**: System MUST maintain a complete audit trail of team membership changes

#### Role-Based Access Control
- **FR-007**: System MUST support exactly four roles: Owner, Admin, Member, Viewer
- **FR-008**: System MUST enforce that each team has exactly one owner at all times
- **FR-009**: System MUST allow owners to assign any role to members (including promoting to owner, which demotes current owner)
- **FR-010**: System MUST allow admins to assign Member or Viewer roles only
- **FR-011**: System MUST prevent members and viewers from changing any roles
- **FR-012**: System MUST enforce role-based permissions on all API endpoints

**Role Permissions Matrix**:
| Action | Owner | Admin | Member | Viewer |
|--------|-------|-------|--------|--------|
| Create team | ✓ | ✗ | ✗ | ✗ |
| Delete team | ✓ | ✗ | ✗ | ✗ |
| Edit team settings | ✓ | ✓ | ✗ | ✗ |
| Invite members | ✓ | ✓ | ✗ | ✗ |
| Remove members | ✓ | ✓ | ✗ | ✗ |
| Change roles | ✓ (all) | ✓ (Member/Viewer only) | ✗ | ✗ |
| Create team tasks | ✓ | ✓ | ✓ | ✗ |
| Edit own team tasks | ✓ | ✓ | ✓ | ✗ |
| Edit others' team tasks | ✓ | ✓ | ✗ | ✗ |
| Delete team tasks | ✓ | ✓ | ✗ (own only) | ✗ |
| View team tasks | ✓ | ✓ | ✓ | ✓ |

#### Team-Based Task Management
- **FR-013**: System MUST allow tasks to be associated with a team (team_id field)
- **FR-014**: System MUST allow team members with appropriate roles to create tasks for their team
- **FR-015**: System MUST filter task lists to show only tasks the user has permission to view
- **FR-016**: System MUST enforce that team tasks are only accessible to team members
- **FR-017**: System MUST maintain backward compatibility with personal tasks (tasks without team_id)

#### Direct Task Sharing
- **FR-018**: System MUST allow task owners to share tasks with specific users
- **FR-019**: System MUST support two sharing permission levels: "view" and "edit"
- **FR-020**: System MUST allow task owners to revoke sharing access at any time
- **FR-021**: System MUST allow users to view all tasks shared with them
- **FR-022**: System MUST prevent users with "view" permission from modifying shared tasks
- **FR-023**: System MUST prevent users with "edit" permission from deleting shared tasks (only owner can delete)

#### Security Requirements
- **FR-024**: System MUST verify JWT authentication on all team and sharing endpoints
- **FR-025**: System MUST validate user permissions before executing any privileged operation
- **FR-026**: System MUST prevent privilege escalation attacks
- **FR-027**: System MUST prevent unauthorized access to team data through direct API calls
- **FR-028**: System MUST log all permission-related errors for security auditing
- **FR-029**: System MUST use database transactions for operations that modify multiple records

### Key Entities

- **Team**: Represents a collaboration group with a name, description, owner, and members. Has one-to-many relationship with tasks and team members.

- **TeamMember**: Represents the association between a user and a team, including their role (owner/admin/member/viewer) and join date. Junction table between users and teams.

- **TaskShare**: Represents direct sharing of a task with a specific user, including permission level (view/edit) and share date. Enables task collaboration outside team context.

- **Task (Extended)**: Existing task entity extended with optional team_id foreign key to support team-based tasks while maintaining backward compatibility with personal tasks.

- **User (Existing)**: Existing user entity from Spec 002, no modifications needed.

### Data Model Extensions

#### New Tables

**teams**:
- `id` (UUID, primary key)
- `name` (VARCHAR, unique, not null)
- `description` (TEXT, nullable)
- `owner_id` (UUID, foreign key to users.id, not null)
- `created_at` (TIMESTAMP, not null)
- `updated_at` (TIMESTAMP, not null)

**team_members**:
- `id` (UUID, primary key)
- `team_id` (UUID, foreign key to teams.id, not null)
- `user_id` (UUID, foreign key to users.id, not null)
- `role` (ENUM: 'owner', 'admin', 'member', 'viewer', not null)
- `joined_at` (TIMESTAMP, not null)
- Unique constraint on (team_id, user_id)

**task_shares**:
- `id` (UUID, primary key)
- `task_id` (UUID, foreign key to tasks.id, not null)
- `shared_with_user_id` (UUID, foreign key to users.id, not null)
- `shared_by_user_id` (UUID, foreign key to users.id, not null)
- `permission` (ENUM: 'view', 'edit', not null)
- `shared_at` (TIMESTAMP, not null)
- Unique constraint on (task_id, shared_with_user_id)

#### Modified Tables

**tasks** (extend existing):
- Add `team_id` (UUID, foreign key to teams.id, nullable) - null means personal task

### API Surface

#### Team Endpoints

**POST /api/teams**
- Create a new team
- Request: `{ name, description? }`
- Response: `{ id, name, description, owner_id, created_at }`
- Auth: Required
- Permission: Any authenticated user

**GET /api/teams**
- List all teams the user is a member of
- Response: `[{ id, name, description, role, member_count }]`
- Auth: Required

**GET /api/teams/{team_id}**
- Get team details
- Response: `{ id, name, description, owner_id, members: [{ user_id, email, role, joined_at }] }`
- Auth: Required
- Permission: Team member

**PATCH /api/teams/{team_id}**
- Update team settings
- Request: `{ name?, description? }`
- Response: `{ id, name, description, updated_at }`
- Auth: Required
- Permission: Owner or Admin

**DELETE /api/teams/{team_id}**
- Delete a team
- Response: `{ message: "Team deleted" }`
- Auth: Required
- Permission: Owner only

#### Team Membership Endpoints

**POST /api/teams/{team_id}/members**
- Invite a user to join the team
- Request: `{ user_id, role: 'admin' | 'member' | 'viewer' }`
- Response: `{ team_id, user_id, role, joined_at }`
- Auth: Required
- Permission: Owner or Admin

**PATCH /api/teams/{team_id}/members/{user_id}**
- Change a member's role
- Request: `{ role: 'owner' | 'admin' | 'member' | 'viewer' }`
- Response: `{ team_id, user_id, role, updated_at }`
- Auth: Required
- Permission: Owner (all roles), Admin (member/viewer only)

**DELETE /api/teams/{team_id}/members/{user_id}**
- Remove a member from the team
- Response: `{ message: "Member removed" }`
- Auth: Required
- Permission: Owner or Admin (cannot remove owner)

**POST /api/teams/{team_id}/leave**
- Leave a team (self-removal)
- Response: `{ message: "Left team" }`
- Auth: Required
- Permission: Any member except owner

#### Extended Task Endpoints

**POST /api/tasks**
- Create a task (personal or team)
- Request: `{ title, description?, completed?, team_id? }`
- Response: `{ id, title, description, completed, user_id, team_id?, created_at }`
- Auth: Required
- Permission: If team_id provided, must be team member with create permission

**GET /api/tasks**
- List all tasks accessible to the user (personal + team + shared)
- Query params: `?team_id={id}` (filter by team), `?shared=true` (only shared tasks)
- Response: `[{ id, title, description, completed, user_id, team_id?, is_shared, permission }]`
- Auth: Required

**GET /api/tasks/{task_id}**
- Get task details
- Response: `{ id, title, description, completed, user_id, team_id?, shared_with: [{ user_id, permission }] }`
- Auth: Required
- Permission: Owner, team member, or has share access

**PATCH /api/tasks/{task_id}**
- Update a task
- Request: `{ title?, description?, completed? }`
- Response: `{ id, title, description, completed, updated_at }`
- Auth: Required
- Permission: Owner, team admin/owner, or has "edit" share permission

**DELETE /api/tasks/{task_id}**
- Delete a task
- Response: `{ message: "Task deleted" }`
- Auth: Required
- Permission: Owner only (team admins/owners can delete team tasks)

#### Task Sharing Endpoints

**POST /api/tasks/{task_id}/share**
- Share a task with a user
- Request: `{ user_id, permission: 'view' | 'edit' }`
- Response: `{ task_id, shared_with_user_id, permission, shared_at }`
- Auth: Required
- Permission: Task owner only

**DELETE /api/tasks/{task_id}/share/{user_id}**
- Revoke task sharing
- Response: `{ message: "Share revoked" }`
- Auth: Required
- Permission: Task owner only

**GET /api/tasks/shared-with-me**
- List all tasks shared with the current user
- Response: `[{ id, title, description, completed, owner_email, permission, shared_at }]`
- Auth: Required

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can create a team and invite members in under 1 minute
- **SC-002**: Role-based permissions are enforced on 100% of API endpoints with appropriate HTTP status codes (401/403)
- **SC-003**: Users can share a task with another user and verify access in under 30 seconds
- **SC-004**: System handles concurrent team operations (10+ simultaneous requests) without data corruption
- **SC-005**: All team and sharing operations complete within 500ms at p95 latency
- **SC-006**: Zero security vulnerabilities related to unauthorized access in security audit
- **SC-007**: 100% backward compatibility - existing personal tasks continue to work without modification
- **SC-008**: All database operations use transactions to ensure data consistency

### Technical Validation

- All new endpoints have comprehensive test coverage (unit + integration tests)
- Permission enforcement is tested for all role combinations
- Database migrations are reversible and tested
- API documentation is complete and accurate
- Security audit passes with no critical or high-severity findings

### User Experience Validation

- Team creation and management flows are intuitive and require no documentation
- Permission denied errors provide clear, actionable messages
- Users can easily distinguish between personal, team, and shared tasks
- Role changes take effect immediately without requiring logout/login

## Implementation Notes

### Architecture Principles

1. **Additive Only**: All changes must be backward compatible. Existing personal task functionality must continue to work unchanged.

2. **Security First**: Permission checks must happen at the API layer, not just in the UI. Never trust client-side validation.

3. **Database Integrity**: Use foreign keys, unique constraints, and transactions to maintain data consistency.

4. **Clear Separation**: Team-based access and direct sharing are independent systems that can work together but don't depend on each other.

5. **Audit Trail**: Log all permission changes and access denials for security monitoring.

### Migration Strategy

1. Create new tables (teams, team_members, task_shares) without modifying existing tables
2. Add team_id column to tasks table as nullable foreign key
3. Existing tasks remain personal (team_id = null)
4. New tasks can optionally be assigned to teams
5. No data migration needed - all existing functionality preserved

### Testing Strategy

1. **Unit Tests**: Test each permission check function in isolation
2. **Integration Tests**: Test complete API flows with different role combinations
3. **Security Tests**: Attempt unauthorized access patterns and verify they're blocked
4. **Performance Tests**: Verify query performance with large teams and many shared tasks
5. **Backward Compatibility Tests**: Verify existing personal task tests still pass

## Out of Scope

- Team task templates or workflows
- Task assignment to specific team members (tasks are team-level, not assigned to individuals)
- Team activity feeds or notifications
- Bulk operations (bulk invite, bulk share)
- Team hierarchies or nested teams
- Advanced permissions (custom roles, granular permissions)
- Task comments or discussions
- File attachments to tasks
- Task dependencies or subtasks
- Calendar integration
- Email notifications for team invites or task shares
- Team analytics or reporting
