# Implementation Plan: Frontend Full-Stack UI

**Branch**: `004-frontend-fullstack-ui` | **Date**: 2026-02-05 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-frontend-fullstack-ui/spec.md`

## Summary

Build a complete Next.js 16+ frontend application that integrates with existing backend APIs (001, 002, 003) to provide a full-stack task management experience. The frontend will implement authentication using Better Auth with JWT tokens, personal task management (CRUD + toggle), team collaboration with RBAC, and task sharing with permission controls. The application will be responsive, secure, and production-ready, with all permission logic enforced by the backend and reflected in the UI.

**Technical Approach**: Use Next.js App Router with Server Components by default, Client Components for interactivity, Tailwind CSS for styling, and native Fetch API for backend communication. All API requests will include JWT tokens in Authorization headers, with 401/403 errors handled globally. The frontend will trust no permission logic locally - all access decisions are validated by the backend.

## Technical Context

**Language/Version**: TypeScript 5.x with Next.js 16+ (App Router)
**Primary Dependencies**:
- Next.js 16+ (App Router)
- React 19+
- Better Auth (client-side integration)
- Tailwind CSS 3.x
- TypeScript 5.x

**Storage**: N/A (frontend consumes backend APIs)
**Testing**: Jest + React Testing Library (component tests), Playwright (E2E tests)
**Target Platform**: Modern web browsers (Chrome, Firefox, Safari, Edge - latest 2 versions), responsive design (mobile 320px+, tablet, desktop)
**Project Type**: Web frontend (Next.js App Router)
**Performance Goals**:
- Page load: <2 seconds on broadband
- API response handling: <200ms UI feedback
- Time to Interactive (TTI): <3 seconds
- First Contentful Paint (FCP): <1.5 seconds

**Constraints**:
- No client-side permission logic (all enforced by backend)
- JWT tokens must be stored securely (httpOnly cookies preferred)
- All API calls must include Authorization: Bearer <JWT> header
- 401 responses trigger logout + redirect to /login
- 403 responses display access denied message
- No offline support required
- No real-time updates (polling only if needed)

**Scale/Scope**:
- 10+ pages/routes
- 30+ React components
- 5+ API integration points
- Support for 100+ concurrent users
- Mobile-first responsive design

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Spec-Driven Development
- [x] Complete specification exists (spec.md)
- [x] Specification approved and validated (requirements.md checklist passed)
- [x] Implementation will follow approved spec exactly
- [x] No deviations planned

### ✅ Agentic Workflow Integrity
- [x] Using `/sp.plan` command (current step)
- [x] Will use specialized agents:
  - `nextjs-ui-builder` for all frontend UI development
  - `secure-auth-agent` for Better Auth integration
- [x] No manual coding planned
- [x] Workflow sequence: spec → plan → tasks → implement

### ✅ Correctness & Consistency
- [x] Frontend will use backend API contracts exactly as defined
- [x] Data models will match backend schemas (User, Task, Team, TeamMember, TaskShare)
- [x] Error handling will be consistent across all components
- [x] State management will maintain data integrity (no stale data)

### ✅ Security by Design
- [x] All API calls (except public routes) will include JWT tokens
- [x] Frontend will never trust local permission logic
- [x] Backend enforces all access control
- [x] Tokens stored securely (httpOnly cookies or secure localStorage)
- [x] No secrets in frontend code
- [x] User input sanitized before display (XSS prevention)

### ✅ Separation of Concerns
- [x] Frontend communicates with backend only through REST APIs
- [x] No business logic in frontend (only presentation and interaction)
- [x] Authentication handled by Better Auth + backend JWT verification
- [x] Clear component hierarchy (pages → layouts → components → UI primitives)
- [x] API client abstracted in separate module

**Constitution Check Result**: ✅ PASSED - All principles satisfied

## Project Structure

### Documentation (this feature)

```text
specs/004-frontend-fullstack-ui/
├── spec.md              # Feature specification
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (technology decisions)
├── data-model.md        # Phase 1 output (frontend data structures)
├── quickstart.md        # Phase 1 output (setup instructions)
├── contracts/           # Phase 1 output (API contracts)
│   ├── auth-api.md
│   ├── tasks-api.md
│   ├── teams-api.md
│   └── task-shares-api.md
└── checklists/
    └── requirements.md  # Spec validation checklist
```

### Source Code (repository root)

```text
frontend/
├── src/
│   ├── app/                    # Next.js App Router pages
│   │   ├── (auth)/            # Auth layout group
│   │   │   ├── login/
│   │   │   │   └── page.tsx
│   │   │   └── register/
│   │   │       └── page.tsx
│   │   ├── (protected)/       # Protected layout group
│   │   │   ├── dashboard/
│   │   │   │   └── page.tsx
│   │   │   ├── tasks/
│   │   │   │   ├── page.tsx
│   │   │   │   └── [id]/
│   │   │   │       └── page.tsx
│   │   │   ├── teams/
│   │   │   │   ├── page.tsx
│   │   │   │   └── [team_id]/
│   │   │   │       ├── page.tsx
│   │   │   │       └── tasks/
│   │   │   │           └── page.tsx
│   │   │   ├── settings/
│   │   │   │   └── page.tsx
│   │   │   ├── layout.tsx     # Protected layout with auth check
│   │   │   ├── loading.tsx
│   │   │   └── error.tsx
│   │   ├── layout.tsx         # Root layout
│   │   ├── page.tsx           # Landing page (redirects)
│   │   ├── loading.tsx
│   │   ├── not-found.tsx
│   │   └── globals.css
│   ├── components/            # React components
│   │   ├── auth/              # Auth-related components
│   │   │   ├── LoginForm.tsx
│   │   │   ├── RegisterForm.tsx
│   │   │   └── LogoutButton.tsx
│   │   ├── tasks/             # Task components
│   │   │   ├── TaskList.tsx
│   │   │   ├── TaskCard.tsx
│   │   │   ├── TaskForm.tsx
│   │   │   ├── TaskDetail.tsx
│   │   │   └── TaskToggle.tsx
│   │   ├── teams/             # Team components
│   │   │   ├── TeamList.tsx
│   │   │   ├── TeamCard.tsx
│   │   │   ├── TeamForm.tsx
│   │   │   ├── MemberList.tsx
│   │   │   └── RoleBadge.tsx
│   │   ├── shared/            # Shared task components
│   │   │   ├── SharedTaskList.tsx
│   │   │   ├── ShareTaskModal.tsx
│   │   │   └── PermissionBadge.tsx
│   │   ├── ui/                # UI primitives
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── Modal.tsx
│   │   │   ├── Spinner.tsx
│   │   │   ├── Alert.tsx
│   │   │   └── EmptyState.tsx
│   │   └── layout/            # Layout components
│   │       ├── Header.tsx
│   │       ├── Sidebar.tsx
│   │       ├── Navigation.tsx
│   │       └── Footer.tsx
│   ├── lib/                   # Utilities and helpers
│   │   ├── api/               # API client
│   │   │   ├── client.ts      # Base API client with JWT handling
│   │   │   ├── auth.ts        # Auth API calls
│   │   │   ├── tasks.ts       # Tasks API calls
│   │   │   ├── teams.ts       # Teams API calls
│   │   │   └── shares.ts      # Task shares API calls
│   │   ├── auth/              # Auth utilities
│   │   │   ├── session.ts     # Session management
│   │   │   ├── token.ts       # Token storage/retrieval
│   │   │   └── middleware.ts  # Auth middleware
│   │   ├── utils/             # General utilities
│   │   │   ├── format.ts      # Date/string formatting
│   │   │   ├── validation.ts  # Input validation
│   │   │   └── errors.ts      # Error handling
│   │   └── types/             # TypeScript types
│   │       ├── api.ts         # API response types
│   │       ├── models.ts      # Data model types
│   │       └── auth.ts        # Auth types
│   └── hooks/                 # Custom React hooks
│       ├── useAuth.ts         # Auth state hook
│       ├── useTasks.ts        # Tasks data hook
│       ├── useTeams.ts        # Teams data hook
│       └── useShares.ts       # Shared tasks hook
├── public/                    # Static assets
│   ├── favicon.ico
│   └── images/
├── .env.local.example         # Environment variables template
├── .eslintrc.json            # ESLint configuration
├── .gitignore
├── next.config.js            # Next.js configuration
├── package.json
├── postcss.config.js         # PostCSS configuration
├── tailwind.config.js        # Tailwind CSS configuration
├── tsconfig.json             # TypeScript configuration
└── README.md
```

**Structure Decision**: Web application structure using Next.js App Router. The `frontend/` directory contains all frontend code, organized by Next.js conventions with App Router. Route groups `(auth)` and `(protected)` separate public and authenticated pages. Components are organized by feature (auth, tasks, teams, shared) with a shared `ui/` directory for primitives. API client is abstracted in `lib/api/` with separate modules per resource. Custom hooks in `hooks/` manage data fetching and state.

## Complexity Tracking

> **No violations - this section is empty**

All constitutional principles are satisfied without exceptions. The frontend architecture follows separation of concerns, uses the approved tech stack, and implements security by design with backend-enforced permissions.

## Phase 0: Research & Technology Decisions

**Objective**: Resolve all technical unknowns and establish implementation patterns.

### Research Tasks

1. **Better Auth Client Integration**
   - Research: How to integrate Better Auth client-side with Next.js App Router
   - Research: JWT token storage best practices (httpOnly cookies vs localStorage)
   - Research: Token refresh patterns in Next.js
   - Output: Authentication strategy and implementation pattern

2. **Next.js App Router Patterns**
   - Research: Server Components vs Client Components usage patterns
   - Research: Route groups for auth vs protected pages
   - Research: Middleware for route protection
   - Research: Loading and error boundaries
   - Output: Component architecture and routing strategy

3. **API Client Architecture**
   - Research: Fetch API patterns with JWT token injection
   - Research: Global error handling (401/403)
   - Research: Request/response interceptors
   - Research: Type-safe API client patterns
   - Output: API client implementation pattern

4. **State Management**
   - Research: When to use Server Components vs Client Components
   - Research: Data fetching patterns (server-side vs client-side)
   - Research: Optimistic updates for better UX
   - Research: Cache invalidation strategies
   - Output: State management strategy

5. **Responsive Design Patterns**
   - Research: Tailwind CSS responsive utilities
   - Research: Mobile-first design patterns
   - Research: Touch-friendly UI components
   - Output: Responsive design guidelines

**Output**: `research.md` with all decisions documented

## Phase 1: Design & Contracts

**Prerequisites**: `research.md` complete

### 1. Data Model (`data-model.md`)

Define frontend TypeScript types matching backend schemas:

**Core Entities**:
- `User`: { id, email, created_at }
- `Task`: { id, title, description, completed, user_id, team_id?, created_at, updated_at }
- `Team`: { id, name, created_at }
- `TeamMember`: { id, team_id, user_id, role, joined_at }
- `TaskShare`: { id, task_id, shared_with_user_id, permission, shared_at }

**API Response Types**:
- `AuthResponse`: { token, user }
- `TaskResponse`: Task with optional owner/team info
- `TeamResponse`: Team with member count
- `ErrorResponse`: { error, detail? }

**UI State Types**:
- `LoadingState`: 'idle' | 'loading' | 'success' | 'error'
- `PermissionLevel`: 'view' | 'edit'
- `TeamRole`: 'owner' | 'admin' | 'member' | 'viewer'

### 2. API Contracts (`contracts/`)

Document all backend API endpoints the frontend will consume:

**`contracts/auth-api.md`**:
- POST /api/auth/signup
- POST /api/auth/signin
- POST /api/auth/signout
- GET /api/auth/session

**`contracts/tasks-api.md`**:
- GET /api/users/{user_id}/tasks
- POST /api/users/{user_id}/tasks
- GET /api/users/{user_id}/tasks/{task_id}
- PUT /api/users/{user_id}/tasks/{task_id}
- DELETE /api/users/{user_id}/tasks/{task_id}
- PATCH /api/users/{user_id}/tasks/{task_id}/toggle

**`contracts/teams-api.md`**:
- GET /api/teams
- POST /api/teams
- GET /api/teams/{team_id}
- GET /api/teams/{team_id}/members
- POST /api/teams/{team_id}/members
- GET /api/teams/{team_id}/tasks

**`contracts/task-shares-api.md`**:
- GET /api/task-shares
- POST /api/task-shares
- DELETE /api/task-shares/{share_id}

### 3. Quickstart Guide (`quickstart.md`)

Setup instructions for developers:
- Prerequisites (Node.js 18+, npm/yarn)
- Environment variables setup (.env.local)
- Installation steps (npm install)
- Development server (npm run dev)
- Build and deployment (npm run build)
- Testing (npm test)

### 4. Agent Context Update

Run: `.specify/scripts/powershell/update-agent-context.ps1 -AgentType claude`

Add to agent context:
- Next.js 16+ App Router patterns
- Better Auth client integration
- Tailwind CSS responsive utilities
- TypeScript type definitions
- API client patterns

**Outputs**:
- `data-model.md`
- `contracts/auth-api.md`
- `contracts/tasks-api.md`
- `contracts/teams-api.md`
- `contracts/task-shares-api.md`
- `quickstart.md`
- Updated agent context file

## Phase 2: Task Breakdown (Separate Command)

**Note**: Task breakdown is handled by the `/sp.tasks` command, NOT by `/sp.plan`.

The `/sp.tasks` command will generate `tasks.md` with detailed implementation tasks organized by phase:

**Expected Task Structure**:
1. **Phase 1: Project Setup** (T001-T005)
2. **Phase 2: Authentication** (T006-T011)
3. **Phase 3: Personal Tasks** (T012-T018)
4. **Phase 4: Teams** (T019-T023)
5. **Phase 5: Team Tasks & Sharing** (T024-T028)
6. **Phase 6: Security & Validation** (T029-T032)
7. **Phase 7: Polish & Finalization** (T033-T036)

## Implementation Strategy

### Phased Rollout

**Phase 1: Foundation** (T001-T005)
- Initialize Next.js project with App Router
- Configure Tailwind CSS
- Setup environment variables and API client
- Implement route protection middleware
- **Deliverable**: Empty Next.js app with routing structure

**Phase 2: Authentication** (T006-T011)
- Integrate Better Auth client-side
- Build signup and login pages
- Implement logout flow
- Setup auth state management
- **Deliverable**: Working authentication flow

**Phase 3: Personal Tasks** (T012-T018)
- Build task list page
- Implement create task form
- Build task detail page with edit
- Add delete and toggle functionality
- Implement loading and error states
- **Deliverable**: Full personal task management

**Phase 4: Teams** (T019-T023)
- Build team list page
- Implement create team form
- Build team detail page with member list
- Display roles and implement role-based UI controls
- **Deliverable**: Team management UI

**Phase 5: Team Tasks & Sharing** (T024-T028)
- Build team task list page
- Implement create team task
- Add shared task indicators
- Implement permission-based action controls
- Build task sharing UI
- **Deliverable**: Collaborative features complete

**Phase 6: Security & Validation** (T029-T032)
- Enforce protected routes globally
- Implement global 401/403 error handling
- Prevent cross-team data access in UI
- Validate all user flows end-to-end
- **Deliverable**: Secure, validated application

**Phase 7: Polish & Finalization** (T033-T036)
- Validate responsive design across devices
- Implement accessibility basics (semantic HTML, ARIA labels)
- Add empty states and edge case handling
- Update documentation
- **Deliverable**: Production-ready frontend

### Testing Strategy

**Component Testing** (Jest + React Testing Library):
- Unit tests for UI components
- Integration tests for forms and interactions
- Mock API responses for isolated testing

**End-to-End Testing** (Playwright):
- Full user flows (signup → login → create task → logout)
- Cross-browser testing (Chrome, Firefox, Safari)
- Responsive design validation

**Manual Testing**:
- Security validation (unauthorized access attempts)
- Permission enforcement (role-based actions)
- Error handling (network failures, invalid inputs)
- Edge cases (empty states, long text, concurrent edits)

### Deployment Considerations

**Environment Variables**:
- `NEXT_PUBLIC_API_URL`: Backend API base URL
- `NEXT_PUBLIC_BETTER_AUTH_URL`: Better Auth endpoint
- `BETTER_AUTH_SECRET`: Shared secret for JWT verification (server-side only)

**Build Optimization**:
- Server Components for static content
- Client Components only where interactivity needed
- Image optimization with Next.js Image component
- Code splitting by route

**Production Checklist**:
- [ ] Environment variables configured
- [ ] API endpoints verified
- [ ] CORS configured on backend
- [ ] Error tracking setup (optional)
- [ ] Performance monitoring (optional)
- [ ] SSL/HTTPS enabled
- [ ] Security headers configured

## Risk Analysis

### High-Priority Risks

1. **JWT Token Management**
   - **Risk**: Token expiration during active session
   - **Mitigation**: Implement token refresh mechanism, handle 401 gracefully
   - **Fallback**: Clear session and redirect to login

2. **API Integration Mismatches**
   - **Risk**: Frontend expects different API contract than backend provides
   - **Mitigation**: Use contracts/ documentation, validate responses
   - **Fallback**: Add response validation layer in API client

3. **Permission Enforcement**
   - **Risk**: UI shows actions user cannot perform
   - **Mitigation**: Backend enforces all permissions, UI reflects backend responses
   - **Fallback**: Handle 403 errors gracefully with clear messages

4. **Responsive Design Complexity**
   - **Risk**: UI breaks on mobile devices
   - **Mitigation**: Mobile-first design, test on real devices
   - **Fallback**: Provide desktop-only warning if mobile support fails

### Medium-Priority Risks

5. **State Synchronization**
   - **Risk**: Stale data after updates
   - **Mitigation**: Refetch data after mutations, use optimistic updates
   - **Fallback**: Add manual refresh button

6. **Error Handling Gaps**
   - **Risk**: Unhandled errors crash the app
   - **Mitigation**: Global error boundaries, comprehensive error handling
   - **Fallback**: Generic error page with retry option

7. **Performance Issues**
   - **Risk**: Slow page loads or API calls
   - **Mitigation**: Use Server Components, implement loading states
   - **Fallback**: Add loading indicators, optimize bundle size

## Success Metrics

### Functional Completeness
- [ ] All 52 functional requirements from spec.md implemented
- [ ] All 6 user stories testable and working
- [ ] All 10 edge cases handled

### Quality Metrics
- [ ] All pages load in <2 seconds
- [ ] 95%+ API calls succeed without errors
- [ ] Zero unauthorized data access in testing
- [ ] Responsive design works on 320px+ screens

### Security Metrics
- [ ] All API calls include JWT tokens
- [ ] 401 errors trigger logout
- [ ] 403 errors display access denied
- [ ] No client-side permission logic

### User Experience Metrics
- [ ] Users can complete signup in <60 seconds
- [ ] Users can create task in <15 seconds
- [ ] Clear feedback for all actions
- [ ] Helpful error messages

## Next Steps

1. **Complete Phase 0**: Generate `research.md` with all technology decisions
2. **Complete Phase 1**: Generate data models, API contracts, and quickstart guide
3. **Run `/sp.tasks`**: Generate detailed task breakdown in `tasks.md`
4. **Run `/sp.implement`**: Execute tasks using specialized agents (nextjs-ui-builder, secure-auth-agent)
5. **Testing & Validation**: Verify all requirements and success criteria
6. **Documentation**: Update README and create deployment guide

## Architectural Decision Records (ADRs)

**Significant Decisions Requiring ADRs**:

1. **Next.js App Router vs Pages Router**
   - Decision: Use App Router
   - Rationale: Modern pattern, better performance, Server Components support
   - Impact: All routing and layouts follow App Router conventions

2. **JWT Token Storage Strategy**
   - Decision: httpOnly cookies (preferred) or secure localStorage
   - Rationale: httpOnly cookies prevent XSS attacks
   - Impact: Token management implementation, CSRF protection needed

3. **State Management Approach**
   - Decision: No external state library (use Server Components + React state)
   - Rationale: Simplicity, leverage Next.js patterns, avoid complexity
   - Impact: Data fetching patterns, component architecture

4. **API Client Architecture**
   - Decision: Custom Fetch wrapper with JWT injection
   - Rationale: Full control, type safety, no external dependencies
   - Impact: All API calls go through centralized client

**Recommendation**: Run `/sp.adr` for each decision after plan approval to document rationale and tradeoffs.

---

**Plan Status**: ✅ COMPLETE - Ready for Phase 0 (Research) and Phase 1 (Design)

**Next Command**: Continue with research and design phases within this `/sp.plan` execution, then run `/sp.tasks` to generate task breakdown.
