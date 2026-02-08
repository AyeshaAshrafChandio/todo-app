<!--
SYNC IMPACT REPORT
==================
Version Change: 1.0.0 → 1.1.0
Rationale: Phase III expansion - Adding AI-Powered Todo Chatbot with MCP tools and agent-based reasoning while maintaining full backward compatibility with Phase I & II

Modified Principles:
  - Principle V (Separation of Concerns) - Expanded to include AI agent and MCP tool boundaries

Added Sections:
  - Phase III: AI-Powered Chatbot Principles (6 new principles)
  - AI/Agent Standards (Agent Behavior, MCP Tool Design, Conversation Management)
  - Phase III Technology Stack (OpenAI Agents SDK, MCP SDK, ChatKit)
  - Phase III Functional Scope (Natural language task management, conversation persistence)
  - Spec Boundaries section (multi-spec architecture requirements)

Removed Sections: None (full backward compatibility maintained)

Templates Requiring Updates:
  ✅ .specify/templates/spec-template.md - Reviewed, compatible with multi-spec architecture
  ✅ .specify/templates/plan-template.md - Reviewed, constitution check section compatible
  ✅ .specify/templates/tasks-template.md - Reviewed, aligns with agentic workflow
  ⚠ .specify/templates/commands/*.md - May need review for Phase III agent references

Follow-up TODOs:
  - Review command templates for Phase III-specific agent guidance
  - Consider creating Phase III-specific checklist template for AI/MCP validation
-->

# Todo Full-Stack Web Application Constitution

**Project**: Todo Full-Stack Web Application with AI-Powered Chatbot (Phase I, II & III)

**Objective**: Transform an in-memory console Todo app into a production-grade, multi-user full-stack web application with AI-powered natural language task management, using a strictly spec-driven, agentic development workflow with no manual coding.

**Phase I**: Backend Core & Data Layer (PostgreSQL, FastAPI, SQLModel)
**Phase II**: Frontend Full-Stack UI (Next.js, Authentication, Responsive Design)
**Phase III**: AI-Powered Chatbot (OpenAI Agents SDK, MCP Tools, Natural Language Interface)

## Core Principles (Phase I & II)

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
- User identity MUST be derived ONLY from verified JWT (never from client-supplied user_id)

### V. Separation of Concerns

Clear boundaries MUST exist between frontend, backend, database, authentication, AI agents, and MCP tools. Backend architecture MUST be stateless.

**Rationale**: Enables independent development, testing, and scaling of each layer. Reduces coupling and improves maintainability.

**Rules**:
- Frontend MUST communicate with backend only through defined REST APIs
- Backend MUST NOT contain frontend-specific logic
- Database access MUST be abstracted through ORM (SQLModel)
- Authentication logic MUST be centralized and reusable
- Business logic MUST reside in backend services, not in API routes
- Backend MUST NOT maintain session state (stateless JWT-based auth)
- **Phase III**: Frontend MUST NOT call MCP tools directly
- **Phase III**: AI agents MUST NOT contain business logic
- **Phase III**: MCP tools MUST NOT contain conversational logic

## Phase III: AI-Powered Chatbot Principles

### VI. Stateless Architecture

Backend MUST hold NO in-memory session state. Conversation context MUST be reconstructed from database per request. MCP tools MUST be stateless and idempotent.

**Rationale**: Ensures scalability, reliability, and ability to resume conversations after server restarts. Prevents memory leaks and state corruption.

**Rules**:
- Backend MUST NOT store conversation state in memory
- All conversation history MUST be persisted to database
- Each request MUST reconstruct context from database
- MCP tools MUST be stateless (no instance variables for state)
- MCP tools MUST be idempotent (same input → same output)
- Conversation resume MUST work after server restart

### VII. Agent Behavior Constraints

Agents may only decide *what* to do. Agents may never directly mutate the database. All state changes MUST happen via MCP tools.

**Rationale**: Maintains clear separation between decision-making (agent) and execution (tools). Ensures auditability and testability of all actions.

**Rules**:
- Agents MUST decide actions but NOT execute them directly
- Agents MUST use MCP tools for all database mutations
- Agents MUST confirm actions in natural language to users
- Agents MUST handle errors gracefully with user-friendly responses
- Agents MUST NOT bypass MCP tools to access database directly

### VIII. MCP Tool Design

Tools MUST map 1:1 to domain actions. Tools MUST validate authorization server-side. Tools MUST be stateless and persist all changes to database.

**Rationale**: Ensures tools are reusable, testable, and secure. Prevents unauthorized actions and maintains data integrity.

**Rules**:
- Each MCP tool MUST correspond to exactly one domain action
- Tools MUST validate JWT authorization on every invocation
- Tools MUST be stateless (no instance state)
- Tools MUST persist all changes to database immediately
- Tools MUST return structured, predictable outputs
- Tools MUST validate input parameters thoroughly
- Tools MUST handle errors and return clear error messages

### IX. Frontend-Backend Integration

Frontend MUST communicate ONLY with FastAPI backend. JWT MUST be attached to every request. Frontend MUST NOT infer permissions or call MCP directly.

**Rationale**: Maintains security boundaries and ensures all authorization happens server-side. Prevents client-side permission bypasses.

**Rules**:
- Frontend MUST send all requests to FastAPI endpoints only
- Frontend MUST include JWT token in Authorization header
- Frontend MUST NOT call MCP tools directly
- Frontend MUST NOT make authorization decisions
- Frontend MUST support conversation resume via conversation_id
- Chat UI MUST be functional (not design-focused)

### X. Backward Compatibility

Phase I & II APIs MUST remain unchanged. Existing REST endpoints MUST continue to work. No breaking schema changes are allowed.

**Rationale**: Ensures existing functionality remains stable while adding new features. Prevents regression and maintains user trust.

**Rules**:
- All Phase I & II API endpoints MUST remain functional
- Database schema changes MUST be additive only (no breaking changes)
- Existing authentication flow MUST continue to work
- Phase III features MUST be implemented as new endpoints/tables
- No modifications to existing API contracts
- Existing frontend components MUST continue to function

### XI. Multi-Spec Architecture

Phase III MUST be implemented as MULTIPLE independent specs, each with single responsibility and clear boundaries.

**Rationale**: Enables parallel development, independent testing, and clear ownership of components. Reduces complexity and improves maintainability.

**Rules**:
- Phase III MUST be split into at least 3 specs:
  - AI Chat Backend (agent orchestration + chat endpoint)
  - MCP Tool Server (task actions as tools)
  - Chat Frontend (ChatKit UI integration)
- Each spec MUST be independently understandable
- Each spec MUST be independently testable
- Each spec MUST have clear inputs and outputs
- Each spec MUST declare dependencies explicitly
- Specs MUST NOT overlap in responsibility

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

### AI/Agent Standards (Phase III)

**Agent Behavior**:
- Agents MUST use natural language to communicate with users
- Agents MUST confirm destructive actions before execution
- Agents MUST provide clear feedback on action results
- Agents MUST handle ambiguous requests by asking clarifying questions
- Agents MUST gracefully handle errors with user-friendly messages
- Agents MUST NOT make assumptions about user intent

**MCP Tool Design**:
- Each tool MUST have a clear, single purpose
- Tool names MUST be descriptive and action-oriented (e.g., `create_task`, `list_tasks`)
- Tool parameters MUST be strongly typed and validated
- Tool responses MUST include success/failure status and relevant data
- Tools MUST log all actions for auditability
- Tools MUST handle concurrent requests safely

**Conversation Management**:
- Each conversation MUST have a unique conversation_id
- Conversation history MUST be stored in database
- Conversations MUST be resumable after server restart
- Conversation context MUST include: user_id, messages, tool calls, timestamps
- Old conversations SHOULD be archived but remain accessible

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

### Phase I & II Technology Stack

| Layer | Technology | Version | Rationale |
|-------|-----------|---------|-----------|
| Frontend | Next.js | 16+ (App Router) | Modern React framework with SSR, optimal for web apps |
| Backend | Python FastAPI | Latest stable | High-performance async API framework |
| ORM | SQLModel | Latest stable | Type-safe ORM combining SQLAlchemy + Pydantic |
| Database | Neon Serverless PostgreSQL | Latest | Serverless PostgreSQL with auto-scaling |
| Authentication | Better Auth | Latest | Modern auth library with JWT support |
| Spec-Driven | Claude Code + Spec-Kit Plus | Latest | Agentic development workflow tools |

### Phase III Technology Stack

| Layer | Technology | Version | Rationale |
|-------|-----------|---------|-----------|
| AI Framework | OpenAI Agents SDK | Latest stable | Official SDK for agent orchestration |
| MCP | Official MCP SDK | Latest stable | Model Context Protocol for tool integration |
| Chat UI | OpenAI ChatKit | Latest stable | Pre-built chat interface components |
| Agent Runtime | FastAPI (same backend) | Latest stable | Unified backend for REST + AI endpoints |

**NON-NEGOTIABLE**: This stack MUST NOT be changed without constitutional amendment.

**Phase III Constraints**:
- No vendor-specific hacks or workarounds
- No server-side memory storage for conversation state
- No hardcoded secrets or API keys
- No UI-driven authorization decisions

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

**Phase III Security**:
- MCP tools MUST validate JWT on every invocation
- Agent responses MUST NOT leak data from other users
- Conversation history MUST be user-scoped
- Tool calls MUST be authorized per user permissions

**Secret Management**:
- Secrets MUST be stored in `.env` files
- `.env` files MUST be in `.gitignore`
- Environment variables MUST be documented in `.env.example`
- Production secrets MUST be managed through secure deployment platform

## Functional Scope

### Phase I & II Core Features

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

### Phase III: AI Chatbot Features

The AI chatbot MUST implement:

1. **Natural Language Task Management**
   - Create tasks via natural language (e.g., "Add buy groceries to my list")
   - List tasks via natural language (e.g., "Show me my tasks")
   - Update tasks via natural language (e.g., "Mark buy groceries as done")
   - Delete tasks via natural language (e.g., "Remove buy groceries")
   - Query tasks via natural language (e.g., "What tasks do I have today?")

2. **Conversation Persistence**
   - Each conversation has unique conversation_id
   - Conversation history stored in database
   - Conversations resumable after server restart
   - Context maintained across multiple messages

3. **MCP Tool Integration**
   - Tools for: create_task, list_tasks, update_task, delete_task, get_task
   - Tools validate authorization server-side
   - Tools return structured responses
   - Tool calls logged for auditability

4. **Agent Orchestration**
   - Agent decides which tools to call based on user intent
   - Agent confirms destructive actions
   - Agent handles errors gracefully
   - Agent provides natural language feedback

5. **Chat UI**
   - ChatKit-based interface
   - Message history display
   - Loading indicators during tool execution
   - Error message display
   - Conversation resume support

### Out of Scope

The following are explicitly OUT OF SCOPE:
- Task sharing between users (Phase I & II)
- Task categories or tags
- Task due dates or reminders
- Email notifications
- Social features
- Advanced search or filtering
- Task attachments
- Collaborative editing
- Third-party integrations
- Voice input/output for chatbot
- Multi-language support
- Custom agent personalities

## Success Criteria

### Phase I & II Implementation Success

- [ ] All specs are fully implemented without manual code
- [ ] All 5 core features are functional
- [ ] Backend only returns data belonging to authenticated user
- [ ] JWT authentication works end-to-end (frontend ↔ backend)
- [ ] Frontend successfully consumes secured APIs
- [ ] API rejects unauthorized or cross-user access attempts

### Phase III Implementation Success

- [ ] Users can manage tasks via natural language
- [ ] AI agent uses MCP tools correctly and transparently
- [ ] Conversations persist across requests
- [ ] Backend remains stateless (no in-memory session state)
- [ ] All Phase I & II functionality remains stable
- [ ] Specs pass checklist validation before implementation
- [ ] Chat UI integrates with backend successfully
- [ ] Conversation resume works after server restart

### Quality Success

- [ ] Application is stable and handles errors gracefully
- [ ] Code is reproducible through agentic workflow
- [ ] All components follow separation of concerns
- [ ] Security constraints are enforced at every layer
- [ ] UI is responsive across devices
- [ ] Zero unauthorized data access
- [ ] No privilege escalation paths
- [ ] Deterministic behavior across all components
- [ ] Clear auditability of all actions

### Process Success

- [ ] Entire development history is auditable (specs, plans, prompts)
- [ ] No manual code modifications in git history
- [ ] All workflow phases completed in order
- [ ] Prompt History Records (PHRs) created for all major work
- [ ] Architecture Decision Records (ADRs) created for significant decisions
- [ ] Phase III implemented as multiple independent specs

### User Experience Success

- [ ] Users can sign up and sign in successfully
- [ ] Users can perform all CRUD operations on their tasks (UI + Chat)
- [ ] Users cannot see or access other users' tasks
- [ ] UI provides clear feedback for all actions
- [ ] Error messages are helpful and user-friendly
- [ ] Chat interface is intuitive and responsive
- [ ] Agent responses are natural and helpful

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

**Version**: 1.1.0 | **Ratified**: 2026-01-18 | **Last Amended**: 2026-02-06
