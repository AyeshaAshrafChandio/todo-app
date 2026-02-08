# Research: Authentication & API Security

**Feature**: 002-auth-api-security
**Date**: 2026-02-04
**Status**: Completed

This document captures research findings and technology decisions for implementing JWT-based authentication and authorization in the Todo application.

## Research Topic 1: Better Auth Configuration for Next.js with JWT Token Issuance

### Decision
Use Better Auth v1.x with JWT session strategy configured to issue tokens containing `user_id` and `email` claims.

### Rationale
- **Better Auth** is specifically designed for Next.js with built-in JWT support
- Provides type-safe authentication with minimal configuration
- Supports both client and server components in Next.js App Router
- Handles token storage, refresh, and session management automatically
- Integrates seamlessly with Next.js middleware for route protection

### Configuration Approach
```typescript
// lib/auth.ts
import { betterAuth } from "better-auth"

export const auth = betterAuth({
  secret: process.env.BETTER_AUTH_SECRET,
  session: {
    strategy: "jwt",
    expiresIn: 60 * 60 * 24, // 24 hours
  },
  jwt: {
    claims: {
      userId: "user.id",
      email: "user.email"
    }
  }
})
```

### Alternatives Considered
1. **NextAuth.js (Auth.js)**: More mature but heavier, requires database adapter for JWT
2. **Clerk**: Third-party service, adds external dependency and cost
3. **Custom JWT implementation**: More control but requires significant boilerplate

### References
- Better Auth Documentation: https://better-auth.com/docs
- Next.js App Router Authentication: https://nextjs.org/docs/app/building-your-application/authentication

---

## Research Topic 2: PyJWT vs python-jose for JWT Verification in FastAPI

### Decision
Use **PyJWT** (version 2.8+) for JWT token verification in FastAPI backend.

### Rationale
- **Simpler API**: PyJWT has a more straightforward API for basic JWT operations
- **Lightweight**: Fewer dependencies than python-jose
- **Well-maintained**: Active development and security updates
- **Performance**: Faster for basic JWT operations (encode/decode)
- **Sufficient features**: Supports HS256, RS256, and all required JWT operations
- **Better error messages**: More descriptive exceptions for debugging

### Implementation Pattern
```python
import jwt
from datetime import datetime, timedelta

def verify_jwt_token(token: str, secret: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            secret,
            algorithms=["HS256"],
            options={"verify_exp": True}
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### Alternatives Considered
1. **python-jose**: More features (JWE, JWS) but heavier, includes cryptography library
2. **authlib**: Full OAuth/OIDC library, overkill for simple JWT verification
3. **Custom implementation**: Security risk, not recommended

### Benchmark Comparison
- PyJWT decode: ~0.5ms per token
- python-jose decode: ~0.8ms per token
- Both well under the 50ms performance requirement

### References
- PyJWT Documentation: https://pyjwt.readthedocs.io/
- FastAPI Security: https://fastapi.tiangolo.com/tutorial/security/

---

## Research Topic 3: FastAPI Dependency Injection Pattern for JWT Verification

### Decision
Use FastAPI's **Depends()** with a reusable dependency function that extracts and verifies JWT tokens from the Authorization header.

### Rationale
- **Declarative**: Clear indication that endpoint requires authentication
- **Reusable**: Single dependency function used across all protected endpoints
- **Type-safe**: Returns typed user object for use in endpoint logic
- **Testable**: Easy to mock for testing
- **FastAPI native**: Follows framework best practices
- **Automatic documentation**: Swagger UI shows authentication requirement

### Implementation Pattern
```python
# app/middleware/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Dependency that verifies JWT token and returns user info.

    Raises:
        HTTPException: 401 if token is invalid or expired
    """
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token,
            settings.BETTER_AUTH_SECRET,
            algorithms=["HS256"]
        )
        return {
            "user_id": payload.get("userId"),
            "email": payload.get("email")
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

# Usage in routes
@router.get("/api/{user_id}/tasks")
def list_tasks(
    user_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify user_id matches authenticated user
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    # ... rest of endpoint logic
```

### Alternatives Considered
1. **Middleware**: Global middleware would apply to all routes, harder to exclude public endpoints
2. **Decorator pattern**: Less idiomatic in FastAPI, harder to test
3. **Manual header parsing**: Repetitive code, error-prone

### References
- FastAPI Dependencies: https://fastapi.tiangolo.com/tutorial/dependencies/
- FastAPI Security: https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/

---

## Research Topic 4: Database Migration Strategy for Adding user_id Foreign Key

### Decision
Use **SQLModel's create_all()** with conditional migration logic to add `user_id` foreign key to existing tasks table without data loss.

### Rationale
- **Backward compatible**: Existing tasks remain accessible
- **No data loss**: All existing task data preserved
- **Simple**: Leverages SQLModel's built-in schema management
- **Testable**: Can be tested in development before production deployment

### Migration Strategy

**Option A: Add nullable user_id column (Recommended)**
```python
# app/models/task.py
class Task(SQLModel, table=True):
    # ... existing fields ...
    user_id: Optional[str] = Field(
        default=None,  # Allow NULL for existing tasks
        foreign_key="users.id",
        index=True
    )
```

**Migration Steps**:
1. Add User model with `id` as primary key
2. Modify Task model to include optional `user_id` field
3. Run `create_all()` to add column (SQLModel handles ALTER TABLE)
4. Existing tasks will have `user_id = NULL`
5. New tasks will require `user_id` (enforced in service layer)
6. Optional: Assign existing tasks to a default "system" user

**Option B: Create new tasks table and migrate data**
- More complex, requires data migration script
- Risk of data loss if migration fails
- Not recommended for this use case

### Handling Existing Tasks
```python
# app/services/task_service.py
def get_tasks_by_user(db: Session, user_id: str):
    # Only return tasks that belong to the user
    # Exclude tasks with NULL user_id (legacy tasks)
    return db.exec(
        select(Task)
        .where(Task.user_id == user_id)
    ).all()
```

### Alternatives Considered
1. **Alembic migrations**: More control but adds complexity, overkill for simple schema change
2. **Drop and recreate table**: Data loss, not acceptable
3. **Separate legacy_tasks table**: Unnecessary complexity

### References
- SQLModel Migrations: https://sqlmodel.tiangolo.com/tutorial/create-db-and-table/
- PostgreSQL ALTER TABLE: https://www.postgresql.org/docs/current/sql-altertable.html

---

## Research Topic 5: Error Handling Patterns for Authentication Failures

### Decision
Use **structured error responses** with specific HTTP status codes and descriptive error messages for different authentication failure scenarios.

### Rationale
- **Clear feedback**: Users understand why authentication failed
- **Security**: Avoid information disclosure (don't reveal if user exists)
- **Debugging**: Developers can diagnose issues quickly
- **Standards compliance**: Follows HTTP status code semantics
- **Consistent format**: All errors follow same JSON structure

### Error Response Pattern

**HTTP Status Codes**:
- **401 Unauthorized**: Missing, invalid, or expired token
- **403 Forbidden**: Valid token but insufficient permissions (cross-user access)
- **422 Unprocessable Entity**: Invalid request data (signup/login validation)

**Error Response Format**:
```json
{
  "detail": "Human-readable error message",
  "error_code": "MACHINE_READABLE_CODE",
  "timestamp": "2026-02-04T10:30:00Z"
}
```

**Specific Error Scenarios**:

1. **Missing Token**:
```python
# Status: 401
{
  "detail": "Authentication required. Please provide a valid token.",
  "error_code": "TOKEN_MISSING"
}
```

2. **Expired Token**:
```python
# Status: 401
{
  "detail": "Token expired. Please log in again.",
  "error_code": "TOKEN_EXPIRED"
}
```

3. **Invalid Token Signature**:
```python
# Status: 401
{
  "detail": "Invalid token signature.",
  "error_code": "TOKEN_INVALID"
}
```

4. **Cross-User Access Attempt**:
```python
# Status: 404 (not 403, to avoid information disclosure)
{
  "detail": "Task not found"
}
```

5. **Invalid Credentials (Login)**:
```python
# Status: 401
{
  "detail": "Invalid email or password.",
  "error_code": "INVALID_CREDENTIALS"
}
```

### Security Considerations
- **Don't reveal user existence**: Use generic "Invalid email or password" instead of "User not found"
- **Rate limiting**: Implement rate limiting on auth endpoints (future enhancement)
- **Logging**: Log all authentication failures for security monitoring
- **Token in URL**: Never accept tokens in URL parameters (only Authorization header)

### Implementation
```python
# app/middleware/auth.py
class AuthError(HTTPException):
    def __init__(self, detail: str, error_code: str):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "detail": detail,
                "error_code": error_code,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
```

### Alternatives Considered
1. **Generic 401 for all failures**: Less helpful for debugging
2. **Detailed error messages**: Security risk (information disclosure)
3. **Custom error codes**: More complex, standard HTTP codes sufficient

### References
- RFC 7235 (HTTP Authentication): https://tools.ietf.org/html/rfc7235
- OWASP Authentication Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html

---

## Research Topic 6: Token Expiration and Refresh Strategies

### Decision
Use **24-hour access tokens** with **automatic refresh** handled by Better Auth on the frontend.

### Rationale
- **Balance security and UX**: 24 hours is long enough to avoid frequent re-authentication but short enough to limit exposure
- **Stateless backend**: No refresh token storage required on backend
- **Better Auth handles refresh**: Frontend automatically refreshes tokens before expiration
- **Simple implementation**: No additional backend endpoints needed
- **Aligns with spec**: Spec doesn't require refresh token rotation (explicitly out of scope)

### Token Lifecycle

**Access Token**:
- **Expiration**: 24 hours (86400 seconds)
- **Claims**: `user_id`, `email`, `iat` (issued at), `exp` (expiration)
- **Algorithm**: HS256 (symmetric signing with shared secret)
- **Storage**: httpOnly cookie (managed by Better Auth)

**Refresh Flow** (handled by Better Auth):
1. Frontend detects token expiring soon (< 5 minutes remaining)
2. Better Auth automatically calls refresh endpoint
3. New token issued with fresh expiration
4. Old token remains valid until expiration (no revocation)

### Backend Configuration
```python
# app/config.py
class Settings(BaseSettings):
    BETTER_AUTH_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_SECONDS: int = 86400  # 24 hours
```

### Frontend Configuration
```typescript
// lib/auth.ts
export const auth = betterAuth({
  session: {
    strategy: "jwt",
    expiresIn: 60 * 60 * 24, // 24 hours
    updateAge: 60 * 60,      // Refresh if older than 1 hour
  }
})
```

### Token Expiration Handling

**Backend**:
```python
def verify_jwt_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.BETTER_AUTH_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            options={"verify_exp": True}  # Verify expiration
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthError("Token expired. Please log in again.", "TOKEN_EXPIRED")
```

**Frontend**:
```typescript
// Better Auth automatically handles token refresh
// No manual implementation needed
```

### Edge Cases

1. **Token expires mid-session**:
   - Frontend: Better Auth refreshes automatically
   - Backend: Returns 401, frontend redirects to login if refresh fails

2. **Secret rotation**:
   - All existing tokens become invalid
   - Users must re-authenticate
   - Acceptable for security updates

3. **Concurrent requests with expired token**:
   - All requests fail with 401
   - Frontend refreshes once, retries all failed requests

### Alternatives Considered

1. **Short-lived access tokens (15 min) + refresh tokens**:
   - More secure but complex
   - Requires refresh token storage and rotation
   - Out of scope per spec

2. **Long-lived tokens (7 days)**:
   - Better UX but security risk
   - Longer exposure window if token compromised

3. **Sliding expiration**:
   - Complex to implement
   - Requires backend state (violates stateless requirement)

### Security Notes
- **No token revocation**: Stateless design means tokens valid until expiration
- **Compromise mitigation**: 24-hour window limits exposure
- **Secret rotation**: Emergency measure for security incidents
- **HTTPS required**: Tokens must only be transmitted over HTTPS in production

### References
- JWT Best Practices: https://tools.ietf.org/html/rfc8725
- Better Auth Session Management: https://better-auth.com/docs/concepts/session

---

## Summary of Decisions

| Topic | Decision | Key Rationale |
|-------|----------|---------------|
| Frontend Auth | Better Auth with JWT | Native Next.js integration, type-safe |
| Backend JWT Library | PyJWT 2.8+ | Lightweight, simple API, well-maintained |
| Auth Pattern | FastAPI Depends() | Declarative, reusable, testable |
| Database Migration | Nullable user_id column | Backward compatible, no data loss |
| Error Handling | Structured 401/403 responses | Clear feedback, security-conscious |
| Token Expiration | 24-hour access tokens | Balance security and UX |

## Implementation Readiness

All research topics resolved. Ready to proceed to Phase 1: Design & Contracts.

**Next Steps**:
1. Create data-model.md with User and Task entity definitions
2. Generate OpenAPI contracts for auth and task endpoints
3. Create quickstart.md with setup instructions
4. Update agent context with new technologies
