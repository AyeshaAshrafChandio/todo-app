# Tasks: MCP Backend Data & Dashboard

**Input**: User requirements for MCP database tables and live dashboard
**Feature**: Database schema for AI chat + Live dashboard with task statistics
**Prerequisites**: Existing backend (FastAPI), frontend (Next.js), Neon Serverless PostgreSQL

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and database connection setup

- [X] T001 Verify Neon Serverless PostgreSQL connection in backend/.env
- [X] T002 [P] Install SQLModel and Alembic dependencies in backend/requirements.txt
- [X] T003 [P] Configure Alembic for database migrations in backend/alembic/
- [X] T004 Create database connection pool configuration in backend/app/database/connection.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core database infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Create base SQLModel models with common fields (id, created_at, updated_at) in backend/app/models/base.py
- [X] T006 [P] Setup database session management and dependency injection in backend/app/database/session.py
- [X] T007 [P] Create database initialization script in backend/app/database/init_db.py
- [X] T008 Configure database indexes strategy in backend/app/database/indexes.py
- [X] T009 Setup database migration workflow documentation in backend/migrations/README.md

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Database Schema for AI Chat (Priority: P1) 🎯 MVP

**Goal**: Create all required database tables (Tasks, Conversations, Messages) with proper relationships and constraints to support AI chat functionality

**Independent Test**: Can create tables via migration, insert test data, query data, and verify relationships work correctly. All tables support efficient querying for AI chat operations.

### Implementation for User Story 1

- [X] T010 [P] [US1] Create Task model in backend/app/models/task.py with fields (id, user_id, title, description, status, created_at, updated_at)
- [X] T011 [P] [US1] Create Conversation model in backend/app/models/conversation.py with fields (id, user_id, created_at, updated_at)
- [X] T012 [P] [US1] Create Message model in backend/app/models/message.py with fields (id, conversation_id, user_id, role, content, created_at)
- [X] T013 [US1] Create database migration for Task table in backend/alembic/versions/001_create_tasks_table.py
- [X] T014 [US1] Create database migration for Conversation table in backend/alembic/versions/002_create_conversations_table.py
- [X] T015 [US1] Create database migration for Message table in backend/alembic/versions/003_create_messages_table.py
- [X] T016 [US1] Add foreign key constraints and indexes for efficient querying in backend/alembic/versions/004_add_indexes.py
- [X] T017 [US1] Create database seed script with sample data in backend/app/database/seed.py
- [X] T018 [US1] Verify all tables created successfully and relationships work in backend/tests/test_database_schema.py

**Checkpoint**: At this point, all core database tables should be created and queryable. AI chat backend can store conversations and messages.

---

## Phase 4: User Story 2 - Team and Sharing Tables (Priority: P2)

**Goal**: Create TaskShares and Teams tables to support multi-user collaboration and task sharing

**Independent Test**: Can create teams, add members, share tasks between users, and query shared tasks efficiently. Data isolation by team is enforced.

### Implementation for User Story 2

- [X] T019 [P] [US2] Create Team model in backend/app/models/team.py with fields (id, name, owner_id, created_at, updated_at)
- [X] T020 [P] [US2] Create TeamMember model in backend/app/models/team_member.py with fields (id, team_id, user_id, role, created_at)
- [X] T021 [P] [US2] Create TaskShare model in backend/app/models/task_share.py with fields (id, task_id, shared_with_user_id, shared_by_user_id, permission, created_at)
- [X] T022 [US2] Create database migration for Team table in backend/alembic/versions/005_create_teams_table.py
- [X] T023 [US2] Create database migration for TeamMember table in backend/alembic/versions/006_create_team_members_table.py
- [X] T024 [US2] Create database migration for TaskShare table in backend/alembic/versions/007_create_task_shares_table.py
- [X] T025 [US2] Add indexes for team and sharing queries in backend/alembic/versions/008_add_team_indexes.py
- [X] T026 [US2] Implement data isolation logic for team-based queries in backend/app/services/team_service.py
- [X] T027 [US2] Verify team and sharing functionality with test data in backend/tests/test_team_schema.py

**Checkpoint**: At this point, teams and task sharing should work. Users can collaborate on tasks within teams.

---

## Phase 5: User Story 3 - Dashboard Statistics API (Priority: P1) 🎯 MVP

**Goal**: Implement backend API endpoints that return task statistics (total, pending, completed, shared) for dashboard display

**Independent Test**: Can call API endpoints and receive accurate task counts. Statistics reflect current database state. Data is filtered by user/team correctly.

### Implementation for User Story 3

- [X] T028 [P] [US3] Create TaskStatistics schema in backend/app/schemas/dashboard.py with fields (total_tasks, pending_tasks, completed_tasks, shared_tasks)
- [X] T029 [US3] Implement get_task_statistics service in backend/app/services/dashboard_service.py
- [X] T030 [US3] Create GET /api/dashboard/statistics endpoint in backend/app/routes/dashboard.py
- [X] T031 [US3] Add user authentication middleware to dashboard routes in backend/app/routes/dashboard.py
- [X] T032 [US3] Implement efficient SQL queries for task counts in backend/app/services/dashboard_service.py
- [X] T033 [US3] Add caching layer for dashboard statistics in backend/app/services/cache_service.py
- [X] T034 [US3] Test dashboard API with various user scenarios in backend/tests/test_dashboard_api.py

**Checkpoint**: At this point, dashboard API returns accurate statistics. Backend is ready for frontend integration.

---

## Phase 6: User Story 4 - Dashboard Frontend UI (Priority: P1) 🎯 MVP

**Goal**: Create live dashboard page showing task statistics with real-time updates via polling

**Independent Test**: Dashboard page loads, displays current statistics, updates automatically every 5 seconds, and shows accurate counts matching database state.

### Implementation for User Story 4

- [X] T035 [P] [US4] Create Dashboard page component in frontend/src/app/(protected)/dashboard/page.tsx
- [X] T036 [P] [US4] Create StatisticsCard component in frontend/src/components/dashboard/StatisticsCard.tsx
- [X] T037 [P] [US4] Create dashboard API client in frontend/src/lib/api/dashboard.ts
- [X] T038 [US4] Implement useDashboard hook with polling logic in frontend/src/hooks/useDashboard.ts
- [X] T039 [US4] Create dashboard layout with statistics cards in frontend/src/components/dashboard/DashboardLayout.tsx
- [X] T040 [US4] Add loading and error states to dashboard in frontend/src/components/dashboard/DashboardLayout.tsx
- [X] T041 [US4] Implement 5-second polling for real-time updates in frontend/src/hooks/useDashboard.ts
- [X] T042 [US4] Add responsive design for mobile/tablet/desktop in frontend/src/components/dashboard/StatisticsCard.tsx
- [X] T043 [US4] Test dashboard UI with mock data in frontend/tests/dashboard.spec.ts

**Checkpoint**: At this point, dashboard UI is complete and updates in real-time. Users can see their task statistics.

---

## Phase 7: User Story 5 - Real-Time Updates via WebSockets (Priority: P3)

**Goal**: Replace polling with WebSocket connections for instant dashboard updates when tasks change

**Independent Test**: Dashboard updates immediately when tasks are created/updated/deleted without manual refresh. WebSocket connection is stable and reconnects on disconnect.

### Implementation for User Story 5

- [X] T044 [P] [US5] Install WebSocket dependencies (websockets, socket.io) in backend/requirements.txt
- [X] T045 [US5] Create WebSocket manager in backend/app/services/websocket_manager.py
- [X] T046 [US5] Implement WebSocket endpoint in backend/app/routes/websocket.py
- [X] T047 [US5] Add WebSocket event emitters to task operations in backend/app/services/task_service.py
- [X] T048 [US5] Create WebSocket client in frontend/src/lib/websocket/client.ts
- [X] T049 [US5] Update useDashboard hook to use WebSocket instead of polling in frontend/src/hooks/useDashboard.ts
- [X] T050 [US5] Implement WebSocket reconnection logic in frontend/src/lib/websocket/client.ts
- [X] T051 [US5] Add WebSocket connection status indicator in frontend/src/components/dashboard/ConnectionStatus.tsx
- [X] T052 [US5] Test WebSocket real-time updates in frontend/tests/websocket.spec.ts

**Checkpoint**: At this point, dashboard updates instantly via WebSockets. Polling is replaced with push-based updates.

---

## Phase 8: User Story 6 - Data Isolation and Security (Priority: P2)

**Goal**: Enforce strict data isolation by user/team with comprehensive security checks

**Independent Test**: Users can only see their own tasks and tasks shared with them. Team members can only see team tasks. Unauthorized access attempts are blocked.

### Implementation for User Story 6

- [X] T053 [P] [US6] Create authorization middleware in backend/app/middleware/authorization.py
- [X] T054 [US6] Implement user-based data filtering in backend/app/services/task_service.py
- [X] T055 [US6] Implement team-based data filtering in backend/app/services/team_service.py
- [X] T056 [US6] Add permission checks to all dashboard endpoints in backend/app/routes/dashboard.py
- [X] T057 [US6] Create security audit logging in backend/app/services/audit_service.py
- [X] T058 [US6] Test data isolation with multiple users in backend/tests/test_data_isolation.py
- [X] T059 [US6] Test unauthorized access scenarios in backend/tests/test_security.py

**Checkpoint**: At this point, data isolation is enforced. Users can only access their own data or shared data.

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T060 [P] Add database query performance monitoring in backend/app/middleware/performance.py
- [X] T061 [P] Create database backup and restore scripts in backend/scripts/backup.sh
- [X] T062 [P] Add comprehensive API documentation in backend/docs/api.md
- [X] T063 [P] Optimize database indexes for common queries in backend/alembic/versions/009_optimize_indexes.py
- [X] T064 Add error handling for database connection failures in backend/app/database/connection.py
- [X] T065 Create dashboard user guide in frontend/docs/dashboard-guide.md
- [X] T066 Run end-to-end testing for complete workflow in tests/e2e/test_dashboard_flow.py
- [X] T067 Validate all functional requirements from specification

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - US1 (Database Schema) must complete before US3 (Dashboard API)
  - US3 (Dashboard API) must complete before US4 (Dashboard UI)
  - US2 (Teams/Sharing) can run in parallel with US1
  - US5 (WebSockets) depends on US4 completion
  - US6 (Security) can run in parallel with other stories
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Independent of US1
- **User Story 3 (P1)**: Depends on US1 (needs Task table) - BLOCKS US4
- **User Story 4 (P1)**: Depends on US3 (needs API endpoints) - BLOCKS US5
- **User Story 5 (P3)**: Depends on US4 (replaces polling with WebSockets)
- **User Story 6 (P2)**: Can start after US1 and US2 complete

### Within Each User Story

- Models before migrations
- Migrations before services
- Services before API endpoints
- API endpoints before frontend integration
- Core implementation before optimization

### Parallel Opportunities

- Phase 1: All setup tasks marked [P] can run in parallel
- Phase 2: All foundational tasks marked [P] can run in parallel
- US1: All model creation tasks (T010, T011, T012) can run in parallel
- US2: All model creation tasks (T019, T020, T021) can run in parallel
- US3: Schema and service tasks (T028, T029) can run in parallel initially
- US4: Frontend components (T035, T036, T037) can run in parallel
- US6: Authorization and filtering tasks (T053, T054, T055) can run in parallel
- Phase 9: All polish tasks marked [P] can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all model creation for User Story 1 together:
Task: "Create Task model in backend/app/models/task.py"
Task: "Create Conversation model in backend/app/models/conversation.py"
Task: "Create Message model in backend/app/models/message.py"
```

---

## Implementation Strategy

### MVP First (User Stories 1, 3, 4 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Database Schema)
4. Complete Phase 5: User Story 3 (Dashboard API)
5. Complete Phase 6: User Story 4 (Dashboard UI with polling)
6. **STOP and VALIDATE**: Test dashboard with real data
7. Deploy/demo if ready

**This gives you**: Working database + Dashboard with task statistics + Real-time updates via polling

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Database ready
3. Add User Story 3 → Test independently → API ready
4. Add User Story 4 → Test independently → Dashboard working (MVP!)
5. Add User Story 2 → Test independently → Teams/sharing enabled
6. Add User Story 6 → Test independently → Security hardened
7. Add User Story 5 → Test independently → WebSockets enabled
8. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Database Schema)
   - Developer B: User Story 2 (Teams/Sharing) - parallel with A
3. After US1 completes:
   - Developer A: User Story 3 (Dashboard API)
   - Developer B: Continues US2
4. After US3 completes:
   - Developer A: User Story 4 (Dashboard UI)
   - Developer B: User Story 6 (Security)
5. After US4 completes:
   - Developer A: User Story 5 (WebSockets)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Database migrations must be run in order (001, 002, 003...)
- Test data isolation thoroughly before production deployment
- Monitor database performance with real data volumes
- Consider connection pooling for Neon Serverless (already configured)

---

## Database Schema Summary

### Core Tables (US1)
- **tasks**: id, user_id, title, description, status, created_at, updated_at
- **conversations**: id, user_id, created_at, updated_at
- **messages**: id, conversation_id, user_id, role, content, created_at

### Collaboration Tables (US2)
- **teams**: id, name, owner_id, created_at, updated_at
- **team_members**: id, team_id, user_id, role, created_at
- **task_shares**: id, task_id, shared_with_user_id, shared_by_user_id, permission, created_at

### Indexes for Performance
- tasks: user_id, status, created_at
- conversations: user_id, created_at
- messages: conversation_id, created_at
- teams: owner_id
- team_members: team_id, user_id
- task_shares: task_id, shared_with_user_id

---

## Dashboard Features Summary

### Statistics Displayed (US3, US4)
- Total tasks count
- Pending tasks count
- Completed tasks count
- Tasks shared in teams count

### Real-Time Updates (US4, US5)
- Polling: Every 5 seconds (US4 - MVP)
- WebSockets: Instant push updates (US5 - Enhancement)

### Security (US6)
- User-based data isolation
- Team-based data isolation
- Permission checks on all endpoints
- Audit logging for security events

---

**Total Tasks**: 67 tasks across 9 phases
**MVP Scope**: Phases 1-2-3-5-6 (Tasks T001-T043) = 43 tasks
**Estimated MVP Time**: 2-3 days for experienced developer
**Full Implementation**: 3-5 days including all enhancements
