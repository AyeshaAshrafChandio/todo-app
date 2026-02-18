# Research: MCP Backend Data & Dashboard

**Feature**: 008-mcp-backend-dashboard
**Date**: 2026-02-07
**Status**: Complete

## Research Questions & Decisions

### 1. Neon Serverless Connection Pooling

**Question**: How to configure connection pooling for Neon Serverless with FastAPI + SQLModel?

**Research Findings**:
- Neon Serverless PostgreSQL uses connection pooling at the infrastructure level
- For FastAPI + SQLModel, use `create_engine` with specific pool settings
- Recommended configuration for serverless:
  - `pool_size=5` (small pool for serverless)
  - `max_overflow=10` (allow burst connections)
  - `pool_pre_ping=True` (verify connections before use)
  - `pool_recycle=3600` (recycle connections every hour)

**Decision**: Use SQLModel with custom engine configuration
```python
from sqlmodel import create_engine
from sqlalchemy.pool import NullPool

# For serverless, use NullPool to avoid connection pooling issues
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,  # No pooling for serverless
    echo=False,
    connect_args={"sslmode": "require"}
)
```

**Rationale**: NullPool is recommended for serverless environments because connections are short-lived and pooling can cause issues with connection limits. Neon handles pooling at the infrastructure level.

**Alternatives Considered**:
- QueuePool with small pool_size: Rejected because serverless functions are ephemeral
- PGBouncer: Rejected because Neon provides built-in connection pooling

---

### 2. Dashboard Statistics Caching Strategy

**Question**: How to implement 5-second cache without in-memory state?

**Research Findings**:
- Time-based caching can be implemented using Python's `functools.lru_cache` with TTL
- Redis would require additional infrastructure (out of scope for MVP)
- Database-level caching (materialized views) requires PostgreSQL 9.3+
- Simple approach: Cache at application level with timestamp validation

**Decision**: Use time-based in-memory cache with TTL
```python
from datetime import datetime, timedelta
from typing import Optional

class CacheService:
    def __init__(self, ttl_seconds: int = 5):
        self._cache = {}
        self._ttl = timedelta(seconds=ttl_seconds)

    def get(self, key: str) -> Optional[dict]:
        if key in self._cache:
            value, timestamp = self._cache[key]
            if datetime.utcnow() - timestamp < self._ttl:
                return value
        return None

    def set(self, key: str, value: dict):
        self._cache[key] = (value, datetime.utcnow())
```

**Rationale**: Simple, no external dependencies, sufficient for 5-second TTL. Cache is per-user (keyed by user_id), so no cross-user data leakage. Stateless in the sense that cache can be rebuilt from database at any time.

**Alternatives Considered**:
- Redis: Rejected due to additional infrastructure complexity for MVP
- Materialized views: Rejected because requires manual refresh triggers
- No caching: Rejected because would cause high database load with polling

---

### 3. WebSocket Implementation for FastAPI

**Question**: Which WebSocket library to use for real-time updates?

**Research Findings**:
- FastAPI has native WebSocket support via Starlette
- Socket.IO requires additional library (python-socketio) and client-side library
- Native WebSocket is simpler and sufficient for this use case
- FastAPI WebSocket example:
```python
from fastapi import WebSocket

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message: {data}")
```

**Decision**: Use FastAPI native WebSocket support
- Endpoint: `ws://localhost:8001/api/ws`
- Authentication: Validate JWT token in query parameter or first message
- Events: JSON messages with `{event_type, payload, timestamp}`
- Reconnection: Client-side auto-reconnect with exponential backoff

**Rationale**: Native support is simpler, no additional dependencies, sufficient for dashboard updates. Socket.IO adds complexity without significant benefit for this use case.

**Alternatives Considered**:
- Socket.IO: Rejected due to additional complexity and dependencies
- Server-Sent Events (SSE): Rejected because WebSocket provides bidirectional communication
- Long polling: Rejected because already using short polling for MVP

---

### 4. Next.js Polling vs. SWR

**Question**: Use custom polling logic or SWR library for data fetching?

**Research Findings**:
- SWR (stale-while-revalidate) is a React Hooks library for data fetching
- Built-in features: caching, revalidation, polling, error handling
- SWR polling example:
```typescript
import useSWR from 'swr'

const { data, error } = useSWR('/api/dashboard/statistics', fetcher, {
  refreshInterval: 5000, // Poll every 5 seconds
  revalidateOnFocus: true,
  revalidateOnReconnect: true
})
```

**Decision**: Use SWR for dashboard data fetching
- Install: `npm install swr`
- Configure: 5-second refresh interval
- Error handling: Built-in retry with exponential backoff
- Caching: Automatic with stale-while-revalidate strategy

**Rationale**: SWR provides all required features out-of-the-box (polling, caching, error handling, loading states). Reduces custom code and improves reliability.

**Alternatives Considered**:
- Custom useEffect polling: Rejected because requires manual implementation of caching, error handling, and retry logic
- React Query: Rejected because SWR is simpler and sufficient for this use case
- Native fetch with setInterval: Rejected due to lack of built-in error handling and caching

---

### 5. Database Index Strategy

**Question**: Which indexes to create for optimal query performance?

**Research Findings**:
- Dashboard statistics query pattern:
  ```sql
  SELECT COUNT(*) FROM tasks WHERE user_id = ? AND status = ?
  ```
- Indexes needed:
  - `tasks(user_id)` - Filter by user
  - `tasks(user_id, status)` - Composite index for filtered counts
  - `conversations(user_id)` - Filter conversations by user
  - `messages(conversation_id)` - Filter messages by conversation
  - `team_members(user_id)` - Find user's teams
  - `task_shares(shared_with_user_id)` - Find shared tasks

**Decision**: Create composite indexes for common query patterns
```sql
-- Tasks table
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_user_status ON tasks(user_id, status);
CREATE INDEX idx_tasks_created_at ON tasks(created_at DESC);

-- Conversations table
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_created_at ON conversations(created_at DESC);

-- Messages table
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at DESC);

-- Teams table
CREATE INDEX idx_teams_owner_id ON teams(owner_id);

-- Team members table
CREATE INDEX idx_team_members_team_id ON team_members(team_id);
CREATE INDEX idx_team_members_user_id ON team_members(user_id);

-- Task shares table
CREATE INDEX idx_task_shares_task_id ON task_shares(task_id);
CREATE INDEX idx_task_shares_shared_with_user_id ON task_shares(shared_with_user_id);
```

**Rationale**: Composite indexes optimize the most common query patterns. Single-column indexes provide flexibility for other queries. Descending indexes on created_at support "recent items" queries.

**Alternatives Considered**:
- Single-column indexes only: Rejected because composite indexes significantly improve filtered count queries
- Full-text search indexes: Rejected because not needed for dashboard statistics
- Partial indexes: Rejected because all statuses need to be counted

---

## Technology Stack Summary

### Backend
- **Language**: Python 3.11+
- **Framework**: FastAPI (latest stable)
- **ORM**: SQLModel (latest stable)
- **Migrations**: Alembic (latest stable)
- **Database Driver**: asyncpg (for Neon PostgreSQL)
- **Authentication**: python-jose (JWT validation)
- **WebSocket**: FastAPI native (Starlette)
- **Testing**: pytest, pytest-asyncio

### Frontend
- **Language**: TypeScript 5.x
- **Framework**: Next.js 14+ (App Router)
- **UI Library**: React 18+
- **Styling**: Tailwind CSS
- **Data Fetching**: SWR (stale-while-revalidate)
- **WebSocket Client**: Native WebSocket API
- **Testing**: Jest/Vitest, Playwright (E2E)

### Database
- **Provider**: Neon Serverless PostgreSQL
- **Connection**: NullPool (no pooling for serverless)
- **SSL**: Required (sslmode=require)

### Deployment
- **Backend**: Uvicorn ASGI server
- **Frontend**: Vercel or similar Next.js hosting
- **Environment**: Production-ready with .env configuration

---

## Best Practices

### Database
1. Always use parameterized queries (SQLModel handles this)
2. Create indexes before deploying to production
3. Test migrations on local database first
4. Use transactions for multi-table operations
5. Monitor query performance with EXPLAIN ANALYZE

### API
1. Validate JWT token on every protected endpoint
2. Return consistent error format: `{"error": "message", "detail": "optional"}`
3. Use HTTP status codes correctly (200, 201, 400, 401, 403, 404, 500)
4. Log all API requests for debugging
5. Implement rate limiting for production

### Frontend
1. Use SWR for all data fetching (consistent caching and error handling)
2. Display loading states during API calls
3. Show user-friendly error messages with retry option
4. Implement optimistic updates for better UX
5. Test on mobile, tablet, and desktop devices

### Security
1. Never trust client-supplied user_id (always use JWT token)
2. Filter all database queries by authenticated user_id
3. Validate all input parameters with Pydantic schemas
4. Use HTTPS in production (enforce SSL)
5. Implement CORS properly (whitelist frontend origin)

### Testing
1. Test data isolation thoroughly (users cannot see other users' data)
2. Test error scenarios (network failures, database timeouts)
3. Test WebSocket reconnection logic
4. Test dashboard with multiple concurrent users
5. Test migration rollback procedures

---

## Implementation Priorities

### MVP (Must Have)
1. Database schema (tasks, conversations, messages)
2. Dashboard statistics API with JWT authentication
3. Dashboard UI with polling (5-second refresh)
4. Data isolation by user_id
5. Basic error handling

### Enhancement (Nice to Have)
1. Team and sharing tables
2. WebSocket real-time updates
3. Advanced security (audit logging, rate limiting)
4. Performance optimization (query caching, connection pooling)
5. Comprehensive E2E testing

### Future (Out of Scope)
1. Task notifications
2. Advanced analytics
3. Export/import functionality
4. Mobile app
5. Third-party integrations

---

## Risk Mitigation

### High Priority
1. **Data Isolation**: Comprehensive security testing to prevent cross-user access
2. **Performance**: Load testing with 100+ concurrent users
3. **Connection Pooling**: Test Neon connection limits under load

### Medium Priority
4. **WebSocket Stability**: Implement auto-reconnect and fallback to polling
5. **Migration Safety**: Test rollback procedures before production

### Low Priority
6. **Cache Invalidation**: Monitor cache hit rates and adjust TTL if needed
7. **Error Handling**: Ensure all error paths return user-friendly messages

---

## Conclusion

All technical unknowns have been resolved. The implementation plan is ready to proceed to Phase 1 (Design & Contracts).

**Key Decisions**:
1. Use NullPool for Neon Serverless connection management
2. Implement time-based caching with 5-second TTL
3. Use FastAPI native WebSocket support
4. Use SWR for frontend data fetching with polling
5. Create composite indexes for optimal query performance

**Next Steps**:
1. Generate data-model.md with entity definitions
2. Generate API contracts in contracts/
3. Generate quickstart.md with setup instructions
4. Update agent context with new technologies
5. Proceed to implementation via /sp.implement
