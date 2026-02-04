# Tasks: Teams, RBAC, and Task Sharing

**Input**: Design documents from `/specs/003-teams-rbac-sharing/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Not explicitly requested in specification - test tasks omitted per template guidelines.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/app/`, `frontend/src/`
- Backend structure: `models/`, `schemas/`, `services/`, `routes/`, `middleware/`
- Frontend structure: `app/`, `components/`, `lib/`, `hooks/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and database migration setup

- [X] T001 Create database migration script for teams, team_members, and task_shares tables in backend/migrations/003_add_teams_rbac_sharing.py
- [X] T002 [P] Create TeamRole enum (owner/admin/member/viewer) in backend/app/models/team_member.py
- [X] T003 [P] Create SharePermission enum (view/edit) in backend/app/models/task_share.py
- [X] T004 Update backend/app/models/__init__.py to export new models

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 [P] Create Team SQLModel in backend/app/models/team.py with fields (id, name, description, owner_id, created_at, updated_at)
- [X] T006 [P] Create TeamMember SQLModel in backend/app/models/team_member.py with fields (id, team_id, user_id, role, joined_at) and unique constraint
- [X] T007 [P] Create TaskShare SQLModel in backend/app/models/task_share.py with fields (id, task_id, shared_with_user_id, shared_by_user_id, permission, shared_at) and unique constraint
- [X] T008 Extend Task SQLModel in backend/app/models/task.py to add nullable team_id field with foreign key to teams.id
- [X] T009 Update User SQLModel in backend/app/models/user.py to add relationships (owned_teams, team_memberships, received_shares, given_shares)
- [X] T010 [P] Create base permission checking functions in backend/app/middleware/permissions.py (require_team_role, require_team_admin, require_team_member, require_team_owner)
- [X] T011 [P] Create task access checking function (can_access_task, can_edit_task, can_delete_task) in backend/app/middleware/permissions.py
- [ ] T012 Run database migration to create tables and add indexes (Ready to run - migration script created)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

**Note**: T012 migration script is ready at `backend/migrations/003_add_teams_rbac_sharing.py`. Run when database is available.

---

## Phase 3: User Story 1 - Team Creation and Membership Management (Priority: P1) 🎯 MVP

**Goal**: Enable users to create teams, invite members, view membership, remove members, and leave teams

**Independent Test**: Create a team, invite members, verify membership list, remove a member, leave team (non-owner)

### Pydantic Schemas for User Story 1

- [X] T013 [P] [US1] Create TeamCreate schema in backend/app/schemas/team.py with name and description fields
- [X] T014 [P] [US1] Create TeamResponse schema in backend/app/schemas/team.py with all team fields
- [X] T015 [P] [US1] Create TeamUpdate schema in backend/app/schemas/team.py with optional name and description
- [X] T016 [P] [US1] Create TeamListResponse schema in backend/app/schemas/team.py with role and member_count
- [X] T017 [P] [US1] Create TeamDetailResponse schema in backend/app/schemas/team.py with members list
- [X] T018 [P] [US1] Create InviteMemberRequest schema in backend/app/schemas/team_member.py with user_id and role
- [X] T019 [P] [US1] Create TeamMemberResponse schema in backend/app/schemas/team_member.py

### Service Layer for User Story 1

- [X] T020 [US1] Implement create_team function in backend/app/services/team_service.py (creates team and adds owner as member in transaction)
- [X] T021 [US1] Implement get_user_teams function in backend/app/services/team_service.py (returns teams user is member of)
- [X] T022 [US1] Implement get_team_details function in backend/app/services/team_service.py (returns team with members list)
- [X] T023 [US1] Implement update_team function in backend/app/services/team_service.py (updates name/description)
- [X] T024 [US1] Implement delete_team function in backend/app/services/team_service.py (deletes team and converts tasks to personal in transaction)
- [X] T025 [US1] Implement invite_member function in backend/app/services/team_member_service.py (adds user to team with role)
- [X] T026 [US1] Implement remove_member function in backend/app/services/team_member_service.py (removes user from team)
- [X] T027 [US1] Implement leave_team function in backend/app/services/team_member_service.py (self-removal, prevents owner from leaving)

### API Routes for User Story 1

- [X] T028 [US1] Implement POST /api/teams endpoint in backend/app/routes/teams.py (create team)
- [X] T029 [US1] Implement GET /api/teams endpoint in backend/app/routes/teams.py (list user's teams)
- [X] T030 [US1] Implement GET /api/teams/{team_id} endpoint in backend/app/routes/teams.py (get team details with permission check)
- [X] T031 [US1] Implement PATCH /api/teams/{team_id} endpoint in backend/app/routes/teams.py (update team with admin permission check)
- [X] T032 [US1] Implement DELETE /api/teams/{team_id} endpoint in backend/app/routes/teams.py (delete team with owner permission check)
- [X] T033 [US1] Implement POST /api/teams/{team_id}/members endpoint in backend/app/routes/team_members.py (invite member with admin permission check)
- [X] T034 [US1] Implement DELETE /api/teams/{team_id}/members/{user_id} endpoint in backend/app/routes/team_members.py (remove member with admin permission check)
- [X] T035 [US1] Implement POST /api/teams/{team_id}/leave endpoint in backend/app/routes/team_members.py (leave team)
- [X] T036 [US1] Register team and team_member routes in backend/app/main.py

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Role-Based Access Control (Priority: P1)

**Goal**: Enable team owners to assign different roles (owner/admin/member/viewer) to team members with appropriate permission enforcement

**Independent Test**: Assign different roles to users and verify each role has correct permissions (admin can manage, member can create tasks, viewer can only view)

### Pydantic Schemas for User Story 2

- [X] T037 [P] [US2] Create ChangeRoleRequest schema in backend/app/schemas/team_member.py with role field

### Service Layer for User Story 2

- [X] T038 [US2] Implement change_member_role function in backend/app/services/team_member_service.py (handles ownership transfer atomically if promoting to owner)
- [X] T039 [US2] Implement get_team_member function in backend/app/services/team_member_service.py (retrieves member with role)
- [X] T040 [US2] Implement validate_role_change function in backend/app/services/team_member_service.py (ensures admins can't change owner role)

### API Routes for User Story 2

- [X] T041 [US2] Implement PATCH /api/teams/{team_id}/members/{user_id} endpoint in backend/app/routes/team_members.py (change member role with permission validation)

### Permission Enforcement for User Story 2

- [X] T042 [US2] Add role-based permission checks to all team endpoints (verify owner/admin/member/viewer permissions)
- [X] T043 [US2] Add comprehensive error handling for permission denied scenarios (return 403 with clear messages)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently with proper RBAC enforcement

---

## Phase 5: User Story 3 - Team-Based Task Management (Priority: P1)

**Goal**: Enable team members to create tasks associated with teams, with visibility based on team membership and role permissions

**Independent Test**: Create tasks assigned to a team, verify all team members can view them, verify role-based edit/delete permissions

### Pydantic Schemas for User Story 3

- [X] T044 [P] [US3] Extend TaskCreate schema in backend/app/schemas/task.py to add optional team_id field
- [X] T045 [P] [US3] Extend TaskResponse schema in backend/app/schemas/task.py to add team_id and access_type fields

### Service Layer for User Story 3

- [X] T046 [US3] Extend create_task function in backend/app/services/task_service.py to support team_id and validate team membership
- [X] T047 [US3] Extend get_user_tasks function in backend/app/services/task_service.py to include team tasks (union of personal, team, and shared)
- [X] T048 [US3] Extend get_task_by_id function in backend/app/services/task_service.py to check team access permissions
- [X] T049 [US3] Extend update_task function in backend/app/services/task_service.py to enforce team role permissions (owner/admin can edit all, member can edit own)
- [X] T050 [US3] Extend delete_task function in backend/app/services/task_service.py to enforce team role permissions (owner/admin can delete)

### API Routes for User Story 3

- [X] T051 [US3] Extend POST /api/tasks endpoint in backend/app/routes/tasks.py to accept team_id and validate team membership
- [X] T052 [US3] Extend GET /api/tasks endpoint in backend/app/routes/tasks.py to support team_id filter and return accessible tasks
- [X] T053 [US3] Extend GET /api/tasks/{task_id} endpoint in backend/app/routes/tasks.py to check team access permissions
- [X] T054 [US3] Extend PATCH /api/tasks/{task_id} endpoint in backend/app/routes/tasks.py to enforce team role permissions
- [X] T055 [US3] Extend DELETE /api/tasks/{task_id} endpoint in backend/app/routes/tasks.py to enforce team role permissions

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently with team-based task management

---

## Phase 6: User Story 5 - Permission Enforcement and Security (Priority: P1)

**Goal**: Ensure all role-based and sharing permissions are enforced at the API level, preventing unauthorized access

**Independent Test**: Attempt unauthorized actions through direct API calls and verify they are blocked with appropriate HTTP status codes (401/403)

### Security Implementation for User Story 5

- [X] T056 [P] [US5] Add JWT authentication check to all team endpoints in backend/app/routes/teams.py (return 401 if not authenticated)
- [X] T057 [P] [US5] Add JWT authentication check to all team_member endpoints in backend/app/routes/team_members.py (return 401 if not authenticated)
- [X] T058 [P] [US5] Add JWT authentication check to all extended task endpoints in backend/app/routes/tasks.py (return 401 if not authenticated)
- [X] T059 [US5] Add permission validation to all privileged operations (verify user has required role before executing)
- [X] T060 [US5] Add cross-team access prevention (verify user cannot access other teams' data)
- [X] T061 [US5] Add logging for all permission-related errors in backend/app/middleware/permissions.py
- [X] T062 [US5] Implement database transaction management for all multi-record operations (team creation, ownership transfer, team deletion)

**Checkpoint**: All P1 user stories (1, 2, 3, 5) should now be complete with comprehensive security enforcement

---

## Phase 7: User Story 4 - Direct Task Sharing Between Users (Priority: P2)

**Goal**: Enable users to share specific tasks with other users outside team context, with view or edit permissions

**Independent Test**: Share a task with another user with edit permission, verify they can access and modify it; share with view permission, verify read-only access

### Pydantic Schemas for User Story 4

- [X] T063 [P] [US4] Create ShareTaskRequest schema in backend/app/schemas/task_share.py with user_id and permission fields
- [X] T064 [P] [US4] Create TaskShareResponse schema in backend/app/schemas/task_share.py
- [X] T065 [P] [US4] Create SharedTaskResponse schema in backend/app/schemas/task_share.py with owner_email and permission

### Service Layer for User Story 4

- [X] T066 [US4] Implement share_task function in backend/app/services/task_share_service.py (creates share record, prevents self-sharing)
- [X] T067 [US4] Implement revoke_share function in backend/app/services/task_share_service.py (removes share record)
- [X] T068 [US4] Implement get_shared_tasks function in backend/app/services/task_share_service.py (returns tasks shared with user)
- [X] T069 [US4] Implement get_task_shares function in backend/app/services/task_share_service.py (returns all shares for a task)
- [X] T070 [US4] Extend can_access_task function in backend/app/middleware/permissions.py to check task shares (already implemented in Phase 2)
- [X] T071 [US4] Extend can_edit_task function in backend/app/middleware/permissions.py to check edit share permission (already implemented in Phase 2)

### API Routes for User Story 4

- [X] T072 [US4] Implement POST /api/tasks/{task_id}/share endpoint in backend/app/routes/task_shares.py (share task with owner permission check)
- [X] T073 [US4] Implement DELETE /api/tasks/{task_id}/share/{user_id} endpoint in backend/app/routes/task_shares.py (revoke share with owner permission check)
- [X] T074 [US4] Implement GET /api/tasks/shared-with-me endpoint in backend/app/routes/task_shares.py (list shared tasks)
- [X] T075 [US4] Extend GET /api/tasks/{task_id} endpoint in backend/app/routes/tasks.py to include shared_with list for task owner
- [X] T076 [US4] Register task_share routes in backend/app/main.py

**Checkpoint**: All user stories (1, 2, 3, 4, 5) should now be independently functional

---

## Phase 8: Frontend - Team Management UI (Priority: P2)

**Purpose**: Build user interface for team creation, membership management, and role assignment

### Frontend Type Definitions

- [X] T077 [P] Create Team type in frontend/src/lib/types/team.ts with all team fields
- [X] T078 [P] Create TeamMember type in frontend/src/lib/types/team.ts with role enum
- [X] T079 [P] Create TeamRole enum in frontend/src/lib/types/team.ts (owner/admin/member/viewer)

### Frontend API Client

- [X] T080 [P] Create createTeam function in frontend/src/lib/api/teams.ts
- [X] T081 [P] Create getUserTeams function in frontend/src/lib/api/teams.ts
- [X] T082 [P] Create getTeamDetails function in frontend/src/lib/api/teams.ts
- [X] T083 [P] Create updateTeam function in frontend/src/lib/api/teams.ts
- [X] T084 [P] Create deleteTeam function in frontend/src/lib/api/teams.ts
- [X] T085 [P] Create inviteMember function in frontend/src/lib/api/teams.ts
- [X] T086 [P] Create changeMemberRole function in frontend/src/lib/api/teams.ts
- [X] T087 [P] Create removeMember function in frontend/src/lib/api/teams.ts
- [X] T088 [P] Create leaveTeam function in frontend/src/lib/api/teams.ts

### Frontend Hooks

- [X] T089 Create useTeams hook in frontend/src/hooks/useTeams.ts (fetch and manage user's teams)
- [X] T090 Create useTeamDetails hook in frontend/src/hooks/useTeamDetails.ts (fetch and manage team details)

### Frontend Components

- [X] T091 [P] Create TeamCard component in frontend/src/components/teams/TeamCard.tsx (displays team summary)
- [X] T092 [P] Create TeamList component in frontend/src/components/teams/TeamList.tsx (displays list of teams)
- [X] T093 [P] Create TeamForm component in frontend/src/components/teams/TeamForm.tsx (create/edit team form)
- [X] T094 [P] Create MemberList component in frontend/src/components/teams/MemberList.tsx (displays team members with roles)
- [X] T095 [P] Create MemberInvite component in frontend/src/components/teams/MemberInvite.tsx (invite member form)
- [X] T096 [P] Create RoleSelector component in frontend/src/components/teams/RoleSelector.tsx (change member role dropdown)

### Frontend Pages

- [X] T097 Create teams list page in frontend/src/app/(protected)/teams/page.tsx (shows user's teams)
- [X] T098 Create team detail page in frontend/src/app/(protected)/teams/[teamId]/page.tsx (shows team details and members)
- [X] T099 Create team settings page in frontend/src/app/(protected)/teams/[teamId]/settings/page.tsx (edit team settings)
- [X] T100 Create new team page in frontend/src/app/(protected)/teams/new/page.tsx (create team form)

---

## Phase 9: Frontend - Task Sharing UI (Priority: P2)

**Purpose**: Build user interface for sharing tasks with other users

### Frontend Type Definitions

- [X] T101 [P] Create TaskShare type in frontend/src/lib/types/share.ts with permission enum
- [X] T102 [P] Create SharePermission enum in frontend/src/lib/types/share.ts (view/edit)

### Frontend API Client

- [X] T103 [P] Create shareTask function in frontend/src/lib/api/shares.ts
- [X] T104 [P] Create revokeShare function in frontend/src/lib/api/shares.ts
- [X] T105 [P] Create getSharedTasks function in frontend/src/lib/api/shares.ts

### Frontend Hooks

- [X] T106 Create useShares hook in frontend/src/hooks/useShares.ts (manage task sharing)

### Frontend Components

- [X] T107 [P] Create ShareTaskModal component in frontend/src/components/shared/ShareTaskModal.tsx (share task dialog)
- [X] T108 [P] Create SharedTaskList component in frontend/src/components/shared/SharedTaskList.tsx (displays shared tasks)

### Frontend Pages

- [X] T109 Create shared tasks page in frontend/src/app/(protected)/shared/page.tsx (shows tasks shared with user)

---

## Phase 10: Frontend - Extended Task Management (Priority: P2)

**Purpose**: Extend existing task components to support team context

### Frontend Updates

- [X] T110 Extend Task type in frontend/src/lib/types/task.ts to add team_id and access_type fields
- [X] T111 Extend createTask function in frontend/src/lib/api/tasks.ts to support team_id parameter
- [X] T112 Extend getTask function in frontend/src/lib/api/tasks.ts to include team and sharing information
- [X] T113 Extend useTasks hook in frontend/src/hooks/useTasks.ts to support team filtering
- [X] T114 Update task creation form to include team selection dropdown (if user is member of teams)
- [X] T115 Update task list to show team badge/indicator for team tasks
- [X] T116 Update task detail view to show team information and share button

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T117 [P] Add comprehensive error handling with user-friendly messages across all endpoints
- [ ] T118 [P] Add loading states and optimistic updates to all frontend operations
- [ ] T119 [P] Add input validation and sanitization to all forms
- [ ] T120 Add database indexes for performance (team_id, user_id lookups) if not already created in migration
- [ ] T121 [P] Add API response caching for frequently accessed data (team lists, member lists)
- [ ] T122 Verify backward compatibility by testing existing personal task functionality
- [ ] T123 Run performance tests with large teams (100+ members) and many shares (1000+)
- [ ] T124 Security audit: attempt unauthorized access patterns and verify all are blocked
- [ ] T125 Update API documentation with all new endpoints
- [ ] T126 Run quickstart.md validation checklist

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - US1, US2, US3, US5 (P1) can proceed in parallel after Foundational
  - US4 (P2) can proceed in parallel with P1 stories or after them
- **Frontend (Phase 8-10)**: Depends on corresponding backend user stories being complete
- **Polish (Phase 11)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Integrates with US1 but independently testable
- **User Story 3 (P1)**: Can start after Foundational (Phase 2) - Integrates with US1/US2 but independently testable
- **User Story 5 (P1)**: Can start after Foundational (Phase 2) - Cross-cutting security for all stories
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - Independent of other stories

### Within Each User Story

- Schemas before services (schemas define contracts)
- Services before routes (routes use services)
- Permission checks integrated throughout
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational models marked [P] can run in parallel (T005-T009)
- All Foundational permission functions marked [P] can run in parallel (T010-T011)
- Once Foundational phase completes, all P1 user stories (US1, US2, US3, US5) can start in parallel
- All schemas within a story marked [P] can run in parallel
- All frontend type definitions marked [P] can run in parallel
- All frontend API client functions marked [P] can run in parallel
- All frontend components marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all schemas for User Story 1 together:
Task: "Create TeamCreate schema in backend/app/schemas/team.py"
Task: "Create TeamResponse schema in backend/app/schemas/team.py"
Task: "Create TeamUpdate schema in backend/app/schemas/team.py"
Task: "Create TeamListResponse schema in backend/app/schemas/team.py"
Task: "Create TeamDetailResponse schema in backend/app/schemas/team.py"
Task: "Create InviteMemberRequest schema in backend/app/schemas/team_member.py"
Task: "Create TeamMemberResponse schema in backend/app/schemas/team_member.py"
```

---

## Parallel Example: Foundational Phase

```bash
# Launch all models together:
Task: "Create Team SQLModel in backend/app/models/team.py"
Task: "Create TeamMember SQLModel in backend/app/models/team_member.py"
Task: "Create TaskShare SQLModel in backend/app/models/task_share.py"

# Launch all permission functions together:
Task: "Create base permission checking functions in backend/app/middleware/permissions.py"
Task: "Create task access checking function in backend/app/middleware/permissions.py"
```

---

## Implementation Strategy

### MVP First (User Stories 1, 2, 3, 5 Only - All P1)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Team Creation & Membership)
4. Complete Phase 4: User Story 2 (RBAC)
5. Complete Phase 5: User Story 3 (Team-Based Tasks)
6. Complete Phase 6: User Story 5 (Permission Enforcement)
7. **STOP and VALIDATE**: Test all P1 stories independently
8. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 5 → Test independently → Deploy/Demo (MVP complete!)
6. Add User Story 4 → Test independently → Deploy/Demo
7. Add Frontend (Phase 8-10) → Test independently → Deploy/Demo
8. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Team Creation)
   - Developer B: User Story 2 (RBAC)
   - Developer C: User Story 3 (Team Tasks)
   - Developer D: User Story 5 (Security)
3. Stories complete and integrate independently
4. Developer E: User Story 4 (Task Sharing) - can start anytime after Foundational
5. Frontend team: Phase 8-10 (after backend stories complete)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Tests not included per specification (not explicitly requested)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- All tasks follow strict checklist format: `- [ ] [ID] [P?] [Story?] Description with file path`

---

## Summary

**Total Tasks**: 126
**Task Distribution**:
- Phase 1 (Setup): 4 tasks
- Phase 2 (Foundational): 8 tasks
- Phase 3 (US1 - Team Creation): 24 tasks
- Phase 4 (US2 - RBAC): 7 tasks
- Phase 5 (US3 - Team Tasks): 12 tasks
- Phase 6 (US5 - Security): 7 tasks
- Phase 7 (US4 - Task Sharing): 14 tasks
- Phase 8 (Frontend - Teams): 24 tasks
- Phase 9 (Frontend - Sharing): 9 tasks
- Phase 10 (Frontend - Tasks): 7 tasks
- Phase 11 (Polish): 10 tasks

**Parallel Opportunities**: 67 tasks marked [P] can run in parallel within their phase
**Independent Stories**: All 5 user stories can be implemented and tested independently
**MVP Scope**: User Stories 1, 2, 3, 5 (all P1) = 50 backend tasks
**Format Validation**: ✅ All tasks follow checklist format with ID, optional [P], optional [Story], and file paths
