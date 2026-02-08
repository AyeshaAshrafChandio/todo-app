# Research: Teams, RBAC, and Task Sharing

**Feature**: 003-teams-rbac-sharing
**Date**: 2026-02-04
**Status**: Complete

## Overview

This document consolidates research findings for implementing multi-user collaboration with team-based task management, role-based access control, and direct task sharing. All technical decisions align with the project constitution and leverage the existing FastAPI + SQLModel + Neon PostgreSQL stack.

## Key Architectural Decisions

### Decision 1: Role-Based Access Control (RBAC) Implementation

**Decision**: Implement RBAC using an ENUM-based role system with four fixed roles (Owner, Admin, Member, Viewer) stored in the team_members table, with permission checks performed at the API layer using dependency injection.

**Rationale**:
- **Simplicity**: Fixed roles are easier to reason about and test than dynamic permission systems
- **Performance**: Role checks are fast lookups without complex permission calculations
- **Type Safety**: SQLModel ENUM provides compile-time type checking
- **Maintainability**: Permission matrix is centralized and easy to audit
- **Security**: All permission checks happen at API layer before business logic executes

**Alternatives Considered**:
1. **Dynamic Permission System**: Rejected because it adds unnecessary complexity for the current scope (4 roles). Would require additional tables (permissions, role_permissions) and more complex queries.
2. **Attribute-Based Access Control (ABAC)**: Rejected because it's overkill for team-based permissions. ABAC is better suited for fine-grained, context-dependent access control.
3. **Client-Side Role Checks**: Rejected because it violates security-first principle. All authorization must happen server-side.

**Implementation Pattern**:
```python
# FastAPI dependency injection for role-based access
async def require_team_role(
    team_id: UUID,
    required_roles: List[TeamRole],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> TeamMember:
    member = get_team_member(db, team_id, current_user.id)
    if not member or member.role not in required_roles:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return member
```

### Decision 2: Team Ownership Model

**Decision**: Implement single-owner model where each team has exactly one owner, with ownership transferable through role promotion (promoting a member to owner automatically demotes current owner to admin).

**Rationale**:
- **Clear Accountability**: Single owner prevents confusion about who has ultimate authority
- **Simplified Logic**: No need to handle multiple owners or ownership conflicts
- **Database Integrity**: Enforced through unique constraint on (team_id, role='owner')
- **Smooth Transitions**: Ownership transfer is atomic (single transaction)

**Alternatives Considered**:
1. **Multiple Owners**: Rejected because it complicates decision-making and deletion logic. Who can delete the team if there are multiple owners?
2. **No Owner Role**: Rejected because teams need ultimate authority for deletion and critical operations.
3. **Immutable Ownership**: Rejected because it prevents legitimate ownership transfers (e.g., when original owner leaves organization).

**Implementation Pattern**:
```python
# Atomic ownership transfer
async def transfer_ownership(team_id: UUID, new_owner_id: UUID, db: Session):
    with db.begin():
        # Demote current owner to admin
        current_owner = db.query(TeamMember).filter(
            TeamMember.team_id == team_id,
            TeamMember.role == TeamRole.OWNER
        ).first()
        current_owner.role = TeamRole.ADMIN

        # Promote new owner
        new_owner = db.query(TeamMember).filter(
            TeamMember.team_id == team_id,
            TeamMember.user_id == new_owner_id
        ).first()
        new_owner.role = TeamRole.OWNER

        db.commit()
```

### Decision 3: Task Sharing vs Team Access

**Decision**: Implement task sharing and team access as independent, orthogonal systems that can coexist. A task can be both team-owned (team_id set) and directly shared with individual users.

**Rationale**:
- **Flexibility**: Users can share team tasks with external collaborators without adding them to the team
- **Separation of Concerns**: Team membership and task sharing have different lifecycles
- **Clear Precedence**: Team permissions take precedence for team members; direct shares apply to non-members
- **Backward Compatibility**: Personal tasks (team_id=null) can still be shared

**Alternatives Considered**:
1. **Unified Permission System**: Rejected because it would require complex permission resolution logic and make the system harder to reason about.
2. **Sharing Only Within Teams**: Rejected because it limits flexibility for cross-team collaboration.
3. **No Direct Sharing**: Rejected because it forces users to create teams for simple one-off collaborations.

**Permission Resolution Logic**:
```python
def can_access_task(user_id: UUID, task: Task, db: Session) -> Tuple[bool, str]:
    # 1. Owner always has full access
    if task.user_id == user_id:
        return (True, "owner")

    # 2. Check team membership if task is team-owned
    if task.team_id:
        member = get_team_member(db, task.team_id, user_id)
        if member:
            return (True, f"team_{member.role}")

    # 3. Check direct sharing
    share = get_task_share(db, task.id, user_id)
    if share:
        return (True, f"shared_{share.permission}")

    return (False, None)
```

### Decision 4: Database Schema Design

**Decision**: Use three new tables (teams, team_members, task_shares) with proper foreign keys and unique constraints, plus extend tasks table with nullable team_id column.

**Rationale**:
- **Normalization**: Proper 3NF design prevents data duplication
- **Referential Integrity**: Foreign keys ensure data consistency
- **Backward Compatibility**: Nullable team_id preserves existing personal tasks
- **Query Performance**: Indexes on foreign keys enable efficient lookups
- **Atomic Operations**: Constraints prevent invalid states (e.g., duplicate team memberships)

**Schema Highlights**:
```sql
-- teams table
CREATE TABLE teams (
    id UUID PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

-- team_members table (junction table with role)
CREATE TABLE team_members (
    id UUID PRIMARY KEY,
    team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('owner', 'admin', 'member', 'viewer')),
    joined_at TIMESTAMP NOT NULL,
    UNIQUE(team_id, user_id)
);

-- task_shares table
CREATE TABLE task_shares (
    id UUID PRIMARY KEY,
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    shared_with_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    shared_by_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    permission VARCHAR(10) NOT NULL CHECK (permission IN ('view', 'edit')),
    shared_at TIMESTAMP NOT NULL,
    UNIQUE(task_id, shared_with_user_id)
);

-- Extend tasks table
ALTER TABLE tasks ADD COLUMN team_id UUID REFERENCES teams(id) ON DELETE SET NULL;
CREATE INDEX idx_tasks_team_id ON tasks(team_id);
```

**Alternatives Considered**:
1. **Denormalized Design**: Rejected because it would duplicate team/member data and create consistency issues.
2. **EAV (Entity-Attribute-Value)**: Rejected because it sacrifices type safety and query performance.
3. **JSON Columns for Permissions**: Rejected because it prevents efficient querying and loses referential integrity.

### Decision 5: API Design Pattern

**Decision**: Use RESTful API design with resource-based endpoints, nested routes for sub-resources, and consistent HTTP status codes.

**Rationale**:
- **Standards Compliance**: Follows REST conventions for predictability
- **Intuitive URLs**: Resource hierarchy is clear (e.g., `/api/teams/{id}/members`)
- **HTTP Semantics**: Proper use of GET/POST/PATCH/DELETE methods
- **Consistency**: Aligns with existing API patterns from Spec 001 and 002

**Endpoint Organization**:
```
Teams:
  POST   /api/teams                    # Create team
  GET    /api/teams                    # List user's teams
  GET    /api/teams/{team_id}          # Get team details
  PATCH  /api/teams/{team_id}          # Update team
  DELETE /api/teams/{team_id}          # Delete team

Team Members:
  POST   /api/teams/{team_id}/members           # Invite member
  PATCH  /api/teams/{team_id}/members/{user_id} # Change role
  DELETE /api/teams/{team_id}/members/{user_id} # Remove member
  POST   /api/teams/{team_id}/leave             # Leave team

Tasks (Extended):
  POST   /api/tasks                    # Create task (with optional team_id)
  GET    /api/tasks                    # List accessible tasks
  GET    /api/tasks/{task_id}          # Get task details
  PATCH  /api/tasks/{task_id}          # Update task
  DELETE /api/tasks/{task_id}          # Delete task

Task Sharing:
  POST   /api/tasks/{task_id}/share              # Share task
  DELETE /api/tasks/{task_id}/share/{user_id}    # Revoke share
  GET    /api/tasks/shared-with-me               # List shared tasks
```

**Alternatives Considered**:
1. **GraphQL**: Rejected because it adds complexity and the REST API is sufficient for current needs.
2. **Flat Endpoint Structure**: Rejected because nested routes better express resource relationships.
3. **RPC-Style Endpoints**: Rejected because it doesn't align with existing API patterns.

### Decision 6: Transaction Management

**Decision**: Use database transactions for all operations that modify multiple records (e.g., ownership transfer, team deletion with cascading effects).

**Rationale**:
- **Data Consistency**: Ensures all-or-nothing semantics for multi-step operations
- **Concurrency Safety**: Prevents race conditions in concurrent operations
- **Rollback Support**: Automatic rollback on errors maintains database integrity
- **Constitutional Requirement**: FR-029 mandates transactions for multi-record operations

**Implementation Pattern**:
```python
# SQLModel transaction context
async def delete_team(team_id: UUID, db: Session):
    with db.begin():
        # Delete team (cascades to team_members via foreign key)
        team = db.get(Team, team_id)
        if not team:
            raise HTTPException(status_code=404)

        # Handle team tasks (either delete or transfer to personal)
        tasks = db.query(Task).filter(Task.team_id == team_id).all()
        for task in tasks:
            task.team_id = None  # Convert to personal task

        db.delete(team)
        db.commit()
```

**Alternatives Considered**:
1. **No Transactions**: Rejected because it risks data inconsistency and violates constitutional requirements.
2. **Application-Level Locking**: Rejected because database transactions are more reliable and performant.
3. **Eventual Consistency**: Rejected because strong consistency is required for permission-critical operations.

### Decision 7: Permission Middleware Architecture

**Decision**: Implement permission checks as FastAPI dependency functions that can be composed and reused across endpoints.

**Rationale**:
- **DRY Principle**: Permission logic defined once and reused
- **Declarative Security**: Permissions declared at endpoint level, not buried in business logic
- **Testability**: Dependencies can be mocked for testing
- **FastAPI Native**: Leverages framework's dependency injection system

**Implementation Pattern**:
```python
# Reusable permission dependencies
async def require_team_admin(
    team_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> TeamMember:
    return await require_team_role(team_id, [TeamRole.OWNER, TeamRole.ADMIN], current_user, db)

async def require_team_member(
    team_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> TeamMember:
    return await require_team_role(team_id, [TeamRole.OWNER, TeamRole.ADMIN, TeamRole.MEMBER], current_user, db)

# Usage in endpoint
@router.post("/teams/{team_id}/members")
async def invite_member(
    team_id: UUID,
    request: InviteMemberRequest,
    member: TeamMember = Depends(require_team_admin),  # Permission check
    db: Session = Depends(get_db)
):
    # Business logic here
    pass
```

**Alternatives Considered**:
1. **Decorator-Based Permissions**: Rejected because FastAPI dependencies are more idiomatic and composable.
2. **Middleware-Based Checks**: Rejected because it's harder to make endpoint-specific permission decisions.
3. **Manual Checks in Each Endpoint**: Rejected because it violates DRY and is error-prone.

## Technology Stack Validation

All technology choices align with the constitutional requirements:

| Component | Technology | Constitutional Compliance |
|-----------|-----------|---------------------------|
| Backend Framework | FastAPI | ✓ Required by constitution |
| ORM | SQLModel | ✓ Required by constitution |
| Database | Neon PostgreSQL | ✓ Required by constitution |
| Authentication | JWT (PyJWT) | ✓ Extends Spec 002 auth |
| Frontend | Next.js 16+ | ✓ Required by constitution |
| Testing | pytest, httpx | ✓ Standard Python testing |

## Best Practices Applied

### 1. Security Best Practices
- **Defense in Depth**: Multiple layers of security (JWT validation, permission checks, database constraints)
- **Principle of Least Privilege**: Users get minimum permissions needed for their role
- **Fail Secure**: Default deny for all permission checks
- **Audit Trail**: All permission changes logged with timestamps

### 2. Database Best Practices
- **Foreign Key Constraints**: Enforce referential integrity
- **Unique Constraints**: Prevent duplicate memberships and shares
- **Indexes**: Optimize common queries (team_id, user_id lookups)
- **Cascading Deletes**: Automatic cleanup of dependent records
- **Nullable Columns**: Enable backward compatibility (team_id nullable)

### 3. API Best Practices
- **Consistent Error Responses**: Standard error format across all endpoints
- **Proper HTTP Status Codes**: 200/201/204 for success, 400/401/403/404/500 for errors
- **Request Validation**: Pydantic schemas validate all inputs
- **Response Schemas**: Explicit response models for type safety
- **Idempotency**: Safe to retry failed requests

### 4. Testing Best Practices
- **Unit Tests**: Test individual functions in isolation
- **Integration Tests**: Test complete API flows
- **Security Tests**: Attempt unauthorized access patterns
- **Performance Tests**: Verify query performance with large datasets
- **Backward Compatibility Tests**: Ensure existing functionality preserved

## Integration Patterns

### Integration with Existing Specs

**Spec 001 (Backend Core & Data Layer)**:
- Extends Task model with team_id column
- Reuses database connection and SQLModel patterns
- Maintains existing task CRUD operations

**Spec 002 (Authentication & API Security)**:
- Leverages existing JWT authentication middleware
- Extends get_current_user dependency for permission checks
- Reuses User model for team membership

### Frontend Integration Pattern

**Better Auth + Team Context**:
```typescript
// Frontend API client with JWT
async function createTeam(name: string, description?: string) {
  const token = await getAuthToken(); // From Better Auth
  const response = await fetch('/api/teams', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ name, description })
  });
  return response.json();
}
```

## Performance Considerations

### Query Optimization
- **Indexes**: Create indexes on foreign keys (team_id, user_id) for fast lookups
- **Eager Loading**: Use SQLModel relationships to avoid N+1 queries
- **Pagination**: Implement pagination for large team member lists
- **Caching**: Consider caching team membership for frequently accessed teams

### Scalability
- **Connection Pooling**: Neon's built-in pooling handles concurrent requests
- **Stateless Design**: No server-side session state enables horizontal scaling
- **Database Transactions**: Keep transactions short to minimize lock contention

## Risk Mitigation

### Identified Risks and Mitigations

1. **Risk**: Race conditions in concurrent role changes
   - **Mitigation**: Database transactions with proper isolation level

2. **Risk**: Performance degradation with large teams (100+ members)
   - **Mitigation**: Database indexes, pagination, query optimization

3. **Risk**: Accidental data leakage across teams
   - **Mitigation**: Comprehensive permission checks, security tests

4. **Risk**: Breaking existing personal task functionality
   - **Mitigation**: Backward compatibility tests, nullable team_id

5. **Risk**: Complex permission logic leading to bugs
   - **Mitigation**: Centralized permission functions, extensive testing

## Conclusion

All architectural decisions align with constitutional principles and leverage the existing technology stack. The design prioritizes security, maintainability, and backward compatibility while enabling flexible multi-user collaboration. No additional research or clarification is needed to proceed with implementation.

**Status**: Research complete. Ready for Phase 1 (Design & Contracts).
