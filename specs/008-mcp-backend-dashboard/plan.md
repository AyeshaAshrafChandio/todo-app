# Implementation Plan: MCP Backend Data & Dashboard

**Branch**: `008-mcp-backend-dashboard` | **Date**: 2026-02-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/008-mcp-backend-dashboard/spec.md`

## Summary

This feature implements a comprehensive database schema for AI chat functionality (tasks, conversations, messages) and a live dashboard showing task statistics (total, pending, completed, shared). The dashboard updates in real-time via polling (MVP) with optional WebSocket enhancement. All data is stored in Neon Serverless PostgreSQL with strict user/team isolation enforced at the database level.

**Technical Approach**:
- Use SQLModel + Alembic for database schema and migrations
- Implement FastAPI endpoints for dashboard statistics with JWT authentication
- Build Next.js dashboard page with polling-based real-time updates
- Enforce data isolation through user_id filtering in all database queries
- Optional WebSocket integration for instant updates (enhancement)

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript 5.x (frontend), Node.js 18+ (frontend runtime)
**Primary Dependencies**:
- Backend: FastAPI, SQLModel, Alembic, Pydantic, python-jose (JWT), asyncpg (Neon driver)
- Frontend: Next.js 14+, React 18+, TypeScript, Tailwind CSS, SWR (data fetching)
**Storage**: Neon Serverless PostgreSQL (existing connection configured)
**Testing**: pytest + pytest-asyncio (backend), Jest/Vitest (frontend), Playwright (E2E)
**Target Platform**: Web application (Linux server + modern browsers)
**Project Type**: Web (backend + frontend)
**Performance Goals**:
- API response time < 100ms (p95)
- Dashboard statistics query < 50ms
- Dashboard UI updates within 5 seconds (polling mode)
- Support 100+ concurrent dashboard users
**Constraints**:
- Backend MUST be stateless (no in-memory session state)
- All API endpoints MUST require JWT authentication
- Database queries MUST filter by user_id for data isolation
- Polling interval MUST be 5 seconds (balance between real-time and server load)
- WebSocket connections MUST auto-reconnect on disconnect
**Scale/Scope**:
- Multi-user application (100+ users)
- 6 database tables (tasks, conversations, messages, teams, team_members, task_shares)
- 3 API endpoints (statistics, WebSocket optional)
- 1 dashboard page with 4 statistics cards

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Spec-Driven Development ✅
- Complete specification exists at `specs/008-mcp-backend-dashboard/spec.md`
- All requirements documented with acceptance criteria
- Implementation will follow approved spec exactly

### Principle II: Agentic Workflow Integrity ✅
- Will use specialized agents:
  - `neon-db-architect` for database schema and migrations
  - `fastapi-backend` for API endpoints and services
  - `nextjs-ui-builder` for dashboard UI components
- No manual code modifications planned

### Principle III: Correctness & Consistency ✅
- Data models will be consistent across backend and frontend
- API contracts will be explicitly defined in contracts/
- Error handling will be consistent across all layers

### Principle IV: Security by Design ✅
- All dashboard endpoints will require JWT authentication
- User data will be filtered by authenticated user_id from token
- Database queries will include user_id filter to prevent cross-user access
- Authorization middleware will validate permissions

### Principle V: Separation of Concerns ✅
- Database access through SQLModel ORM (no raw SQL in routes)
- Business logic in services (dashboard_service.py, task_service.py)
- API routes only handle HTTP concerns
- Frontend communicates only through REST APIs

### Principle VI: Stateless Architecture ✅
- Backend holds no in-memory state
- All data persisted to Neon PostgreSQL
- Dashboard statistics computed from database per request
- Caching layer (5 seconds) uses time-based expiration, not session state

### Principle X: Backward Compatibility ✅
- No modifications to existing Phase I & II APIs
- New tables added (no changes to existing schema)
- New endpoints added (no changes to existing routes)
- Existing authentication flow unchanged

### Technology Stack Compliance ✅
- Backend: FastAPI ✅
- ORM: SQLModel ✅
- Database: Neon Serverless PostgreSQL ✅
- Frontend: Next.js 14+ ✅
- Authentication: Better Auth (JWT) ✅

**GATE STATUS**: ✅ PASS - All constitutional principles satisfied

## Project Structure

### Documentation (this feature)

```text
specs/008-mcp-backend-dashboard/
├── spec.md              # Feature specification (COMPLETE)
├── plan.md              # This file (IN PROGRESS)
├── research.md          # Phase 0 output (PENDING)
├── data-model.md        # Phase 1 output (PENDING)
├── quickstart.md        # Phase 1 output (PENDING)
├── contracts/           # Phase 1 output (PENDING)
│   ├── dashboard-api.yaml
│   └── websocket-events.yaml
└── tasks.md             # Phase 2 output (COMPLETE - already generated)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── models/
│   │   ├── task.py              # EXISTING - may need updates
│   │   ├── conversation.py      # NEW - Phase 3 (US1)
│   │   ├── message.py           # NEW - Phase 3 (US1)
│   │   ├── team.py              # NEW - Phase 4 (US2)
│   │   ├── team_member.py       # NEW - Phase 4 (US2)
│   │   └── task_share.py        # NEW - Phase 4 (US2)
│   ├── schemas/
│   │   └── dashboard.py         # NEW - Phase 5 (US3)
│   ├── services/
│   │   ├── task_service.py      # EXISTING - may need updates
│   │   ├── dashboard_service.py # NEW - Phase 5 (US3)
│   │   ├── cache_service.py     # NEW - Phase 5 (US3)
│   │   └── websocket_manager.py # NEW - Phase 7 (US5)
│   ├── routes/
│   │   ├── dashboard.py         # NEW - Phase 5 (US3)
│   │   └── websocket.py         # NEW - Phase 7 (US5)
│   ├── middleware/
│   │   ├── authorization.py     # NEW - Phase 8 (US6)
│   │   └── performance.py       # NEW - Phase 9 (Polish)
│   └── database/
│       ├── connection.py        # EXISTING - may need updates
│       ├── session.py           # NEW - Phase 2 (Foundational)
│       ├── init_db.py           # NEW - Phase 2 (Foundational)
│       ├── indexes.py           # NEW - Phase 2 (Foundational)
│       └── seed.py              # NEW - Phase 3 (US1)
├── alembic/
│   └── versions/
│       ├── 001_create_tasks_table.py       # NEW - Phase 3 (US1)
│       ├── 002_create_conversations_table.py # NEW - Phase 3 (US1)
│       ├── 003_create_messages_table.py    # NEW - Phase 3 (US1)
│       ├── 004_add_indexes.py              # NEW - Phase 3 (US1)
│       ├── 005_create_teams_table.py       # NEW - Phase 4 (US2)
│       ├── 006_create_team_members_table.py # NEW - Phase 4 (US2)
│       ├── 007_create_task_shares_table.py # NEW - Phase 4 (US2)
│       ├── 008_add_team_indexes.py         # NEW - Phase 4 (US2)
│       └── 009_optimize_indexes.py         # NEW - Phase 9 (Polish)
└── tests/
    ├── test_database_schema.py  # NEW - Phase 3 (US1)
    ├── test_team_schema.py      # NEW - Phase 4 (US2)
    ├── test_dashboard_api.py    # NEW - Phase 5 (US3)
    ├── test_data_isolation.py   # NEW - Phase 8 (US6)
    └── test_security.py         # NEW - Phase 8 (US6)

frontend/
├── src/
│   ├── app/
│   │   └── (protected)/
│   │       └── dashboard/
│   │           ├── page.tsx              # NEW - Phase 6 (US4)
│   │           └── DashboardClient.tsx   # NEW - Phase 6 (US4)
│   ├── components/
│   │   └── dashboard/
│   │       ├── DashboardLayout.tsx       # NEW - Phase 6 (US4)
│   │       ├── StatisticsCard.tsx        # NEW - Phase 6 (US4)
│   │       └── ConnectionStatus.tsx      # NEW - Phase 7 (US5)
│   ├── hooks/
│   │   └── useDashboard.ts               # NEW - Phase 6 (US4)
│   ├── lib/
│   │   ├── api/
│   │   │   └── dashboard.ts              # NEW - Phase 6 (US4)
│   │   └── websocket/
│   │       └── client.ts                 # NEW - Phase 7 (US5)
└── tests/
    ├── dashboard.spec.ts        # NEW - Phase 6 (US4)
    └── websocket.spec.ts        # NEW - Phase 7 (US5)
```

**Structure Decision**: Web application structure (Option 2) selected because this feature spans both backend (database, API) and frontend (dashboard UI). Backend handles data persistence and API endpoints, frontend provides user interface. Clear separation enables parallel development by specialized agents.

## Complexity Tracking

> **No constitutional violations detected - this section is empty**

All implementation follows constitutional principles:
- Stateless backend architecture maintained
- JWT authentication enforced
- Data isolation at database level
- Separation of concerns preserved
- Backward compatibility maintained
- Technology stack compliant

## Phase 0: Research & Unknowns

**Status**: PENDING

### Research Tasks

1. **Neon Serverless Connection Pooling**
   - Decision: How to configure connection pooling for serverless environment
   - Rationale: Neon requires specific pooling configuration for optimal performance
   - Research: Review Neon documentation for FastAPI + SQLModel best practices

2. **Dashboard Statistics Caching Strategy**
   - Decision: How to implement 5-second cache without in-memory state
   - Rationale: Need to balance real-time updates with database load
   - Research: Evaluate time-based caching vs. Redis vs. database-level caching

3. **WebSocket Implementation for FastAPI**
   - Decision: Which WebSocket library to use (websockets, socket.io, FastAPI native)
   - Rationale: Need reliable WebSocket support with auto-reconnect
   - Research: Compare FastAPI WebSocket support vs. Socket.IO for Python

4. **Next.js Polling vs. SWR**
   - Decision: Use custom polling logic or SWR library for data fetching
   - Rationale: SWR provides built-in polling, caching, and error handling
   - Research: Evaluate SWR vs. custom useEffect polling implementation

5. **Database Index Strategy**
   - Decision: Which indexes to create for optimal query performance
   - Rationale: Dashboard queries need to be fast (< 50ms)
   - Research: Analyze query patterns and determine optimal index strategy

**Output**: research.md with all decisions documented

## Phase 1: Design & Contracts

**Status**: PENDING

### Data Model (data-model.md)

**Entities to define**:
1. Task (existing - may need updates)
2. Conversation (new)
3. Message (new)
4. Team (new)
5. TeamMember (new)
6. TaskShare (new)

**Relationships**:
- Task → User (many-to-one)
- Conversation → User (many-to-one)
- Message → Conversation (many-to-one)
- Team → User (owner, many-to-one)
- TeamMember → Team, User (many-to-one each)
- TaskShare → Task, User (many-to-one each)

### API Contracts (contracts/)

**Endpoints to define**:
1. `GET /api/dashboard/statistics` - Returns task statistics
   - Request: JWT token in Authorization header
   - Response: `{total_tasks, pending_tasks, completed_tasks, shared_tasks}`
   - Status codes: 200 OK, 401 Unauthorized, 500 Internal Server Error

2. `WS /api/ws` - WebSocket connection for real-time updates (optional)
   - Events: `task_created`, `task_updated`, `task_deleted`, `task_completed`
   - Payload: `{event_type, task_id, user_id, timestamp}`

### Quickstart Guide (quickstart.md)

**Sections to include**:
1. Prerequisites (Neon database, Python 3.11+, Node.js 18+)
2. Database setup (run migrations)
3. Backend setup (install dependencies, configure .env)
4. Frontend setup (install dependencies, configure .env)
5. Running the application
6. Testing the dashboard
7. Troubleshooting common issues

**Output**: data-model.md, contracts/, quickstart.md

## Phase 2: Tasks Generation

**Status**: COMPLETE ✅

Tasks already generated at `specs/008-mcp-backend-dashboard/tasks.md` with 67 tasks across 9 phases:
- Phase 1: Setup (4 tasks)
- Phase 2: Foundational (5 tasks)
- Phase 3: User Story 1 - Database Schema (9 tasks)
- Phase 4: User Story 2 - Team and Sharing (9 tasks)
- Phase 5: User Story 3 - Dashboard API (7 tasks)
- Phase 6: User Story 4 - Dashboard UI (9 tasks)
- Phase 7: User Story 5 - WebSockets (9 tasks)
- Phase 8: User Story 6 - Security (7 tasks)
- Phase 9: Polish (8 tasks)

**MVP Scope**: Phases 1-2-3-5-6 (43 tasks) for working database + dashboard with polling

## Implementation Notes

### Database Migrations Strategy
- Use Alembic for all schema changes
- Migrations must be numbered sequentially (001, 002, 003...)
- Each migration must be idempotent (can run multiple times safely)
- Test migrations on local database before production

### Authentication Flow
1. Frontend includes JWT token in `Authorization: Bearer <token>` header
2. Backend extracts token using `get_current_user` dependency
3. Backend validates token signature and expiration
4. Backend extracts user_id from token payload
5. Backend filters all queries by user_id

### Dashboard Update Strategy
- **MVP (US4)**: Polling every 5 seconds using SWR or custom hook
- **Enhancement (US5)**: WebSocket push updates for instant feedback
- Both approaches must maintain same API contract

### Data Isolation Enforcement
- All database queries MUST include `WHERE user_id = {authenticated_user_id}`
- Team queries MUST include `WHERE team_id IN (SELECT team_id FROM team_members WHERE user_id = {authenticated_user_id})`
- Shared task queries MUST include `WHERE task_id IN (SELECT task_id FROM task_shares WHERE shared_with_user_id = {authenticated_user_id})`

### Performance Optimization
- Create indexes on frequently queried columns (user_id, status, created_at)
- Use database connection pooling for Neon Serverless
- Implement 5-second cache for dashboard statistics
- Use COUNT queries instead of fetching all records

### Error Handling
- API errors return consistent JSON format: `{"error": "message", "detail": "optional"}`
- Frontend displays user-friendly error messages
- Retry logic for transient failures (network errors, database timeouts)
- Graceful degradation when WebSocket unavailable (fall back to polling)

## Risk Analysis

### High Priority Risks

1. **Database Connection Pooling**
   - Risk: Neon Serverless requires specific pooling configuration
   - Mitigation: Research Neon best practices in Phase 0, test with load

2. **Real-Time Update Performance**
   - Risk: Polling every 5 seconds may cause high database load
   - Mitigation: Implement caching layer, monitor query performance

3. **Data Isolation Bugs**
   - Risk: Missing user_id filter could leak data across users
   - Mitigation: Comprehensive security testing, code review of all queries

### Medium Priority Risks

4. **WebSocket Connection Stability**
   - Risk: WebSocket connections may drop frequently
   - Mitigation: Implement auto-reconnect, fall back to polling

5. **Migration Conflicts**
   - Risk: Multiple developers creating migrations simultaneously
   - Mitigation: Sequential migration numbering, merge conflict resolution

### Low Priority Risks

6. **Frontend Polling Overhead**
   - Risk: Many open dashboard tabs could overwhelm backend
   - Mitigation: Rate limiting, connection pooling, monitoring

## Success Metrics

- [ ] All 6 database tables created successfully
- [ ] Dashboard statistics API returns accurate counts
- [ ] Dashboard UI updates within 5 seconds of task changes
- [ ] 100% data isolation (users only see their own tasks)
- [ ] API response time < 100ms (p95)
- [ ] Database query time < 50ms
- [ ] Zero unauthorized data access in security testing
- [ ] WebSocket connections remain stable for 1+ hour (if implemented)

## Next Steps

1. Execute Phase 0: Research (resolve all unknowns)
2. Execute Phase 1: Design & Contracts (data-model.md, contracts/, quickstart.md)
3. Update agent context with new technologies
4. Proceed to implementation via `/sp.implement` command
