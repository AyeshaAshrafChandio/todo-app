# Tasks: Authentication & API Security

**Feature**: 002-auth-api-security
**Branch**: `002-auth-api-security`
**Spec**: [spec.md](./spec.md)
**Plan**: [plan.md](./plan.md)

## Overview

This document breaks down the Authentication & API Security feature into actionable tasks organized by user story. Each user story represents an independently testable increment that delivers value.

**Total Tasks**: 45
**Estimated Phases**: 8
**MVP Scope**: Phase 3 (User Story 1 - User Registration & Login)

## Task Organization

Tasks are organized by user story priority (P1, P2, P3, P4) to enable incremental delivery. Each phase builds on previous phases and can be independently tested.

**Parallelization**: Tasks marked with `[P]` can be executed in parallel with other `[P]` tasks in the same phase.

---

## Phase 1: Setup & Environment Configuration

**Goal**: Prepare the development environment and install required dependencies.

**Duration**: ~30 minutes

### Tasks

- [x] T001 Generate BETTER_AUTH_SECRET using Python secrets module and document in .env.example
- [x] T002 [P] Add PyJWT==2.8.0 to backend/requirements.txt
- [x] T003 [P] Add bcrypt==4.1.2 to backend/requirements.txt
- [x] T004 [P] Update backend/app/config.py to include BETTER_AUTH_SECRET, JWT_ALGORITHM, JWT_EXPIRATION_SECONDS settings
- [x] T005 Install backend dependencies: cd backend && pip install -r requirements.txt
- [x] T006 Verify backend starts successfully with new configuration (Note: Database connection from Spec 1 needs configuration)

**Acceptance Criteria**:
- ✅ BETTER_AUTH_SECRET is generated and documented
- ✅ All authentication dependencies installed
- ✅ Backend configuration includes JWT settings
- ✅ Backend starts without errors

---

## Phase 2: Foundational - Database & Core Auth Infrastructure

**Goal**: Create foundational authentication infrastructure that all user stories depend on.

**Duration**: ~2 hours

**Dependencies**: Phase 1 must be complete

### Tasks

- [x] T007 [P] Create backend/app/models/user.py with User SQLModel (id, email, password_hash, created_at, updated_at)
- [x] T008 [P] Create backend/app/schemas/user.py with UserResponse schema (id, email, created_at)
- [x] T009 [P] Create backend/app/schemas/auth.py with SignupRequest, SigninRequest, AuthResponse schemas
- [x] T010 Extend backend/app/models/task.py to add user_id field (Optional[str], foreign_key="users.id", nullable=True)
- [x] T011 Create backend/app/middleware/auth.py with get_current_user dependency function using HTTPBearer and PyJWT
- [x] T012 [P] Create backend/app/services/auth_service.py with hash_password, verify_password, create_jwt_token functions
- [x] T013 [P] Create backend/app/services/user_service.py with create_user, get_user_by_email, get_user_by_id functions
- [x] T014 Run database migration to create users table and add user_id column to tasks table
- [x] T015 Verify database schema changes: users table exists, tasks.user_id column exists with foreign key

**Acceptance Criteria**:
- ✅ User model created with bcrypt password hashing
- ✅ Task model extended with user_id foreign key
- ✅ JWT verification dependency function implemented
- ✅ Auth service functions (hash, verify, create token) working
- ✅ Database schema updated successfully
- ✅ No breaking changes to existing Spec 1 functionality

**Independent Test**:
Can create a User in database, hash a password, verify password, and generate a JWT token.

---

## Phase 3: User Story 1 (P1) - User Registration & Login

**Goal**: Enable users to register accounts and log in to receive JWT tokens.

**Duration**: ~2 hours

**Dependencies**: Phase 2 must be complete

**User Story**: As a new user, I need to create an account and log in so that I can access the todo application with my own secure workspace.

### Tasks

- [ ] T016 [US1] Create POST /api/auth/signup endpoint in backend/app/routes/auth.py that accepts email and password
- [ ] T017 [US1] Implement signup logic: validate email format, check for duplicate email, hash password, create user, return JWT token
- [ ] T018 [US1] Create POST /api/auth/signin endpoint in backend/app/routes/auth.py that accepts email and password
- [ ] T019 [US1] Implement signin logic: find user by email, verify password, generate JWT token, return token with user info
- [ ] T020 [US1] Create GET /api/auth/me endpoint in backend/app/routes/auth.py with get_current_user dependency
- [ ] T021 [US1] Register auth router in backend/app/main.py with app.include_router(auth.router)
- [ ] T022 [US1] Add error handling for duplicate email (422), invalid credentials (401), missing fields (422)

**Acceptance Criteria**:
- ✅ Users can register with valid email and password
- ✅ Duplicate email returns 422 error
- ✅ Users can login with correct credentials
- ✅ Invalid credentials return 401 error
- ✅ JWT token is returned on successful signup/signin
- ✅ Token contains userId and email claims
- ✅ /api/auth/me returns current user info when authenticated

**Independent Test** (from spec):
1. Register new account with valid email/password → receives JWT token
2. Login with correct credentials → receives JWT token with user_id and email
3. Login with incorrect credentials → receives 401 error
4. Register with existing email → receives error message

**Parallel Execution**:
- T016, T018, T020 can be implemented in parallel (different endpoints)

---

## Phase 4: User Story 2 (P2) - Protected Task Access

**Goal**: Require JWT authentication on all task endpoints to prevent unauthorized access.

**Duration**: ~1.5 hours

**Dependencies**: Phase 3 must be complete

**User Story**: As an authenticated user, I need all task operations to require my valid JWT token so that unauthorized users cannot access the task API.

### Tasks

- [ ] T023 [P] [US2] Add get_current_user dependency to GET /api/{user_id}/tasks endpoint in backend/app/routes/tasks.py
- [ ] T024 [P] [US2] Add get_current_user dependency to POST /api/{user_id}/tasks endpoint in backend/app/routes/tasks.py
- [ ] T025 [P] [US2] Add get_current_user dependency to GET /api/{user_id}/tasks/{id} endpoint in backend/app/routes/tasks.py
- [ ] T026 [P] [US2] Add get_current_user dependency to PUT /api/{user_id}/tasks/{id} endpoint in backend/app/routes/tasks.py
- [ ] T027 [P] [US2] Add get_current_user dependency to DELETE /api/{user_id}/tasks/{id} endpoint in backend/app/routes/tasks.py
- [ ] T028 [P] [US2] Add get_current_user dependency to PATCH /api/{user_id}/tasks/{id}/complete endpoint in backend/app/routes/tasks.py
- [ ] T029 [US2] Add user_id validation in each endpoint: verify path user_id matches authenticated user's ID, return 403 if mismatch
- [ ] T030 [US2] Update API documentation to indicate authentication requirement on all task endpoints

**Acceptance Criteria**:
- ✅ All task endpoints require valid JWT token
- ✅ Requests without token return 401 Unauthorized
- ✅ Requests with invalid token return 401 Unauthorized
- ✅ Requests with expired token return 401 Unauthorized
- ✅ Requests with valid token are processed successfully
- ✅ API documentation shows authentication requirement

**Independent Test** (from spec):
1. Request with valid JWT token → processed successfully
2. Request without JWT token → 401 Unauthorized
3. Request with expired JWT token → 401 Unauthorized with error message
4. Request with malformed JWT token → 401 Unauthorized

**Parallel Execution**:
- T023-T028 can be implemented in parallel (different endpoints)

---

## Phase 5: User Story 3 (P3) - Task Ownership Enforcement

**Goal**: Ensure users can only access and modify their own tasks through database-level filtering.

**Duration**: ~2 hours

**Dependencies**: Phase 4 must be complete

**User Story**: As an authenticated user, I need to only see and modify my own tasks so that my todo list remains private and isolated from other users.

### Tasks

- [ ] T031 [P] [US3] Update create_task function in backend/app/services/task_service.py to automatically set user_id from authenticated user
- [ ] T032 [P] [US3] Update get_tasks_by_user function in backend/app/services/task_service.py to filter by user_id
- [ ] T033 [P] [US3] Update get_task_by_id function in backend/app/services/task_service.py to filter by user_id and task_id
- [ ] T034 [P] [US3] Update update_task function in backend/app/services/task_service.py to verify task belongs to user before updating
- [ ] T035 [P] [US3] Update delete_task function in backend/app/services/task_service.py to verify task belongs to user before deleting
- [ ] T036 [P] [US3] Update toggle_task_completion function in backend/app/services/task_service.py to verify task belongs to user
- [ ] T037 [US3] Ensure all task operations return 404 (not 403) when task doesn't exist or doesn't belong to user
- [ ] T038 [US3] Add database indexes on tasks(user_id) and tasks(user_id, created_at) for query performance

**Acceptance Criteria**:
- ✅ Task creation automatically assigns user_id
- ✅ Users only see their own tasks in list
- ✅ Users cannot access other users' tasks (404 response)
- ✅ Users cannot update other users' tasks (404 response)
- ✅ Users cannot delete other users' tasks (404 response)
- ✅ Cross-user access returns 404 (not 403) to avoid information disclosure
- ✅ Database queries are optimized with proper indexes

**Independent Test** (from spec):
1. User A requests task list → only sees tasks they created
2. User A attempts to update User B's task → receives 404 Not Found
3. User A attempts to delete User B's task → receives 404 Not Found
4. User A creates task → task automatically associated with their user_id

**Parallel Execution**:
- T031-T036 can be implemented in parallel (different service functions)

---

## Phase 6: User Story 4 (P4) - Token Validation & Error Handling

**Goal**: Provide clear error messages and comprehensive token validation for better debugging and user experience.

**Duration**: ~1.5 hours

**Dependencies**: Phase 5 must be complete

**User Story**: As a system administrator, I need clear error messages and proper token validation so that security issues can be diagnosed and users understand authentication failures.

### Tasks

- [ ] T039 [P] [US4] Enhance JWT verification in backend/app/middleware/auth.py to catch ExpiredSignatureError and return "Token expired" message
- [ ] T040 [P] [US4] Enhance JWT verification to catch InvalidTokenError and return "Invalid token signature" message
- [ ] T041 [P] [US4] Add validation for required JWT claims (userId, email) and return "Invalid token claims" if missing
- [ ] T042 [US4] Add security logging for all authentication failures in backend/app/middleware/auth.py
- [ ] T043 [US4] Standardize error response format with detail, error_code, and timestamp fields
- [ ] T044 [US4] Update all authentication error responses to use structured format with appropriate error codes

**Acceptance Criteria**:
- ✅ Invalid signature returns 401 with "Invalid token signature" message
- ✅ Expired token returns 401 with "Token expired" message
- ✅ Missing claims return 401 with "Invalid token claims" message
- ✅ All authentication failures are logged for security auditing
- ✅ Error responses follow consistent structure
- ✅ Error codes are machine-readable (TOKEN_EXPIRED, TOKEN_INVALID, etc.)

**Independent Test** (from spec):
1. Token with invalid signature → 401 with "Invalid token signature"
2. Expired token → 401 with "Token expired"
3. Token with missing claims → 401 with "Invalid token claims"
4. Authentication failure → security event logged

**Parallel Execution**:
- T039-T041 can be implemented in parallel (different error types)

---

## Phase 7: Frontend - Better Auth Integration

**Goal**: Implement frontend authentication UI and Better Auth integration.

**Duration**: ~3 hours

**Dependencies**: Phase 3 must be complete (backend auth endpoints available)

**Note**: This phase spans multiple user stories (US1, US2, US3) from the frontend perspective.

### Tasks

- [ ] T045 [P] Initialize Next.js frontend project with App Router in frontend/ directory
- [ ] T046 [P] Install Better Auth: npm install better-auth
- [ ] T047 [P] Install React Query: npm install @tanstack/react-query
- [ ] T048 Create frontend/lib/auth.ts with Better Auth configuration (JWT strategy, 24-hour expiration)
- [ ] T049 [P] Create frontend/lib/api-client.ts with axios/fetch wrapper that includes JWT token in Authorization header
- [ ] T050 [P] Create frontend/app/layout.tsx with Better Auth provider and React Query provider
- [ ] T051 [P] Create frontend/components/auth/SignupForm.tsx with email and password fields
- [ ] T052 [P] Create frontend/components/auth/LoginForm.tsx with email and password fields
- [ ] T053 Create frontend/app/(auth)/signup/page.tsx using SignupForm component
- [ ] T054 Create frontend/app/(auth)/login/page.tsx using LoginForm component
- [ ] T055 [P] Create frontend/app/(protected)/tasks/page.tsx with authentication check and redirect
- [ ] T056 [P] Create frontend/components/tasks/TaskList.tsx to display user's tasks
- [ ] T057 [P] Create frontend/components/tasks/TaskItem.tsx for individual task display
- [ ] T058 [P] Create frontend/components/tasks/CreateTaskForm.tsx for task creation
- [ ] T059 Implement token storage in Better Auth (httpOnly cookies or secure localStorage)
- [ ] T060 Add automatic token refresh logic in Better Auth configuration
- [ ] T061 Add authentication state management and protected route middleware
- [ ] T062 Configure CORS in backend/app/main.py to allow frontend origin (http://localhost:3000)

**Acceptance Criteria**:
- ✅ Users can register via frontend signup form
- ✅ Users can login via frontend login form
- ✅ JWT token is stored securely
- ✅ Protected routes redirect unauthenticated users to login
- ✅ API requests include JWT token in Authorization header
- ✅ Token automatically refreshes before expiration
- ✅ Users can view and manage their tasks
- ✅ CORS configured correctly for frontend-backend communication

**Independent Test**:
1. Register new user via frontend → redirected to tasks page with token
2. Login existing user → redirected to tasks page with token
3. Access protected route without auth → redirected to login
4. Create task via frontend → task appears in list with user_id

**Parallel Execution**:
- T045-T047 (setup tasks)
- T051-T052 (form components)
- T056-T058 (task components)

---

## Phase 8: Polish & Cross-Cutting Concerns

**Goal**: Finalize documentation, API specs, and ensure production readiness.

**Duration**: ~1 hour

**Dependencies**: All previous phases complete

### Tasks

- [ ] T063 [P] Update backend API documentation (Swagger/OpenAPI) to show authentication requirements
- [ ] T064 [P] Add authentication examples to API documentation with sample JWT tokens
- [ ] T065 [P] Update .env.example with all required environment variables and descriptions
- [ ] T066 [P] Create or update README.md with setup instructions for authentication
- [ ] T067 Verify all Spec 1 functionality still works (backward compatibility check)
- [ ] T068 Run manual end-to-end test: signup → login → create task → list tasks → logout
- [ ] T069 Verify JWT token expiration and refresh flow works correctly
- [ ] T070 Check that secrets are not hardcoded anywhere in codebase

**Acceptance Criteria**:
- ✅ API documentation clearly shows authentication requirements
- ✅ Environment variables documented in .env.example
- ✅ README includes authentication setup instructions
- ✅ All Spec 1 functionality works without regressions
- ✅ End-to-end authentication flow works
- ✅ No hardcoded secrets in codebase
- ✅ Token expiration and refresh working

**Independent Test**:
Complete end-to-end flow from registration to task management works seamlessly.

---

## Dependencies & Execution Order

### User Story Completion Order

```
Phase 1 (Setup)
    ↓
Phase 2 (Foundational)
    ↓
Phase 3 (US1: Registration & Login) ← MVP Scope
    ↓
Phase 4 (US2: Protected Access)
    ↓
Phase 5 (US3: Task Ownership)
    ↓
Phase 6 (US4: Error Handling)
    ↓
Phase 7 (Frontend)
    ↓
Phase 8 (Polish)
```

### Critical Path

1. **Setup** (Phase 1) → **Foundational** (Phase 2) → **US1** (Phase 3)
   - This is the MVP: Users can register and login
   - Delivers: User authentication with JWT tokens

2. **US1** → **US2** (Phase 4)
   - Adds: Protected task endpoints
   - Delivers: API security perimeter

3. **US2** → **US3** (Phase 5)
   - Adds: Per-user data isolation
   - Delivers: Multi-user capability

4. **US3** → **US4** (Phase 6)
   - Adds: Enhanced error handling
   - Delivers: Production-ready error handling

5. **US1-US4** → **Frontend** (Phase 7)
   - Adds: User interface
   - Delivers: Complete user experience

6. **All** → **Polish** (Phase 8)
   - Adds: Documentation and final checks
   - Delivers: Production-ready system

### Parallel Execution Opportunities

**Phase 2 (Foundational)**:
- T007, T008, T009 (models and schemas)
- T012, T013 (service functions)

**Phase 3 (US1)**:
- T016, T018, T020 (different auth endpoints)

**Phase 4 (US2)**:
- T023-T028 (all task endpoint modifications)

**Phase 5 (US3)**:
- T031-T036 (all service function updates)

**Phase 6 (US4)**:
- T039-T041 (different error types)

**Phase 7 (Frontend)**:
- T045-T047 (setup)
- T051-T052 (auth forms)
- T056-T058 (task components)

**Phase 8 (Polish)**:
- T063-T066 (documentation tasks)

---

## Implementation Strategy

### MVP First Approach

**Minimum Viable Product**: Phase 1 + Phase 2 + Phase 3 (User Story 1)

This delivers:
- User registration and login
- JWT token generation
- Basic authentication infrastructure

**Value**: Users can create accounts and authenticate, establishing the foundation for all security features.

### Incremental Delivery

1. **Sprint 1**: Phases 1-3 (MVP)
   - Deliverable: Working authentication system
   - Test: Users can register and login

2. **Sprint 2**: Phases 4-5 (US2 + US3)
   - Deliverable: Protected API with per-user isolation
   - Test: Users can only access their own tasks

3. **Sprint 3**: Phases 6-7 (US4 + Frontend)
   - Deliverable: Complete user experience with error handling
   - Test: End-to-end authentication flow

4. **Sprint 4**: Phase 8 (Polish)
   - Deliverable: Production-ready system
   - Test: All acceptance criteria met

### Testing Strategy

**Per User Story**:
- Each phase includes independent test criteria
- Tests verify the specific user story acceptance scenarios
- No cross-story dependencies in testing

**Integration Testing**:
- Phase 8 includes end-to-end testing
- Verifies all user stories work together
- Confirms backward compatibility with Spec 1

---

## Task Summary

| Phase | User Story | Task Count | Parallel Tasks | Duration |
|-------|-----------|------------|----------------|----------|
| 1 | Setup | 6 | 3 | ~30 min |
| 2 | Foundational | 9 | 4 | ~2 hours |
| 3 | US1 (P1) | 7 | 3 | ~2 hours |
| 4 | US2 (P2) | 8 | 6 | ~1.5 hours |
| 5 | US3 (P3) | 8 | 6 | ~2 hours |
| 6 | US4 (P4) | 6 | 3 | ~1.5 hours |
| 7 | Frontend | 18 | 9 | ~3 hours |
| 8 | Polish | 8 | 4 | ~1 hour |
| **Total** | **4 Stories** | **70** | **38** | **~13.5 hours** |

---

## Validation Checklist

### Format Validation

- ✅ All tasks follow checklist format: `- [ ] [TaskID] [P?] [Story?] Description with file path`
- ✅ Task IDs are sequential (T001-T070)
- ✅ [P] marker present for parallelizable tasks
- ✅ [US#] marker present for user story tasks
- ✅ File paths included in task descriptions
- ✅ No tasks missing checkboxes or IDs

### Content Validation

- ✅ Each user story has dedicated phase
- ✅ Each phase has clear goal and acceptance criteria
- ✅ Independent test criteria defined per story
- ✅ Dependencies clearly documented
- ✅ Parallel execution opportunities identified
- ✅ MVP scope clearly defined (Phase 3)
- ✅ All 28 functional requirements from spec covered
- ✅ Backward compatibility with Spec 1 maintained

### Completeness Validation

- ✅ All entities from data-model.md covered (User, Task extension)
- ✅ All endpoints from contracts/ covered (3 auth + 5 task endpoints)
- ✅ All research decisions from research.md implemented
- ✅ Setup instructions from quickstart.md reflected in tasks
- ✅ All 4 user stories from spec.md have dedicated phases
- ✅ Frontend and backend both covered
- ✅ Database migration included
- ✅ Error handling comprehensive

---

## Next Steps

1. **Review Tasks**: Verify all tasks are clear and actionable
2. **Confirm MVP Scope**: Agree on Phases 1-3 as MVP
3. **Execute Implementation**: Run `/sp.implement` to begin task execution
4. **Track Progress**: Use task checkboxes to track completion
5. **Test Incrementally**: Test each phase independently before proceeding

**Ready for**: Implementation via `/sp.implement` command with specialized agents.
