# Implementation Plan: Authentication & API Security

**Branch**: `002-auth-api-security` | **Date**: 2026-02-04 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-auth-api-security/spec.md`

## Summary

This plan implements JWT-based authentication and authorization to secure the existing Todo REST API. The implementation adds Better Auth on the Next.js frontend for user registration/login, JWT token verification middleware on the FastAPI backend, and per-user task ownership enforcement at the database query level. All changes are additive - Spec 1 functionality remains unchanged.

**Key Deliverables**:
1. Better Auth integration on Next.js frontend with JWT token issuance
2. JWT verification middleware on FastAPI backend using shared secret
3. User model and authentication endpoints (signup, signin)
4. Task model extension with user_id foreign key
5. Authorization enforcement on all task CRUD operations
6. Comprehensive error handling for authentication failures

## Technical Context

**Language/Version**:
- Backend: Python 3.10+ (FastAPI)
- Frontend: Next.js 16+ (App Router)

**Primary Dependencies**:
- Backend: FastAPI, SQLModel, PyJWT (or python-jose), python-dotenv, uvicorn
- Frontend: Next.js, Better Auth, React
- Database: Neon Serverless PostgreSQL

**Storage**: Neon Serverless PostgreSQL (already configured from Spec 1)

**Testing**:
- Backend: pytest with pytest-asyncio
- Frontend: Jest/React Testing Library (to be configured)

**Target Platform**:
- Backend: Linux server (containerized deployment)
- Frontend: Web browser (modern browsers with ES6+ support)

**Project Type**: Web application (frontend + backend with REST API)

**Performance Goals**:
- JWT token verification: <50ms per request
- Authentication endpoints: <500ms response time
- Support 100 concurrent authenticated requests without degradation

**Constraints**:
- Stateless authentication (no backend session storage)
- JWT verification on every protected request
- Shared secret (BETTER_AUTH_SECRET) between frontend and backend
- No modifications to Spec 1 code or database schema (only extensions)
- All changes must be additive

**Scale/Scope**:
- Multi-user application with per-user data isolation
- Expected: 100-1000 concurrent users
- Task ownership enforced at database query level

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Spec-Driven Development ✅
- **Status**: PASS
- **Verification**: All requirements are defined in spec.md with clear acceptance criteria
- **Notes**: 28 functional requirements (FR-001 through FR-028) are fully specified

### Principle II: Agentic Workflow Integrity ✅
- **Status**: PASS
- **Verification**: Implementation will use specialized agents:
  - `secure-auth-agent` for authentication implementation
  - `fastapi-backend` for backend API modifications
  - `neon-db-architect` for database schema extensions
  - `nextjs-ui-builder` for frontend auth UI
- **Notes**: No manual coding permitted; all changes via Claude Code agents

### Principle III: Correctness & Consistency ✅
- **Status**: PASS
- **Verification**:
  - User model will be consistent across frontend (Better Auth) and backend (SQLModel)
  - JWT token claims (user_id, email) will be standardized
  - API contracts will be explicitly defined in contracts/
- **Notes**: Data model consistency enforced through shared type definitions

### Principle IV: Security by Design ✅
- **Status**: PASS - Core focus of this specification
- **Verification**:
  - JWT verification on all task endpoints (FR-006 through FR-010)
  - User data isolation enforced at database query level (FR-016 through FR-021)
  - Secrets stored in .env files (FR-022 through FR-025)
  - Stateless authentication (no backend session storage)
- **Notes**: This spec implements the security layer required by the constitution

### Principle V: Separation of Concerns ✅
- **Status**: PASS
- **Verification**:
  - Frontend: Better Auth handles user authentication and token storage
  - Backend: JWT verification middleware separate from business logic (FR-015)
  - Database: User data isolation through query filters
  - Authentication logic centralized and reusable
- **Notes**: Clear boundaries between authentication and business logic

### Technology Stack Compliance ✅
- **Status**: PASS
- **Verification**:
  - Frontend: Next.js 16+ (App Router) ✓
  - Backend: Python FastAPI ✓
  - ORM: SQLModel ✓
  - Database: Neon Serverless PostgreSQL ✓
  - Authentication: Better Auth ✓
- **Notes**: All technologies align with constitutional requirements

### Process Constraints Compliance ✅
- **Status**: PASS
- **Verification**:
  - No manual coding (agentic workflow only) ✓
  - No deviation from spec ✓
  - No skipping workflow steps ✓
  - Spec 1 remains unchanged (additive changes only) ✓
- **Notes**: All process constraints will be enforced during implementation

### Security Constraints Compliance ✅
- **Status**: PASS
- **Verification**:
  - All task endpoints require JWT (except public auth endpoints) ✓
  - Unauthorized requests return 401 ✓
  - Task ownership enforced on every CRUD operation ✓
  - Secrets in .env files ✓
- **Notes**: Security constraints are the primary focus of this specification

**GATE RESULT**: ✅ PASS - All constitutional principles satisfied. Proceed to Phase 0.

## Project Structure

### Documentation (this feature)

```text
specs/002-auth-api-security/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (in progress)
├── research.md          # Phase 0 output (to be created)
├── data-model.md        # Phase 1 output (to be created)
├── quickstart.md        # Phase 1 output (to be created)
├── contracts/           # Phase 1 output (to be created)
│   ├── auth-api.yaml    # Authentication API contract (OpenAPI)
│   └── tasks-api.yaml   # Updated tasks API contract with auth
├── checklists/
│   └── requirements.md  # Spec quality checklist (completed)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── models/
│   │   ├── task.py           # [EXTEND] Add user_id foreign key relationship
│   │   └── user.py           # [NEW] User model for authentication
│   ├── schemas/
│   │   ├── task.py           # [EXISTING] Task request/response schemas
│   │   ├── user.py           # [NEW] User request/response schemas
│   │   └── auth.py           # [NEW] Auth request/response schemas (login, signup, token)
│   ├── services/
│   │   ├── task_service.py   # [MODIFY] Add user_id filtering to all queries
│   │   ├── auth_service.py   # [NEW] Authentication logic (password hashing, token generation)
│   │   └── user_service.py   # [NEW] User CRUD operations
│   ├── routes/
│   │   ├── tasks.py          # [MODIFY] Add JWT dependency to all endpoints
│   │   └── auth.py           # [NEW] Authentication endpoints (signup, signin)
│   ├── middleware/
│   │   └── auth.py           # [NEW] JWT verification middleware/dependency
│   ├── database/
│   │   └── connection.py     # [EXISTING] Database connection (no changes)
│   ├── config.py             # [MODIFY] Add BETTER_AUTH_SECRET configuration
│   └── main.py               # [MODIFY] Register auth routes
└── tests/
    ├── test_auth_endpoints.py    # [NEW] Test authentication endpoints
    ├── test_jwt_verification.py  # [NEW] Test JWT middleware
    ├── test_task_ownership.py    # [NEW] Test per-user task isolation
    └── [existing test files]     # [MODIFY] Update to include auth tokens

frontend/
├── app/
│   ├── (auth)/
│   │   ├── login/
│   │   │   └── page.tsx      # [NEW] Login page
│   │   └── signup/
│   │       └── page.tsx      # [NEW] Signup page
│   ├── (protected)/
│   │   └── tasks/
│   │       └── page.tsx      # [NEW] Protected tasks page
│   └── layout.tsx            # [NEW] Root layout with auth provider
├── lib/
│   ├── auth.ts               # [NEW] Better Auth configuration
│   └── api-client.ts         # [NEW] API client with JWT token injection
└── components/
    ├── auth/
    │   ├── LoginForm.tsx     # [NEW] Login form component
    │   └── SignupForm.tsx    # [NEW] Signup form component
    └── tasks/
        └── [task components] # [NEW] Task list, task item components

.env
├── BETTER_AUTH_SECRET        # [NEW] Shared secret for JWT signing/verification
├── DATABASE_URL              # [EXISTING] Neon PostgreSQL connection string
└── [other env vars]
```

**Structure Decision**: This is a web application with separate frontend and backend. The backend extends the existing FastAPI structure from Spec 1 by adding authentication models, services, routes, and middleware. The frontend is a new Next.js application using App Router with Better Auth integration. All changes to backend are additive - no Spec 1 code is modified, only extended.

## Complexity Tracking

> **No constitutional violations detected. This section is empty.**

All implementation follows constitutional principles:
- Single technology stack (no additional frameworks)
- Clear separation of concerns (auth middleware separate from business logic)
- Stateless architecture (no session storage)
- Standard patterns (JWT, REST API, ORM)

## Phase 0: Research & Technology Decisions

**Status**: ✅ Completed

**Research Tasks**:
1. ✅ Better Auth configuration for Next.js with JWT token issuance
2. ✅ PyJWT vs python-jose for JWT verification in FastAPI
3. ✅ FastAPI dependency injection pattern for JWT verification
4. ✅ Database migration strategy for adding user_id foreign key to existing tasks
5. ✅ Error handling patterns for authentication failures (401, 403)
6. ✅ Token expiration and refresh strategies

**Output**: `research.md` with decisions, rationale, and alternatives considered

**Key Decisions**:
- Frontend: Better Auth with JWT session strategy
- Backend: PyJWT 2.8+ for token verification
- Auth Pattern: FastAPI Depends() for dependency injection
- Migration: Nullable user_id column for backward compatibility
- Error Handling: Structured 401/403 responses with error codes
- Token Expiration: 24-hour access tokens with automatic refresh

## Phase 1: Design & Contracts

**Status**: ✅ Completed

**Deliverables**:
1. ✅ `data-model.md` - User and Task entity definitions with relationships
2. ✅ `contracts/auth-api.yaml` - OpenAPI spec for authentication endpoints
3. ✅ `contracts/tasks-api.yaml` - Updated OpenAPI spec for protected task endpoints
4. ✅ `quickstart.md` - Setup instructions for authentication configuration
5. ✅ Agent context updated with new technologies

**Output**: Complete design artifacts ready for task breakdown

**Artifacts Created**:
- User entity with bcrypt password hashing
- Task entity extended with user_id foreign key
- JWT token structure with userId and email claims
- 3 authentication endpoints (signup, signin, me)
- 5 protected task endpoints (list, create, get, update, delete, toggle)
- Comprehensive setup and testing guide

## Phase 2: Task Breakdown

**Status**: Not started (handled by `/sp.tasks` command)

This phase will be executed by the `/sp.tasks` command after Phase 1 is complete.

## Next Steps

1. Execute Phase 0: Research (resolve technology choices)
2. Execute Phase 1: Design (create data models and API contracts)
3. Update agent context with new technologies
4. Run `/sp.tasks` to generate task breakdown
5. Run `/sp.implement` to execute tasks via specialized agents
