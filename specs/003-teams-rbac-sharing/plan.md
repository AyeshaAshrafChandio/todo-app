# Implementation Plan: Teams, RBAC, and Task Sharing

**Branch**: `003-teams-rbac-sharing` | **Date**: 2026-02-04 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-teams-rbac-sharing/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Enable multi-user collaboration through team-based task management with role-based access control (Owner/Admin/Member/Viewer) and direct task sharing. This feature extends the existing todo application with three new database tables (teams, team_members, task_shares) and 18 new API endpoints while maintaining 100% backward compatibility with personal tasks. All permissions are enforced at the API layer using JWT authentication, with database transactions ensuring data consistency across multi-record operations.

## Technical Context

**Language/Version**: Python 3.11+ (Backend), TypeScript/JavaScript (Frontend with Next.js 16+)
**Primary Dependencies**:
- Backend: FastAPI, SQLModel, psycopg[binary], PyJWT, bcrypt, pydantic, python-dotenv
- Frontend: Next.js 16+ (App Router), React, Better Auth
- Database: Neon Serverless PostgreSQL

**Storage**: Neon Serverless PostgreSQL with connection pooling
**Testing**: pytest (backend), pytest-asyncio, httpx (API testing), Next.js testing utilities (frontend)
**Target Platform**: Web server (Linux/cloud for backend), Browser (modern browsers for frontend)
**Project Type**: Web application (FastAPI backend + Next.js frontend)
**Performance Goals**:
- API response time: <500ms at p95 latency
- Concurrent operations: Handle 10+ simultaneous team operations without data corruption
- Database queries: Optimized with proper indexes for team membership and task sharing lookups

**Constraints**:
- 100% backward compatibility with existing personal tasks (team_id nullable)
- All permissions enforced at API layer (never trust client)
- Database transactions required for multi-record operations
- Stateless authentication (JWT-based, no session storage)
- Security-first: All endpoints except auth require valid JWT

**Scale/Scope**:
- Multi-user collaboration system
- Teams with 100+ members (performance testing requirement)
- 1000+ task shares (performance testing requirement)
- 4 distinct roles with granular permissions
- 18 new API endpoints
- 3 new database tables + 1 extended table

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Spec-Driven Development ✓
- **Status**: PASS
- **Evidence**: Complete specification exists at `specs/003-teams-rbac-sharing/spec.md` with 29 functional requirements, 5 prioritized user stories, complete data model, and 18 API endpoints fully specified
- **Compliance**: All implementation will follow approved specification

### Principle II: Agentic Workflow Integrity ✓
- **Status**: PASS
- **Evidence**: Plan follows workflow sequence (spec → plan → tasks → implement)
- **Agent Strategy**:
  - `neon-db-architect`: Database schema design (teams, team_members, task_shares tables)
  - `secure-auth-agent`: Permission enforcement and JWT validation middleware
  - `fastapi-backend`: API endpoint implementation with role-based access control
  - `nextjs-ui-builder`: Frontend components for team management and task sharing UI
- **Compliance**: No manual coding; all implementation through specialized agents

### Principle III: Correctness & Consistency ✓
- **Status**: PASS
- **Evidence**:
  - Data models will be consistent across frontend (TypeScript interfaces) and backend (SQLModel/Pydantic)
  - API contracts fully specified in spec with request/response formats
  - Shared type definitions for roles, permissions, and entities
- **Compliance**: OpenAPI schema will be generated to ensure contract alignment

### Principle IV: Security by Design ✓
- **Status**: PASS
- **Evidence**:
  - All 18 new endpoints require JWT authentication (FR-024)
  - Permission validation before all privileged operations (FR-025)
  - Prevention of privilege escalation (FR-026)
  - User data filtered by authenticated user ID
  - Database transactions for multi-record operations (FR-029)
- **Compliance**: Security requirements are first-class in specification

### Principle V: Separation of Concerns ✓
- **Status**: PASS
- **Evidence**:
  - Backend API layer separate from business logic (services)
  - Database access through SQLModel ORM
  - Authentication middleware centralized
  - Frontend communicates only through REST APIs
  - Stateless JWT-based authentication
- **Compliance**: Clear layer boundaries maintained

### Technology Stack Compliance ✓
- **Status**: PASS
- **Evidence**: Uses approved stack (FastAPI, SQLModel, Neon PostgreSQL, Next.js 16+, Better Auth)
- **Compliance**: No deviations from constitutional technology requirements

### Security Constraints Compliance ✓
- **Status**: PASS
- **Evidence**:
  - JWT required on all endpoints except public auth endpoints
  - User data isolation enforced at database query level
  - Secrets managed through `.env` files
- **Compliance**: All security constraints satisfied

### Backward Compatibility ✓
- **Status**: PASS
- **Evidence**:
  - Additive-only architecture (team_id nullable on tasks table)
  - Existing personal tasks continue to work (FR-017)
  - No breaking changes to existing API contracts
- **Compliance**: 100% backward compatibility guaranteed

**GATE RESULT**: ✅ PASS - No constitutional violations. All principles satisfied. Proceed to Phase 0.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py (existing - Spec 002)
│   │   ├── task.py (existing - Spec 001, extended in Spec 002)
│   │   ├── team.py (NEW - this feature)
│   │   ├── team_member.py (NEW - this feature)
│   │   └── task_share.py (NEW - this feature)
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py (existing - Spec 002)
│   │   ├── user.py (existing - Spec 002)
│   │   ├── task.py (existing - Spec 001)
│   │   ├── team.py (NEW - this feature)
│   │   ├── team_member.py (NEW - this feature)
│   │   └── task_share.py (NEW - this feature)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py (existing - Spec 002)
│   │   ├── user_service.py (existing - Spec 002)
│   │   ├── task_service.py (existing - Spec 001)
│   │   ├── team_service.py (NEW - this feature)
│   │   ├── team_member_service.py (NEW - this feature)
│   │   └── task_share_service.py (NEW - this feature)
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py (existing - Spec 002)
│   │   ├── tasks.py (existing - Spec 001, EXTEND - this feature)
│   │   ├── teams.py (NEW - this feature)
│   │   ├── team_members.py (NEW - this feature)
│   │   └── task_shares.py (NEW - this feature)
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── auth.py (existing - Spec 002, EXTEND - this feature)
│   │   └── permissions.py (NEW - this feature)
│   ├── database/
│   │   ├── __init__.py
│   │   └── connection.py (existing - Spec 001)
│   ├── config.py (existing - Spec 001, 002)
│   └── main.py (existing - Spec 001, 002, EXTEND - this feature)
└── tests/
    ├── test_user_model.py (existing - Spec 002)
    ├── test_task_user_relationship.py (existing - Spec 002)
    ├── test_team_model.py (NEW - this feature)
    ├── test_team_member_model.py (NEW - this feature)
    ├── test_task_share_model.py (NEW - this feature)
    ├── test_team_api.py (NEW - this feature)
    ├── test_team_member_api.py (NEW - this feature)
    ├── test_task_share_api.py (NEW - this feature)
    ├── test_permissions.py (NEW - this feature)
    └── test_backward_compatibility.py (NEW - this feature)

frontend/
├── src/
│   ├── app/
│   │   ├── (auth)/
│   │   │   ├── login/
│   │   │   └── signup/
│   │   ├── (protected)/
│   │   │   ├── dashboard/
│   │   │   ├── tasks/
│   │   │   ├── teams/ (NEW - this feature)
│   │   │   │   ├── page.tsx
│   │   │   │   ├── [teamId]/
│   │   │   │   │   ├── page.tsx
│   │   │   │   │   ├── members/
│   │   │   │   │   └── settings/
│   │   │   │   └── new/
│   │   │   └── shared/ (NEW - this feature)
│   │   │       └── page.tsx
│   │   └── layout.tsx
│   ├── components/
│   │   ├── auth/
│   │   ├── tasks/
│   │   ├── teams/ (NEW - this feature)
│   │   │   ├── TeamCard.tsx
│   │   │   ├── TeamList.tsx
│   │   │   ├── TeamForm.tsx
│   │   │   ├── MemberList.tsx
│   │   │   ├── MemberInvite.tsx
│   │   │   └── RoleSelector.tsx
│   │   └── shared/ (NEW - this feature)
│   │       ├── ShareTaskModal.tsx
│   │       └── SharedTaskList.tsx
│   ├── lib/
│   │   ├── api/
│   │   │   ├── auth.ts
│   │   │   ├── tasks.ts (EXTEND - this feature)
│   │   │   ├── teams.ts (NEW - this feature)
│   │   │   └── shares.ts (NEW - this feature)
│   │   └── types/
│   │       ├── auth.ts
│   │       ├── task.ts (EXTEND - this feature)
│   │       ├── team.ts (NEW - this feature)
│   │       └── share.ts (NEW - this feature)
│   └── hooks/
│       ├── useAuth.ts
│       ├── useTasks.ts (EXTEND - this feature)
│       ├── useTeams.ts (NEW - this feature)
│       └── useShares.ts (NEW - this feature)
└── tests/
    └── [frontend test files]
```

**Structure Decision**: Web application structure (Option 2) with separate backend and frontend directories. This feature extends existing backend models, services, and routes while adding new team-related modules. Frontend adds new pages for team management and task sharing while extending existing task components to support team context. All new files are clearly marked as "NEW" while extensions to existing files are marked as "EXTEND".

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**Status**: No constitutional violations detected. All principles satisfied.

This section is intentionally left empty as the Constitution Check passed without any violations requiring justification.

---

## Phase 0: Research & Architectural Decisions

**Status**: ✅ Complete

**Output**: `research.md` - Comprehensive architectural research document

**Key Decisions Made**:

1. **RBAC Implementation**: Fixed 4-role system (Owner/Admin/Member/Viewer) with ENUM-based storage and FastAPI dependency injection for permission checks
2. **Team Ownership Model**: Single-owner model with atomic ownership transfer via role promotion
3. **Task Sharing vs Team Access**: Independent, orthogonal systems that can coexist with clear precedence rules
4. **Database Schema Design**: Three new normalized tables (teams, team_members, task_shares) plus extended tasks table with nullable team_id
5. **API Design Pattern**: RESTful with resource-based endpoints and nested routes for sub-resources
6. **Transaction Management**: Database transactions for all multi-record operations
7. **Permission Middleware**: FastAPI dependency functions for composable, reusable permission checks

**Alternatives Considered**: Dynamic permission systems, ABAC, multiple owners, unified permission system, GraphQL, application-level locking

**Rationale**: All decisions prioritize simplicity, security, performance, and maintainability while aligning with constitutional principles and existing technology stack.

**Research Document**: See `specs/003-teams-rbac-sharing/research.md` for complete details.

---

## Phase 1: Design & Contracts

**Status**: ✅ Complete

**Outputs**:
- `data-model.md` - Complete entity definitions with SQLModel schemas
- `contracts/api-contracts.md` - All 18 API endpoints with request/response formats
- `quickstart.md` - Implementation guide for developers
- `CLAUDE.md` - Updated agent context

### Data Model Summary

**New Entities**:
1. **Team**: Collaboration group with name, description, owner (3 new tables)
2. **TeamMember**: Junction table with role-based membership (ENUM: owner/admin/member/viewer)
3. **TaskShare**: Direct sharing with permission levels (ENUM: view/edit)

**Extended Entities**:
1. **Task**: Added nullable team_id for backward compatibility
2. **User**: Added relationships for teams, memberships, and shares

**Database Changes**:
- 3 new tables with proper foreign keys and unique constraints
- 1 extended table (tasks.team_id nullable)
- 10 new indexes for query performance
- Migration strategy with rollback support

### API Contracts Summary

**18 Total Endpoints**:
- **Teams** (5): POST, GET, GET/:id, PATCH/:id, DELETE/:id
- **Team Members** (4): POST, PATCH/:user_id, DELETE/:user_id, POST/leave
- **Tasks Extended** (5): POST (with team_id), GET (with filters), GET/:id, PATCH/:id, DELETE/:id
- **Task Sharing** (3): POST/share, DELETE/share/:user_id, GET/shared-with-me

**Authentication**: All endpoints require JWT (Bearer token)
**Authorization**: Role-based permissions enforced at API layer
**Error Handling**: Consistent error format with proper HTTP status codes

### Implementation Sequence

**Priority 1 (Foundation)**:
1. Database schema (neon-db-architect)
2. Pydantic schemas (fastapi-backend)
3. Permission middleware (secure-auth-agent)
4. Service layer (fastapi-backend)
5. API routes (fastapi-backend)
6. Backend testing (fastapi-backend)

**Priority 2 (User Interface)**:
7. Frontend components (nextjs-ui-builder)
8. Frontend integration (nextjs-ui-builder)

### Agent Context Update

Updated `CLAUDE.md` with:
- Language: Python 3.11+ (Backend), TypeScript/JavaScript (Frontend)
- Database: Neon Serverless PostgreSQL with connection pooling
- Project Type: Web application (FastAPI backend + Next.js frontend)

---

## Constitution Check (Post-Design)

*Re-evaluation after Phase 1 design completion*

### Principle I: Spec-Driven Development ✅
- **Status**: PASS
- **Evidence**: All design artifacts (data model, API contracts, quickstart) directly derived from approved specification
- **Compliance**: Implementation will follow design artifacts exactly

### Principle II: Agentic Workflow Integrity ✅
- **Status**: PASS
- **Evidence**: Clear agent assignments in quickstart guide, no manual coding planned
- **Compliance**: Specialized agents will handle their respective domains

### Principle III: Correctness & Consistency ✅
- **Status**: PASS
- **Evidence**: Data model and API contracts are fully aligned, shared type definitions planned
- **Compliance**: OpenAPI schema will ensure contract consistency

### Principle IV: Security by Design ✅
- **Status**: PASS
- **Evidence**: Permission middleware designed, all endpoints require JWT, role-based access control enforced
- **Compliance**: Security is first-class in design

### Principle V: Separation of Concerns ✅
- **Status**: PASS
- **Evidence**: Clear layer separation (models, schemas, services, routes, middleware)
- **Compliance**: Each layer has distinct responsibilities

**GATE RESULT**: ✅ PASS - Design maintains constitutional compliance. Ready for task generation with `/sp.tasks`.

---

## Next Steps

1. **Generate Tasks**: Run `/sp.tasks` to break down implementation into testable tasks
2. **Implement**: Execute tasks using specialized agents (neon-db-architect, secure-auth-agent, fastapi-backend, nextjs-ui-builder)
3. **Test**: Comprehensive testing at each phase (unit, integration, security, performance)
4. **Document**: Create ADRs for significant decisions if needed
5. **Commit**: Use `/sp.git.commit_pr` to commit and create pull request

---

## Artifacts Generated

| Artifact | Status | Location |
|----------|--------|----------|
| Implementation Plan | ✅ Complete | `specs/003-teams-rbac-sharing/plan.md` |
| Research Document | ✅ Complete | `specs/003-teams-rbac-sharing/research.md` |
| Data Model | ✅ Complete | `specs/003-teams-rbac-sharing/data-model.md` |
| API Contracts | ✅ Complete | `specs/003-teams-rbac-sharing/contracts/api-contracts.md` |
| Quickstart Guide | ✅ Complete | `specs/003-teams-rbac-sharing/quickstart.md` |
| Agent Context | ✅ Updated | `CLAUDE.md` |
| Tasks Document | ⏳ Pending | Run `/sp.tasks` to generate |

---

**Planning Phase Complete**: All design artifacts generated. Ready for task generation and implementation.
