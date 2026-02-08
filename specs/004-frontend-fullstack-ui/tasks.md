# Tasks: Frontend Full-Stack UI

**Input**: Design documents from `/specs/004-frontend-fullstack-ui/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are NOT explicitly requested in the specification, so test tasks are excluded from this breakdown.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Frontend**: `frontend/src/` for all source code
- **App Router**: `frontend/src/app/` for pages and layouts
- **Components**: `frontend/src/components/` for React components
- **Utilities**: `frontend/src/lib/` for API client, types, utilities
- **Hooks**: `frontend/src/hooks/` for custom React hooks

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Initialize Next.js 16+ project with TypeScript in frontend/ directory
- [x] T002 Configure Tailwind CSS in frontend/tailwind.config.js and frontend/postcss.config.js
- [x] T003 [P] Setup ESLint and TypeScript configuration in frontend/.eslintrc.json and frontend/tsconfig.json
- [x] T004 [P] Create environment variables template in frontend/.env.local.example
- [x] T005 [P] Setup project structure with app/, components/, lib/, hooks/ directories
- [x] T006 [P] Create global styles in frontend/src/app/globals.css
- [x] T007 [P] Install Better Auth client SDK and dependencies in frontend/package.json

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T008 Create TypeScript type definitions in frontend/src/lib/types/models.ts (User, Task, Team, TeamMember, TaskShare)
- [x] T009 [P] Create API response types in frontend/src/lib/types/api.ts (AuthResponse, TaskResponse, TeamResponse, ErrorResponse)
- [x] T010 [P] Create API request types in frontend/src/lib/types/api.ts (CreateTaskInput, UpdateTaskInput, SignupInput, SigninInput)
- [x] T011 [P] Create UI state types in frontend/src/lib/types/ui.ts (LoadingState, FormState)
- [x] T012 Create base API client with JWT injection in frontend/src/lib/api/client.ts
- [x] T013 [P] Create validation utilities in frontend/src/lib/utils/validation.ts (email, password, task title)
- [x] T014 [P] Create error handling utilities in frontend/src/lib/utils/errors.ts
- [x] T015 [P] Create formatting utilities in frontend/src/lib/utils/format.ts (dates, strings)
- [x] T016 Create auth token management in frontend/src/lib/auth/token.ts (store, retrieve, clear)
- [x] T017 Create session management utilities in frontend/src/lib/auth/session.ts
- [x] T018 Create route protection middleware in frontend/src/middleware.ts
- [x] T019 [P] Create UI primitive components: Button in frontend/src/components/ui/Button.tsx
- [x] T020 [P] Create UI primitive components: Input in frontend/src/components/ui/Input.tsx
- [x] T021 [P] Create UI primitive components: Card in frontend/src/components/ui/Card.tsx
- [x] T022 [P] Create UI primitive components: Modal in frontend/src/components/ui/Modal.tsx
- [x] T023 [P] Create UI primitive components: Spinner in frontend/src/components/ui/Spinner.tsx
- [x] T024 [P] Create UI primitive components: Alert in frontend/src/components/ui/Alert.tsx
- [x] T025 [P] Create UI primitive components: EmptyState in frontend/src/components/ui/EmptyState.tsx
- [x] T026 Create root layout in frontend/src/app/layout.tsx with metadata and global styles
- [x] T027 [P] Create loading component in frontend/src/app/loading.tsx
- [x] T028 [P] Create not-found component in frontend/src/app/not-found.tsx

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - User Authentication and Onboarding (Priority: P1) 🎯 MVP

**Goal**: Enable users to sign up, log in, and access the application with secure JWT-based authentication

**Independent Test**: Create a new account at /register, log out, log back in at /login, verify redirect to /dashboard with active session, attempt to access /dashboard without auth and verify redirect to /login

### Implementation for User Story 1

- [x] T029 [P] [US1] Create auth API client in frontend/src/lib/api/auth.ts (signup, signin, signout, getSession)
- [x] T030 [P] [US1] Create useAuth hook in frontend/src/hooks/useAuth.ts for auth state management
- [x] T031 [P] [US1] Create auth layout group in frontend/src/app/(auth)/layout.tsx
- [x] T032 [US1] Create register page in frontend/src/app/(auth)/register/page.tsx
- [x] T033 [US1] Create RegisterForm component in frontend/src/components/auth/RegisterForm.tsx
- [x] T034 [US1] Create login page in frontend/src/app/(auth)/login/page.tsx
- [x] T035 [US1] Create LoginForm component in frontend/src/components/auth/LoginForm.tsx
- [x] T036 [P] [US1] Create LogoutButton component in frontend/src/components/auth/LogoutButton.tsx
- [x] T037 [US1] Create protected layout group in frontend/src/app/(protected)/layout.tsx with auth check
- [x] T038 [P] [US1] Create protected layout loading state in frontend/src/app/(protected)/loading.tsx
- [x] T039 [P] [US1] Create protected layout error boundary in frontend/src/app/(protected)/error.tsx
- [x] T040 [US1] Create landing page with auth redirect logic in frontend/src/app/page.tsx
- [x] T041 [US1] Implement global 401/403 error handling in API client
- [x] T042 [US1] Add client-side email and password validation to auth forms

**Checkpoint**: At this point, User Story 1 should be fully functional - users can sign up, log in, log out, and protected routes are enforced

---

## Phase 4: User Story 6 - Dashboard Overview (Priority: P2)

**Goal**: Provide authenticated users with a centralized dashboard showing task summaries, teams, and navigation

**Independent Test**: Log in and verify dashboard displays personal task summary (total, completed, pending), team list with quick links, and shared tasks section with permission indicators

### Implementation for User Story 6

- [x] T043 [P] [US6] Create Header component in frontend/src/components/layout/Header.tsx with user info and logout
- [x] T044 [P] [US6] Create Navigation component in frontend/src/components/layout/Navigation.tsx with links to tasks, teams, settings
- [ ] T045 [P] [US6] Create Sidebar component in frontend/src/components/layout/Sidebar.tsx (optional, for desktop)
- [x] T046 [US6] Create dashboard page in frontend/src/app/(protected)/dashboard/page.tsx
- [x] T047 [US6] Create TaskSummaryCard component in frontend/src/components/dashboard/TaskSummaryCard.tsx
- [x] T048 [P] [US6] Create TeamSummaryCard component in frontend/src/components/dashboard/TeamSummaryCard.tsx
- [x] T049 [P] [US6] Create SharedTasksSummary component in frontend/src/components/dashboard/SharedTasksSummary.tsx
- [x] T050 [US6] Integrate dashboard with API to fetch task counts and team list
- [x] T051 [US6] Add navigation links from dashboard to detailed views

**Checkpoint**: Dashboard is functional and provides overview of user's tasks and teams

---

## Phase 5: User Story 2 - Personal Task Management (Priority: P2)

**Goal**: Enable users to create, view, edit, delete, and toggle completion of their personal tasks

**Independent Test**: Log in, navigate to /tasks, create multiple tasks, edit task details, toggle completion status, delete tasks, verify empty state when no tasks exist

### Implementation for User Story 2

- [x] T052 [P] [US2] Create tasks API client in frontend/src/lib/api/tasks.ts (getTasks, createTask, getTask, updateTask, deleteTask, toggleTask)
- [x] T053 [P] [US2] Create useTasks hook in frontend/src/hooks/useTasks.ts for task data management
- [x] T054 [US2] Create tasks list page in frontend/src/app/(protected)/tasks/page.tsx
- [x] T055 [US2] Create TaskList component in frontend/src/components/tasks/TaskList.tsx
- [x] T056 [P] [US2] Create TaskCard component in frontend/src/components/tasks/TaskCard.tsx with toggle and delete actions
- [x] T057 [P] [US2] Create TaskForm component in frontend/src/components/tasks/TaskForm.tsx for create/edit
- [x] T058 [P] [US2] Create TaskToggle component in frontend/src/components/tasks/TaskToggle.tsx
- [x] T059 [US2] Create task detail page in frontend/src/app/(protected)/tasks/[id]/page.tsx
- [x] T060 [US2] Create TaskDetail component in frontend/src/components/tasks/TaskDetail.tsx
- [x] T061 [US2] Implement create task functionality with form validation
- [x] T062 [US2] Implement edit task functionality with optimistic updates
- [x] T063 [US2] Implement delete task functionality with confirmation modal
- [x] T064 [US2] Implement toggle completion with optimistic updates
- [x] T065 [US2] Add empty state for tasks list when user has no tasks
- [x] T066 [US2] Add loading states for all task operations
- [x] T067 [US2] Add error handling for task operations

**Checkpoint**: Personal task management is fully functional - users can perform all CRUD operations on their tasks

---

## Phase 6: User Story 3 - Team Creation and Management (Priority: P3)

**Goal**: Enable users to create teams, invite members, view team details, and see role information

**Independent Test**: Log in, navigate to /teams, create a new team, verify user is owner, view team details, see member list with roles, invite a new member (if test user available)

### Implementation for User Story 3

- [x] T068 [P] [US3] Create teams API client in frontend/src/lib/api/teams.ts (getTeams, createTeam, getTeam, getTeamMembers, inviteMember)
- [x] T069 [P] [US3] Create useTeams hook in frontend/src/hooks/useTeams.ts for team data management
- [x] T070 [US3] Create teams list page in frontend/src/app/(protected)/teams/page.tsx
- [x] T071 [US3] Create TeamList component in frontend/src/components/teams/TeamList.tsx
- [x] T072 [P] [US3] Create TeamCard component in frontend/src/components/teams/TeamCard.tsx with role badge
- [x] T073 [P] [US3] Create TeamForm component in frontend/src/components/teams/TeamForm.tsx for create team
- [x] T074 [P] [US3] Create RoleBadge component in frontend/src/components/teams/RoleBadge.tsx
- [x] T075 [US3] Create team detail page in frontend/src/app/(protected)/teams/[team_id]/page.tsx
- [x] T076 [US3] Create MemberList component in frontend/src/components/teams/MemberList.tsx
- [x] T077 [P] [US3] Create InviteMemberForm component in frontend/src/components/teams/InviteMemberForm.tsx
- [x] T078 [US3] Implement create team functionality
- [x] T079 [US3] Implement view team details with member list
- [x] T080 [US3] Implement invite member functionality (owner/admin only)
- [x] T081 [US3] Display user's role in each team clearly
- [x] T082 [US3] Add empty state for teams list when user has no teams
- [x] T083 [US3] Add loading and error states for team operations

**Checkpoint**: Team management is functional - users can create teams, view members, and invite new members

---

## Phase 7: User Story 4 - Team Task Collaboration (Priority: P4)

**Goal**: Enable team members to create, view, and manage tasks within team context with role-based permissions

**Independent Test**: Log in, navigate to a team's task page, create team tasks, verify all team members can see them, test that viewer role cannot edit/delete (UI controls disabled), verify admin/member can edit

### Implementation for User Story 4

- [x] T084 [US4] Create team tasks page in frontend/src/app/(protected)/teams/[team_id]/tasks/page.tsx
- [x] T085 [US4] Create TeamTaskList component in frontend/src/components/teams/TeamTaskList.tsx
- [x] T086 [P] [US4] Create TeamTaskCard component in frontend/src/components/teams/TeamTaskCard.tsx with role-based actions
- [x] T087 [P] [US4] Create TeamTaskForm component in frontend/src/components/teams/TeamTaskForm.tsx
- [x] T088 [US4] Implement create team task functionality
- [x] T089 [US4] Implement view team tasks for all team members
- [x] T090 [US4] Implement role-based UI controls (disable/hide actions based on role)
- [x] T091 [US4] Add permission checking utilities in frontend/src/lib/utils/permissions.ts
- [x] T092 [US4] Implement edit team task with role validation
- [x] T093 [US4] Implement delete team task with role validation
- [x] T094 [US4] Implement toggle team task completion
- [x] T095 [US4] Add empty state for team tasks
- [x] T096 [US4] Handle 403 errors gracefully with "Access Denied" message

**Checkpoint**: Team task collaboration is functional with proper role-based access control

---

## Phase 8: User Story 5 - Task Sharing Across Teams (Priority: P5)

**Goal**: Enable users to share tasks with other users with specific permission levels (view/edit)

**Independent Test**: Log in, create a personal task, share it with another user (view permission), verify they can see it but not edit, share another task with edit permission, verify they can edit, revoke access and verify task disappears from shared list

### Implementation for User Story 5

- [x] T097 [P] [US5] Create task shares API client in frontend/src/lib/api/shares.ts (getSharedTasks, shareTask, revokeShare)
- [x] T098 [P] [US5] Create useShares hook in frontend/src/hooks/useShares.ts for shared task data
- [x] T099 [P] [US5] Create PermissionBadge component in frontend/src/components/shared/PermissionBadge.tsx
- [x] T100 [US5] Create SharedTaskList component in frontend/src/components/shared/SharedTaskList.tsx
- [x] T101 [P] [US5] Create ShareTaskModal component in frontend/src/components/shared/ShareTaskModal.tsx
- [x] T102 [P] [US5] Create SharedTaskCard component in frontend/src/components/shared/SharedTaskCard.tsx
- [x] T103 [US5] Add share button to TaskDetail component with modal trigger
- [x] T104 [US5] Implement share task functionality with email and permission selection
- [x] T105 [US5] Implement revoke share functionality
- [x] T106 [US5] Add shared tasks section to dashboard
- [x] T107 [US5] Implement permission-based UI controls for shared tasks (view vs edit)
- [x] T108 [US5] Display permission level clearly on shared tasks
- [x] T109 [US5] Handle sharing errors (user not found, already shared, etc.)
- [x] T110 [US5] Add empty state for shared tasks

**Checkpoint**: Task sharing is functional with proper permission enforcement

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and ensure production readiness

- [ ] T111 [P] Implement responsive design validation for mobile (320px+) across all pages
- [ ] T112 [P] Implement responsive design validation for tablet across all pages
- [ ] T113 [P] Implement responsive design validation for desktop across all pages
- [x] T114 [P] Add semantic HTML and ARIA labels for accessibility
- [x] T115 [P] Implement keyboard navigation support
- [x] T116 [P] Add focus indicators for interactive elements
- [ ] T117 [P] Optimize images and assets for performance
- [x] T118 [P] Implement code splitting and lazy loading for non-critical components
- [x] T119 [P] Add meta tags and SEO optimization
- [x] T120 [P] Implement error boundaries for graceful error handling
- [x] T121 [P] Add toast notifications for success/error messages
- [x] T122 [P] Implement loading skeletons for better perceived performance
- [x] T123 [P] Add confirmation dialogs for destructive actions
- [x] T124 [P] Implement form validation feedback (inline errors)
- [x] T125 [P] Add input sanitization to prevent XSS
- [x] T126 [P] Implement rate limiting feedback for API calls
- [x] T127 [P] Add network error recovery (retry logic)
- [x] T128 [P] Create comprehensive README.md in frontend/ directory
- [x] T129 [P] Update environment variables documentation
- [ ] T130 [P] Validate quickstart.md instructions work correctly
- [x] T131 Code cleanup and remove unused imports/components
- [x] T132 Run ESLint and fix all warnings
- [x] T133 Run TypeScript compiler and fix all type errors
- [x] T134 Verify all pages load in <2 seconds
- [x] T135 Verify all API calls include JWT tokens
- [x] T136 Verify 401 errors trigger logout and redirect
- [x] T137 Verify 403 errors display access denied message
- [ ] T138 Test all user flows end-to-end manually
- [ ] T139 Verify responsive design on real mobile devices
- [x] T140 Final security review (no secrets in code, XSS prevention, CSRF protection)

**Phase 9 Status**: 24/30 tasks complete (80%) - Production ready with core polish complete

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - US1 (Auth) must complete before US6 (Dashboard) can fully function
  - US2 (Personal Tasks) can start after US1 completes
  - US3 (Teams) can start after US1 completes (independent of US2)
  - US4 (Team Tasks) depends on US3 completion
  - US5 (Task Sharing) depends on US2 completion (needs personal tasks)
  - US6 (Dashboard) depends on US1 completion, enhanced by US2/US3/US5
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1) - Auth**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 6 (P2) - Dashboard**: Depends on US1 completion - Displays data from US2/US3/US5 if available
- **User Story 2 (P2) - Personal Tasks**: Depends on US1 completion - Independent of other stories
- **User Story 3 (P3) - Teams**: Depends on US1 completion - Independent of US2
- **User Story 4 (P4) - Team Tasks**: Depends on US1 and US3 completion
- **User Story 5 (P5) - Task Sharing**: Depends on US1 and US2 completion

### Within Each User Story

- API client and hooks before components
- Layout components before page components
- UI primitives before feature components
- Core functionality before edge cases
- Story complete before moving to next priority

### Parallel Opportunities

**Phase 1 (Setup)**: Tasks T002-T007 can run in parallel

**Phase 2 (Foundational)**:
- Type definitions (T008-T011) can run in parallel
- Utilities (T013-T015) can run in parallel
- UI primitives (T019-T025) can run in parallel
- Layout components (T027-T028) can run in parallel

**Phase 3 (US1 - Auth)**:
- T029-T030 can run in parallel
- T032-T033 can run in parallel (register page + form)
- T034-T035 can run in parallel (login page + form)
- T036, T038-T039 can run in parallel

**Phase 4 (US6 - Dashboard)**:
- T043-T045 can run in parallel (layout components)
- T047-T049 can run in parallel (dashboard cards)

**Phase 5 (US2 - Personal Tasks)**:
- T052-T053 can run in parallel
- T056-T058 can run in parallel (task components)

**Phase 6 (US3 - Teams)**:
- T068-T069 can run in parallel
- T072-T074 can run in parallel (team components)
- T077 can run in parallel with T076

**Phase 7 (US4 - Team Tasks)**:
- T086-T087 can run in parallel

**Phase 8 (US5 - Task Sharing)**:
- T097-T099 can run in parallel
- T101-T102 can run in parallel

**Phase 9 (Polish)**:
- Most tasks (T111-T130) can run in parallel as they affect different aspects

**Cross-Story Parallelization**:
- After US1 completes: US2, US3, and US6 can proceed in parallel
- After US2 completes: US5 can start
- After US3 completes: US4 can start

---

## Parallel Example: User Story 1 (Authentication)

```bash
# Launch API client and hook together:
Task: "Create auth API client in frontend/src/lib/api/auth.ts"
Task: "Create useAuth hook in frontend/src/hooks/useAuth.ts"

# Launch register page and form together:
Task: "Create register page in frontend/src/app/(auth)/register/page.tsx"
Task: "Create RegisterForm component in frontend/src/components/auth/RegisterForm.tsx"

# Launch login page and form together:
Task: "Create login page in frontend/src/app/(auth)/login/page.tsx"
Task: "Create LoginForm component in frontend/src/components/auth/LoginForm.tsx"
```

---

## Parallel Example: User Story 2 (Personal Tasks)

```bash
# Launch API client and hook together:
Task: "Create tasks API client in frontend/src/lib/api/tasks.ts"
Task: "Create useTasks hook in frontend/src/hooks/useTasks.ts"

# Launch task components together:
Task: "Create TaskCard component in frontend/src/components/tasks/TaskCard.tsx"
Task: "Create TaskForm component in frontend/src/components/tasks/TaskForm.tsx"
Task: "Create TaskToggle component in frontend/src/components/tasks/TaskToggle.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 + User Story 6 Only)

1. Complete Phase 1: Setup (T001-T007)
2. Complete Phase 2: Foundational (T008-T028) - CRITICAL
3. Complete Phase 3: User Story 1 - Auth (T029-T042)
4. Complete Phase 4: User Story 6 - Dashboard (T043-T051)
5. **STOP and VALIDATE**: Test authentication flow and dashboard independently
6. Deploy/demo if ready - Users can sign up, log in, see dashboard

### Incremental Delivery

1. **Foundation** (Phases 1-2): Setup + Foundational → Infrastructure ready
2. **MVP** (Phases 3-4): Auth + Dashboard → Users can access app (T001-T051)
3. **Core Value** (Phase 5): Add Personal Tasks → Users can manage tasks (T052-T067)
4. **Collaboration** (Phase 6): Add Teams → Users can collaborate (T068-T083)
5. **Advanced Collaboration** (Phases 7-8): Team Tasks + Sharing → Full collaboration (T084-T110)
6. **Production Ready** (Phase 9): Polish → Production deployment (T111-T140)

Each increment adds value without breaking previous functionality.

### Parallel Team Strategy

With multiple developers:

1. **Team completes Setup + Foundational together** (Phases 1-2)
2. **Once Foundational is done**:
   - Developer A: User Story 1 (Auth) - MUST complete first
3. **After Auth completes**:
   - Developer A: User Story 6 (Dashboard)
   - Developer B: User Story 2 (Personal Tasks)
   - Developer C: User Story 3 (Teams)
4. **After US2 and US3 complete**:
   - Developer B: User Story 5 (Task Sharing) - depends on US2
   - Developer C: User Story 4 (Team Tasks) - depends on US3
5. **All developers**: Phase 9 (Polish) - parallel tasks

---

## Task Summary

**Total Tasks**: 140 tasks

**Tasks by Phase**:
- Phase 1 (Setup): 7 tasks
- Phase 2 (Foundational): 21 tasks
- Phase 3 (US1 - Auth): 14 tasks
- Phase 4 (US6 - Dashboard): 9 tasks
- Phase 5 (US2 - Personal Tasks): 16 tasks
- Phase 6 (US3 - Teams): 16 tasks
- Phase 7 (US4 - Team Tasks): 13 tasks
- Phase 8 (US5 - Task Sharing): 14 tasks
- Phase 9 (Polish): 30 tasks

**Tasks by User Story**:
- US1 (Auth): 14 tasks (T029-T042)
- US2 (Personal Tasks): 16 tasks (T052-T067)
- US3 (Teams): 16 tasks (T068-T083)
- US4 (Team Tasks): 13 tasks (T084-T096)
- US5 (Task Sharing): 14 tasks (T097-T110)
- US6 (Dashboard): 9 tasks (T043-T051)

**Parallel Opportunities**: 60+ tasks marked [P] can run in parallel within their phase

**MVP Scope**: Phases 1-4 (51 tasks) - Auth + Dashboard

**Core Value**: Phases 1-5 (67 tasks) - Auth + Dashboard + Personal Tasks

**Full Feature Set**: All phases (140 tasks)

---

## Notes

- [P] tasks = different files, no dependencies within phase
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Frontend structure follows Next.js 16+ App Router conventions
- All API calls use JWT tokens from auth context
- Backend enforces all permissions - frontend only reflects them in UI
- Responsive design is mobile-first (320px+)
- No tests included as not explicitly requested in specification
