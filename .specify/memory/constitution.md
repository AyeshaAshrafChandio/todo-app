<!--
SYNC IMPACT REPORT
==================
Version Change: NEW → 1.0.0
Rationale: Initial constitution for Todo Full-Stack Web Application (Phase-2 Hackathon)

Modified Principles: N/A (new constitution)
Added Sections:
  - Core Principles (5 principles)
  - Key Standards (API, Authentication, Data, Frontend, Spec Quality)
  - Technology Stack & Constraints
  - Functional Scope
  - Success Criteria
  - Governance

Removed Sections: N/A

Templates Requiring Updates:
  ✅ .specify/templates/spec-template.md - Reviewed, aligns with spec quality standards
  ✅ .specify/templates/plan-template.md - Reviewed, constitution check section compatible
  ✅ .specify/templates/tasks-template.md - Reviewed, aligns with agentic workflow

Follow-up TODOs: None
-->

# Todo Full-Stack Web Application Constitution

**Project**: Todo Full-Stack Web Application (Phase-2 Hackathon)

**Objective**: Transform an in-memory console Todo app into a production-grade, multi-user full-stack web application using a strictly spec-driven, agentic development workflow with no manual coding.

## Core Principles

### I. Spec-Driven Development

All implementation MUST strictly follow approved specifications. No behavior may be implemented outside written specifications.

**Rationale**: Ensures predictability, auditability, and alignment between requirements and implementation. Prevents scope creep and undocumented features.

**Rules**:
- Every feature MUST have a complete specification before implementation begins
- Specifications MUST be approved before moving to planning phase
- Implementation MUST NOT deviate from approved specs
- Any required changes MUST go through spec amendment process

### II. Agentic Workflow Integrity

Development workflow MUST follow the strict sequence: Write spec → Generate plan → Break into tasks → Implement via Claude Code. No manual edits, patches, or human-written code are permitted.

**Rationale**: Maintains consistency, reproducibility, and full auditability of the development process. Ensures AI-driven development quality standards.

**Rules**:
- Workflow steps MUST be executed in order (no skipping)
- No manual code modifications outside the agentic workflow
- All code MUST be generated through Claude Code agents
- Specialized agents MUST be used for their respective domains:
  - `secure-auth-agent` for authentication features
  - `nextjs-ui-builder` for frontend development
  - `neon-db-architect` for database operations
  - `fastapi-backend` for backend API development

### III. Correctness & Consistency

Backend, frontend, and authentication logic MUST align perfectly. API behavior MUST be deterministic and predictable across all layers.

**Rationale**: Prevents integration issues, data inconsistencies, and unpredictable system behavior. Ensures reliable user experience.

**Rules**:
- Data models MUST be consistent across frontend and backend
- API contracts MUST be explicitly defined and followed
- Error handling MUST be consistent across all layers
- State management MUST maintain data integrity
- All components MUST use shared type definitions where applicable

### IV. Security by Design

Authentication and authorization MUST be enforced at every layer. No data leakage across users is permitted.

**Rationale**: Protects user data, prevents unauthorized access, and ensures compliance with security best practices.

**Rules**:
- All API endpoints (except public auth endpoints) MUST require valid JWT tokens
- JWT tokens MUST be verified on every backend request
- User data MUST be filtered by authenticated user ID
- Unauthorized requests MUST return 401 Unauthorized status
- Cross-user data access MUST be prevented at the database query level
- Secrets MUST be stored in `.env` files (never hardcoded)
- Token expiration and refresh MUST be handled properly

### V. Separation of Concerns

Clear boundaries MUST exist between frontend, backend, database, and authentication layers. Backend architecture MUST be stateless.

**Rationale**: Enables independent development, testing, and scaling of each layer. Reduces coupling and improves maintainability.

**Rules**:
- Frontend MUST communicate with backend only through defined REST APIs
- Backend MUST NOT contain frontend-specific logic
- Database access MUST be abstracted through ORM (SQLModel)
- Authentication logic MUST be centralized and reusable
- Business logic MUST reside in backend services, not in API routes
- Backend MUST NOT maintain session state (stateless JWT-based auth)

## Key Standards

### API Standards

**RESTful Design**:
- Resources MUST be noun-based (e.g., `/api/tasks`, not `/api/getTasks`)
- HTTP methods MUST follow REST semantics (GET, POST, PUT, DELETE)
- Endpoints MUST be versioned if breaking changes are anticipated

**HTTP Status Codes**:
- 200 OK: Successful GET, PUT, or PATCH
- 201 Created: Successful POST creating new resource
- 204 No Content: Successful DELETE
- 400 Bad Request: Invalid request data
- 401 Unauthorized: Missing or invalid authentication
- 403 Forbidden: Valid auth but insufficient permissions
- 404 Not Found: Resource does not exist
- 500 Internal Server Error: Unexpected server error

**JSON Consistency**:
- All requests and responses MUST use JSON format
- Field names MUST use camelCase in frontend, snake_case in backend
- Error responses MUST follow consistent structure: `{"error": "message", "detail": "optional details"}`
- Timestamps MUST use ISO 8601 format

### Authentication Standards

**JWT-Based Stateless Authentication**:
- Better Auth MUST be configured to issue JWT tokens on login
- JWT tokens MUST include: user ID, email, expiration time
- Shared secret (`BETTER_AUTH_SECRET`) MUST be consistent across frontend and backend
- Token verification MUST happen on every protected backend request

**Token Flow**:
1. User logs in on frontend → Better Auth creates session and issues JWT token
2. Frontend stores token securely (httpOnly cookie or secure storage)
3. Frontend includes token in `Authorization: Bearer <token>` header for API calls
4. Backend extracts token, verifies signature using shared secret
5. Backend decodes token to get user ID and matches with request context
6. Backend filters all data queries by authenticated user ID

**Security Requirements**:
- Tokens MUST have reasonable expiration times (e.g., 1 hour for access tokens)
- Refresh token mechanism MUST be implemented for session continuity
- Password hashing MUST use industry-standard algorithms (bcrypt, argon2)
- Failed login attempts SHOULD be rate-limited

### Data Standards

**Persistent Storage**:
- All data MUST be stored in Neon Serverless PostgreSQL
- No in-memory or file-based storage for production data
- Database connection MUST use connection pooling for serverless environments

**ORM Usage**:
- SQLModel MUST be used for all database operations
- Raw SQL queries SHOULD be avoided unless necessary for performance
- Database migrations MUST be version-controlled and reproducible

**User Data Isolation**:
- All task queries MUST filter by authenticated user ID
- Database schema MUST enforce foreign key relationships (tasks → users)
- Queries MUST use parameterized statements to prevent SQL injection

### Frontend Standards

**Next.js 16+ App Router**:
- MUST use App Router (not Pages Router)
- Server Components SHOULD be used by default
- Client Components MUST be explicitly marked with `'use client'`
- File-based routing MUST follow Next.js conventions

**Responsive Design**:
- Mobile-first approach MUST be followed
- UI MUST be responsive across mobile, tablet, and desktop
- Touch targets MUST be appropriately sized for mobile devices

**Auth-Aware Routing**:
- Protected pages MUST redirect unauthenticated users to login
- Authentication state MUST be managed consistently
- Token refresh MUST happen transparently to the user

### Spec Quality Standards

All specifications MUST be:

**Unambiguous**:
- Requirements MUST be clear and have single interpretation
- Vague terms like "should work well" are NOT acceptable
- Use MUST/SHOULD/MAY keywords per RFC 2119

**Testable**:
- Every requirement MUST have verifiable acceptance criteria
- Success criteria MUST be measurable
- Edge cases MUST be explicitly documented

**Implementation-Ready**:
- Sufficient detail for agents to implement without clarification
- API contracts MUST be fully specified (endpoints, methods, request/response formats)
- Data models MUST include all required fields and relationships

**Free of Assumptions**:
- No implicit requirements or "obvious" behaviors
- All dependencies MUST be explicitly stated
- Technology choices MUST be justified

## Technology Stack & Constraints

### Fixed Technology Stack

| Layer | Technology | Version | Rationale |
|-------|-----------|---------|-----------|
| Frontend | Next.js | 16+ (App Router) | Modern React framework with SSR, optimal for web apps |
| Backend | Python FastAPI | Latest stable | High-performance async API framework |
| ORM | SQLModel | Latest stable | Type-safe ORM combining SQLAlchemy + Pydantic |
| Database | Neon Serverless PostgreSQL | Latest | Serverless PostgreSQL with auto-scaling |
| Authentication | Better Auth | Latest | Modern auth library with JWT support |
| Spec-Driven | Claude Code + Spec-Kit Plus | Latest | Agentic development workflow tools |

**NON-NEGOTIABLE**: This stack MUST NOT be changed without constitutional amendment.

### Process Constraints

**No Manual Coding**:
- All code MUST be generated through Claude Code agents
- Manual edits for bug fixes are NOT permitted
- Code changes MUST go through spec → plan → tasks → implement workflow

**No Deviation from Specs**:
- Implementation MUST match approved specifications exactly
- "Improvements" or "enhancements" outside spec are NOT permitted
- Changes require spec amendment and re-approval

**No Skipping Steps**:
- Workflow phases MUST be completed in order
- Planning MUST NOT begin before spec approval
- Implementation MUST NOT begin before tasks are defined
- Each phase MUST produce required artifacts

### Security Constraints

**API Protection**:
- All API endpoints MUST require valid JWT (except public auth endpoints: signup, signin)
- Unauthorized requests MUST return 401 Unauthorized
- Malformed tokens MUST be rejected with clear error messages

**User Data Isolation**:
- Task ownership MUST be enforced on every CRUD operation
- Users MUST NOT be able to access other users' tasks
- Database queries MUST include user ID filter
- API responses MUST only contain data belonging to authenticated user

**Secret Management**:
- Secrets MUST be stored in `.env` files
- `.env` files MUST be in `.gitignore`
- Environment variables MUST be documented in `.env.example`
- Production secrets MUST be managed through secure deployment platform

## Functional Scope

### Core Features (Basic Level)

The application MUST implement these 5 features:

1. **User Authentication**
   - User signup with email and password
   - User signin with email and password
   - JWT token generation and management
   - Secure password hashing

2. **Todo CRUD Operations**
   - Create new tasks
   - Read/list user's tasks
   - Update task details
   - Delete tasks
   - Toggle task completion status

3. **User Isolation**
   - Each user sees only their own tasks
   - Cross-user data access prevented
   - User ID enforcement at database level

4. **Persistent Storage**
   - All data stored in Neon PostgreSQL
   - Data survives application restarts
   - Database schema with proper relationships

5. **Responsive UI**
   - Modern, clean interface
   - Mobile-friendly design
   - Intuitive user experience
   - Loading states and error handling

### Out of Scope

The following are explicitly OUT OF SCOPE for Phase 2:
- Task sharing between users
- Task categories or tags
- Task due dates or reminders
- Email notifications
- Social features
- Advanced search or filtering
- Task attachments
- Collaborative editing
- Third-party integrations

## Success Criteria

### Implementation Success

- [ ] All specs are fully implemented without manual code
- [ ] All 5 core features are functional
- [ ] Backend only returns data belonging to authenticated user
- [ ] JWT authentication works end-to-end (frontend ↔ backend)
- [ ] Frontend successfully consumes secured APIs
- [ ] API rejects unauthorized or cross-user access attempts

### Quality Success

- [ ] Application is stable and handles errors gracefully
- [ ] Code is reproducible through agentic workflow
- [ ] All components follow separation of concerns
- [ ] Security constraints are enforced at every layer
- [ ] UI is responsive across devices

### Process Success

- [ ] Entire development history is auditable (specs, plans, prompts)
- [ ] No manual code modifications in git history
- [ ] All workflow phases completed in order
- [ ] Prompt History Records (PHRs) created for all major work
- [ ] Architecture Decision Records (ADRs) created for significant decisions

### User Experience Success

- [ ] Users can sign up and sign in successfully
- [ ] Users can perform all CRUD operations on their tasks
- [ ] Users cannot see or access other users' tasks
- [ ] UI provides clear feedback for all actions
- [ ] Error messages are helpful and user-friendly

## Governance

### Constitutional Authority

This constitution supersedes all other development practices, guidelines, and conventions. In case of conflict, constitutional principles take precedence.

### Amendment Process

Constitutional amendments require:
1. Documented rationale for the change
2. Impact analysis on existing specs, plans, and code
3. Version bump following semantic versioning:
   - **MAJOR**: Backward-incompatible changes (e.g., removing principles, changing stack)
   - **MINOR**: New principles or sections added
   - **PATCH**: Clarifications, wording improvements, typo fixes
4. Update to all dependent templates and documentation
5. Explicit approval before implementation continues

### Compliance Review

**All development artifacts MUST verify constitutional compliance**:
- Specs MUST reference relevant constitutional principles
- Plans MUST include "Constitution Check" section
- Tasks MUST align with workflow integrity requirements
- Implementation MUST follow all standards and constraints
- PRs MUST be reviewed for constitutional compliance

### Complexity Justification

Any violation of constitutional principles MUST be:
1. Explicitly documented in the plan's "Complexity Tracking" section
2. Justified with clear rationale
3. Accompanied by explanation of why simpler alternatives were rejected
4. Approved before implementation proceeds

### Enforcement

Constitutional violations discovered during development MUST:
1. Be flagged immediately
2. Block further progress until resolved
3. Be resolved through spec amendment or implementation correction
4. Be documented in project history for learning

**Version**: 1.0.0 | **Ratified**: 2026-01-18 | **Last Amended**: 2026-01-18
