# Quickstart Guide: Teams, RBAC, and Task Sharing

**Feature**: 003-teams-rbac-sharing
**Date**: 2026-02-04
**Audience**: Developers implementing this feature

## Overview

This guide provides a quick reference for implementing multi-user collaboration with team-based task management, role-based access control (RBAC), and direct task sharing. Follow this guide after reading the full specification, research, and data model documents.

## Prerequisites

Before starting implementation:

1. **Completed Specs**:
   - ✅ Spec 001 (Backend Core & Data Layer) - provides Task model and database infrastructure
   - ✅ Spec 002 (Authentication & API Security) - provides User model and JWT authentication

2. **Environment Setup**:
   - Python 3.11+ installed
   - Neon PostgreSQL database configured
   - FastAPI backend running
   - Next.js 16+ frontend setup
   - Better Auth configured with JWT

3. **Required Dependencies** (already installed from Spec 002):
   - FastAPI, SQLModel, psycopg[binary]
   - PyJWT, bcrypt
   - pydantic, python-dotenv

## Implementation Sequence

### Phase 1: Database Schema (neon-db-architect agent)

**Priority**: P1 - Foundation for all other work

**Tasks**:
1. Create `teams` table with proper constraints
2. Create `team_members` table with role enum and unique constraint
3. Create `task_shares` table with permission enum and unique constraint
4. Extend `tasks` table with nullable `team_id` column
5. Create all required indexes for performance
6. Write migration scripts (forward and rollback)
7. Test migrations on development database

**Key Files**:
- `backend/app/models/team.py` (NEW)
- `backend/app/models/team_member.py` (NEW)
- `backend/app/models/task_share.py` (NEW)
- `backend/app/models/task.py` (EXTEND - add team_id)
- `backend/migrations/003_add_teams_rbac_sharing.py` (NEW)

**Validation**:
- All tables created successfully
- Foreign keys enforce referential integrity
- Unique constraints prevent duplicate memberships/shares
- Indexes exist on all foreign keys
- Backward compatibility: existing tasks still work

---

### Phase 2: Pydantic Schemas (fastapi-backend agent)

**Priority**: P1 - Required for API validation

**Tasks**:
1. Create team request/response schemas
2. Create team member request/response schemas
3. Create task share request/response schemas
4. Extend task schemas to include team_id and access_type
5. Define enum types for roles and permissions

**Key Files**:
- `backend/app/schemas/team.py` (NEW)
- `backend/app/schemas/team_member.py` (NEW)
- `backend/app/schemas/task_share.py` (NEW)
- `backend/app/schemas/task.py` (EXTEND)

**Example Schema**:
```python
# backend/app/schemas/team.py
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional

class TeamCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)

class TeamResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    owner_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

---

### Phase 3: Permission Middleware (secure-auth-agent agent)

**Priority**: P1 - Security foundation

**Tasks**:
1. Create permission checking functions using FastAPI dependencies
2. Implement role-based access control logic
3. Create reusable permission dependencies (require_team_admin, require_team_member, etc.)
4. Implement task access checking (owner, team, share)
5. Add comprehensive error handling with proper HTTP status codes

**Key Files**:
- `backend/app/middleware/permissions.py` (NEW)
- `backend/app/middleware/auth.py` (EXTEND - add team permission checks)

**Example Permission Dependency**:
```python
# backend/app/middleware/permissions.py
from fastapi import Depends, HTTPException
from uuid import UUID
from app.middleware.auth import get_current_user
from app.models.user import User
from app.models.team_member import TeamMember, TeamRole

async def require_team_role(
    team_id: UUID,
    required_roles: List[TeamRole],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> TeamMember:
    member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == current_user.id
    ).first()

    if not member or member.role not in required_roles:
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions for this operation"
        )

    return member

async def require_team_admin(
    team_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> TeamMember:
    return await require_team_role(
        team_id,
        [TeamRole.OWNER, TeamRole.ADMIN],
        current_user,
        db
    )
```

---

### Phase 4: Service Layer (fastapi-backend agent)

**Priority**: P1 - Business logic

**Tasks**:
1. Create team service with CRUD operations
2. Create team member service with role management
3. Create task share service with permission handling
4. Extend task service to support team context
5. Implement transaction management for multi-record operations
6. Add comprehensive error handling

**Key Files**:
- `backend/app/services/team_service.py` (NEW)
- `backend/app/services/team_member_service.py` (NEW)
- `backend/app/services/task_share_service.py` (NEW)
- `backend/app/services/task_service.py` (EXTEND)

**Example Service Function**:
```python
# backend/app/services/team_service.py
from sqlmodel import Session, select
from uuid import UUID
from app.models.team import Team
from app.models.team_member import TeamMember, TeamRole

def create_team(
    db: Session,
    name: str,
    description: Optional[str],
    owner_id: UUID
) -> Team:
    with db.begin():
        # Create team
        team = Team(
            name=name,
            description=description,
            owner_id=owner_id
        )
        db.add(team)
        db.flush()  # Get team.id

        # Add owner as team member
        member = TeamMember(
            team_id=team.id,
            user_id=owner_id,
            role=TeamRole.OWNER
        )
        db.add(member)
        db.commit()
        db.refresh(team)

    return team
```

---

### Phase 5: API Routes (fastapi-backend agent)

**Priority**: P1 - API endpoints

**Tasks**:
1. Create team routes (5 endpoints)
2. Create team member routes (4 endpoints)
3. Create task share routes (3 endpoints)
4. Extend task routes to support team_id and filtering (5 endpoints)
5. Wire up permission dependencies to each endpoint
6. Register all routes in main.py

**Key Files**:
- `backend/app/routes/teams.py` (NEW)
- `backend/app/routes/team_members.py` (NEW)
- `backend/app/routes/task_shares.py` (NEW)
- `backend/app/routes/tasks.py` (EXTEND)
- `backend/app/main.py` (EXTEND - register new routes)

**Example Route**:
```python
# backend/app/routes/teams.py
from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from app.schemas.team import TeamCreate, TeamResponse
from app.services.team_service import create_team
from app.middleware.auth import get_current_user

router = APIRouter(prefix="/api/teams", tags=["Teams"])

@router.post("/", response_model=TeamResponse, status_code=201)
async def create_team_endpoint(
    request: TeamCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        team = create_team(
            db=db,
            name=request.name,
            description=request.description,
            owner_id=current_user.id
        )
        return team
    except IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Team name already exists"
        )
```

---

### Phase 6: Backend Testing (fastapi-backend agent)

**Priority**: P1 - Quality assurance

**Tasks**:
1. Write unit tests for all service functions
2. Write integration tests for all API endpoints
3. Write security tests (unauthorized access attempts)
4. Write permission tests (role-based access control)
5. Write backward compatibility tests (existing personal tasks)
6. Write performance tests (large teams, many shares)

**Key Files**:
- `backend/tests/test_team_model.py` (NEW)
- `backend/tests/test_team_member_model.py` (NEW)
- `backend/tests/test_task_share_model.py` (NEW)
- `backend/tests/test_team_api.py` (NEW)
- `backend/tests/test_team_member_api.py` (NEW)
- `backend/tests/test_task_share_api.py` (NEW)
- `backend/tests/test_permissions.py` (NEW)
- `backend/tests/test_backward_compatibility.py` (NEW)

**Test Coverage Goals**:
- Unit tests: 90%+ coverage
- Integration tests: All happy paths + error cases
- Security tests: All unauthorized access patterns blocked
- Performance tests: <500ms p95 latency

---

### Phase 7: Frontend Components (nextjs-ui-builder agent)

**Priority**: P2 - User interface

**Tasks**:
1. Create team management pages (list, detail, create, edit)
2. Create team member management components
3. Create task sharing modal/dialog
4. Extend task components to show team context
5. Create shared tasks view
6. Implement role-based UI (hide actions based on permissions)

**Key Files**:
- `frontend/src/app/(protected)/teams/page.tsx` (NEW)
- `frontend/src/app/(protected)/teams/[teamId]/page.tsx` (NEW)
- `frontend/src/components/teams/TeamCard.tsx` (NEW)
- `frontend/src/components/teams/TeamList.tsx` (NEW)
- `frontend/src/components/teams/MemberList.tsx` (NEW)
- `frontend/src/components/shared/ShareTaskModal.tsx` (NEW)
- `frontend/src/lib/api/teams.ts` (NEW)
- `frontend/src/lib/types/team.ts` (NEW)

---

### Phase 8: Frontend Integration (nextjs-ui-builder agent)

**Priority**: P2 - Connect UI to API

**Tasks**:
1. Create API client functions for all team endpoints
2. Create API client functions for task sharing
3. Extend task API client to support team_id
4. Implement error handling and loading states
5. Add optimistic updates for better UX
6. Implement JWT token refresh

**Key Files**:
- `frontend/src/lib/api/teams.ts` (NEW)
- `frontend/src/lib/api/shares.ts` (NEW)
- `frontend/src/lib/api/tasks.ts` (EXTEND)
- `frontend/src/hooks/useTeams.ts` (NEW)
- `frontend/src/hooks/useShares.ts` (NEW)

---

## Quick Reference

### Role Permissions Matrix

| Action | Owner | Admin | Member | Viewer |
|--------|-------|-------|--------|--------|
| Create team | ✓ | ✗ | ✗ | ✗ |
| Delete team | ✓ | ✗ | ✗ | ✗ |
| Edit team settings | ✓ | ✓ | ✗ | ✗ |
| Invite members | ✓ | ✓ | ✗ | ✗ |
| Remove members | ✓ | ✓ | ✗ | ✗ |
| Change roles | ✓ (all) | ✓ (member/viewer) | ✗ | ✗ |
| Create team tasks | ✓ | ✓ | ✓ | ✗ |
| Edit own tasks | ✓ | ✓ | ✓ | ✗ |
| Edit others' tasks | ✓ | ✓ | ✗ | ✗ |
| Delete tasks | ✓ | ✓ | ✗ (own only) | ✗ |
| View team tasks | ✓ | ✓ | ✓ | ✓ |

### Share Permissions

| Permission | View | Edit | Delete |
|------------|------|------|--------|
| **view** | ✓ | ✗ | ✗ |
| **edit** | ✓ | ✓ | ✗ |
| **owner** | ✓ | ✓ | ✓ |

### Common Queries

**Get user's teams**:
```python
teams = db.query(Team).join(TeamMember).filter(
    TeamMember.user_id == user_id
).all()
```

**Check team permission**:
```python
member = db.query(TeamMember).filter(
    TeamMember.team_id == team_id,
    TeamMember.user_id == user_id
).first()
has_permission = member and member.role in required_roles
```

**Get accessible tasks**:
```python
# Personal tasks
personal = db.query(Task).filter(Task.user_id == user_id)

# Team tasks
team = db.query(Task).join(TeamMember).filter(
    TeamMember.user_id == user_id
)

# Shared tasks
shared = db.query(Task).join(TaskShare).filter(
    TaskShare.shared_with_user_id == user_id
)

all_tasks = personal.union(team).union(shared).all()
```

## Testing Checklist

Before marking implementation complete:

- [ ] All database migrations run successfully
- [ ] All 18 API endpoints return correct responses
- [ ] Permission checks block unauthorized access (401/403)
- [ ] Role-based permissions enforced correctly
- [ ] Backward compatibility: existing personal tasks work
- [ ] Team creation and membership management works
- [ ] Task sharing works with correct permissions
- [ ] Frontend displays teams and shared tasks
- [ ] All tests pass (unit, integration, security)
- [ ] Performance meets targets (<500ms p95)

## Troubleshooting

**Issue**: "Team name already exists" error
- **Solution**: Team names must be unique. Check existing teams or choose different name.

**Issue**: "Insufficient permissions" error
- **Solution**: Verify user's role in team. Only owners/admins can perform management actions.

**Issue**: Cannot delete team owner
- **Solution**: Transfer ownership first by promoting another member to owner.

**Issue**: Personal tasks not showing after adding team_id
- **Solution**: Ensure team_id is nullable and queries handle NULL correctly.

**Issue**: Shared tasks not accessible
- **Solution**: Verify TaskShare record exists and permission is correct (view/edit).

## Next Steps

After completing implementation:

1. Run `/sp.tasks` to generate detailed task breakdown
2. Execute tasks using specialized agents
3. Create comprehensive test suite
4. Document any architectural decisions as ADRs
5. Create PR with `/sp.git.commit_pr`

## Resources

- **Specification**: `specs/003-teams-rbac-sharing/spec.md`
- **Research**: `specs/003-teams-rbac-sharing/research.md`
- **Data Model**: `specs/003-teams-rbac-sharing/data-model.md`
- **API Contracts**: `specs/003-teams-rbac-sharing/contracts/api-contracts.md`
- **Constitution**: `.specify/memory/constitution.md`

---

**Status**: Quickstart guide complete. Ready for task generation with `/sp.tasks`.
