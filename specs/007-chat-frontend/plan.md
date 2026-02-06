# Implementation Plan: Chat Frontend

**Branch**: `007-chat-frontend` | **Date**: 2026-02-06 | **Spec**: [specs/007-chat-frontend/spec.md](./spec.md)
**Input**: Feature specification from `/specs/007-chat-frontend/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement a Next.js-based chat frontend for Phase III AI Todo Chatbot that enables users to manage tasks through natural language conversation. The frontend provides JWT-based authentication (login/register), a responsive chat interface for message exchange with the AI assistant, message history display, comprehensive error handling, and full accessibility support. The implementation uses Next.js 14+ App Router, TypeScript, and Tailwind CSS, communicating exclusively with backend APIs (Specs 002, 005, 006) without direct database or MCP tool access. The system maintains strict separation of concerns with the frontend handling only UI/UX while the backend manages AI reasoning, MCP tool execution, and data persistence.

## Technical Context

**Language/Version**: TypeScript 5.x with Next.js 14+ (App Router), React 18+
**Primary Dependencies**: Next.js 14+, React 18+, Tailwind CSS 3.x, React hooks/Context for state management
**Storage**: N/A (frontend only - no direct database access, communicates with backend APIs)
**Testing**: Jest + React Testing Library (unit tests), Playwright or Cypress (e2e tests)
**Target Platform**: Modern web browsers (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+), responsive design for mobile/tablet/desktop
**Project Type**: Web application (frontend only)
**Performance Goals**:
- Chat interface loads in <2 seconds on standard broadband
- Authentication completes in <30 seconds
- Message send/receive in <10 seconds (excluding AI processing time)
- 95% first message success rate
**Constraints**:
- JWT authentication required for all API requests
- Responsive design (mobile 320-767px, tablet 768-1023px, desktop 1024px+)
- WCAG AA accessibility compliance (4.5:1 contrast ratio, keyboard navigation)
- No direct MCP tool or database access (backend APIs only)
- Session-based message history (not persisted unless backend supports)
**Scale/Scope**:
- 6 user stories (2 P1 MVP, 2 P2, 2 P3)
- 55 functional requirements across 7 categories
- 3 main routes (/auth/login, /auth/register, /chat)
- 10-15 React components estimated

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Spec-Driven Development ✅
- **Status**: PASS
- **Evidence**: Complete specification exists at specs/007-chat-frontend/spec.md with 6 user stories, 55 functional requirements, and 10 success criteria. All requirements are unambiguous with zero [NEEDS CLARIFICATION] markers.
- **Compliance**: Implementation will strictly follow approved specification.

### Principle II: Agentic Workflow Integrity ✅
- **Status**: PASS
- **Evidence**: Following strict workflow: spec (completed) → plan (in progress) → tasks (next) → implement (via nextjs-ui-builder agent).
- **Compliance**: Will use nextjs-ui-builder agent for all frontend implementation. No manual coding permitted.

### Principle III: Correctness & Consistency ✅
- **Status**: PASS
- **Evidence**: API contracts clearly defined in spec (POST /api/auth/login, POST /api/auth/register, POST /api/chat). Frontend will use consistent data models matching backend schemas.
- **Compliance**: TypeScript types will ensure type safety. API client will enforce consistent error handling.

### Principle IV: Security by Design ✅
- **Status**: PASS
- **Evidence**: 5 security requirements (FR-051 to FR-055) covering JWT storage, no hardcoded secrets, no client-side authorization, XSS prevention.
- **Compliance**: JWT stored securely (httpOnly cookie or secure localStorage), Authorization header on all requests, input sanitization implemented.

### Principle V: Separation of Concerns ✅
- **Status**: PASS
- **Evidence**: Frontend communicates only with backend APIs (no direct database or MCP access). Clear boundaries: UI layer only.
- **Compliance**: No business logic in frontend. All authorization decisions made by backend. Frontend handles only presentation and user interaction.

### Principle IX: Frontend-Backend Integration ✅
- **Status**: PASS
- **Evidence**: All API requests go through FastAPI endpoints. JWT included in Authorization header. No direct MCP tool calls.
- **Compliance**: Frontend will use fetch/axios to call backend APIs exclusively. No MCP SDK imported in frontend code.

### Principle X: Backward Compatibility ✅
- **Status**: PASS
- **Evidence**: No changes to existing backend APIs (Specs 002, 005, 006). Frontend is new addition, no modifications to Phase I/II code.
- **Compliance**: Uses existing authentication endpoints from Spec 002, chat endpoint from Spec 005. No breaking changes.

### Overall Assessment: ✅ ALL GATES PASS

**No constitutional violations detected.** This is a frontend-only feature that:
- Follows spec-driven development workflow
- Uses appropriate specialized agent (nextjs-ui-builder)
- Maintains security boundaries (JWT, no client-side auth decisions)
- Respects separation of concerns (no direct database/MCP access)
- Preserves backward compatibility (no changes to existing APIs)

**Complexity Tracking**: Not applicable - no violations to justify.

## Project Structure

### Documentation (this feature)

```text
specs/007-chat-frontend/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (technology best practices)
├── data-model.md        # Phase 1 output (frontend state entities)
├── quickstart.md        # Phase 1 output (setup and testing guide)
├── contracts/           # Phase 1 output (API client contracts)
│   └── api-client.yaml  # OpenAPI-style documentation for frontend API client
├── checklists/          # Quality validation
│   └── requirements.md  # Specification quality checklist (completed)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
frontend/
├── src/
│   ├── app/                    # Next.js App Router pages
│   │   ├── auth/
│   │   │   ├── login/
│   │   │   │   └── page.tsx    # Login page (US1)
│   │   │   └── register/
│   │   │       └── page.tsx    # Registration page (US1)
│   │   ├── chat/
│   │   │   └── page.tsx        # Chat interface (US2, US3)
│   │   ├── layout.tsx          # Root layout with auth provider
│   │   └── page.tsx            # Landing/redirect page
│   ├── components/             # Reusable React components
│   │   ├── auth/
│   │   │   ├── LoginForm.tsx   # Login form component
│   │   │   └── RegisterForm.tsx # Registration form component
│   │   ├── chat/
│   │   │   ├── ChatInterface.tsx    # Main chat container (US2)
│   │   │   ├── MessageList.tsx      # Message history display (US3)
│   │   │   ├── MessageInput.tsx     # Message input with send button (US2)
│   │   │   ├── Message.tsx          # Individual message bubble
│   │   │   ├── TypingIndicator.tsx  # AI typing indicator (US2)
│   │   │   └── ErrorMessage.tsx     # Error display with retry (US4)
│   │   └── common/
│   │       ├── Button.tsx      # Reusable button component
│   │       ├── Input.tsx       # Reusable input component
│   │       └── LoadingSpinner.tsx # Loading indicator
│   ├── lib/                    # Utility functions and API client
│   │   ├── api/
│   │   │   ├── auth.ts         # Authentication API calls (login, register)
│   │   │   ├── chat.ts         # Chat API calls (send message)
│   │   │   └── client.ts       # Base API client with JWT handling
│   │   ├── hooks/
│   │   │   ├── useAuth.ts      # Authentication state hook
│   │   │   ├── useChat.ts      # Chat state management hook
│   │   │   └── useLocalStorage.ts # Secure token storage hook
│   │   └── types/
│   │       ├── auth.ts         # Authentication types
│   │       ├── chat.ts         # Chat message types
│   │       └── api.ts          # API response types
│   ├── context/                # React Context providers
│   │   ├── AuthContext.tsx     # Authentication context (US1)
│   │   └── ChatContext.tsx     # Chat state context (US2, US3)
│   └── styles/
│       └── globals.css         # Global styles with Tailwind
├── public/                     # Static assets
│   └── icons/                  # UI icons
├── tests/                      # Test files
│   ├── unit/
│   │   ├── components/         # Component unit tests
│   │   └── lib/                # Utility function tests
│   └── e2e/
│       ├── auth.spec.ts        # Authentication flow tests
│       └── chat.spec.ts        # Chat interaction tests
├── .env.example                # Environment variables template
├── .env.local                  # Local environment variables (gitignored)
├── next.config.js              # Next.js configuration
├── tailwind.config.js          # Tailwind CSS configuration
├── tsconfig.json               # TypeScript configuration
└── package.json                # Dependencies and scripts

backend/                        # Existing backend (NO CHANGES)
├── app/
│   ├── api/
│   │   ├── auth.py            # Existing auth endpoints (Spec 002)
│   │   └── chat.py            # Existing chat endpoint (Spec 005)
│   └── services/
│       └── mcp_tools.py       # Existing MCP tools (Spec 006)
```

**Structure Decision**: Web application structure (Option 2) with frontend-only changes. The frontend directory contains all new code for this feature. Backend directory remains unchanged, maintaining backward compatibility (Principle X). Frontend uses Next.js 14+ App Router with file-based routing, TypeScript for type safety, and Tailwind CSS for styling. Components are organized by feature (auth, chat, common) for maintainability. API client layer (lib/api/) abstracts backend communication and handles JWT token management. Context providers manage global state (authentication, chat messages). Tests are organized by type (unit, e2e) for comprehensive coverage.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**No violations detected** - Complexity tracking not required.

---

## Post-Design Constitution Re-Check

*Re-evaluation after Phase 1 design artifacts (research.md, data-model.md, contracts/, quickstart.md)*

### Principle I: Spec-Driven Development ✅
- **Status**: PASS (Confirmed)
- **Evidence**: All design artifacts align with specification. No deviations or scope creep detected.

### Principle II: Agentic Workflow Integrity ✅
- **Status**: PASS (Confirmed)
- **Evidence**: Planning workflow completed correctly. Ready for /sp.tasks → nextjs-ui-builder agent implementation.

### Principle III: Correctness & Consistency ✅
- **Status**: PASS (Confirmed)
- **Evidence**: API contracts (contracts/api-client.yaml) match backend APIs. TypeScript types ensure consistency.

### Principle IV: Security by Design ✅
- **Status**: PASS (Confirmed)
- **Evidence**: JWT storage strategy documented (httpOnly cookies preferred). XSS prevention, CSRF prevention, input sanitization all addressed in design.

### Principle V: Separation of Concerns ✅
- **Status**: PASS (Confirmed)
- **Evidence**: Frontend state entities (data-model.md) are client-side only. No business logic in frontend. API client layer abstracts backend communication.

### Principle IX: Frontend-Backend Integration ✅
- **Status**: PASS (Confirmed)
- **Evidence**: API client architecture (contracts/api-client.yaml) uses only backend APIs. No direct MCP or database access.

### Principle X: Backward Compatibility ✅
- **Status**: PASS (Confirmed)
- **Evidence**: No changes to existing backend code. Uses existing endpoints from Specs 002, 005, 006.

### Overall Assessment: ✅ ALL GATES PASS (POST-DESIGN)

**Design artifacts confirm constitutional compliance.** All principles satisfied:
- Spec-driven development maintained
- Agentic workflow followed correctly
- Security boundaries respected
- Separation of concerns enforced
- Backward compatibility preserved

**Ready for task generation** (/sp.tasks) and implementation (nextjs-ui-builder agent).

---

## Planning Summary

### Artifacts Generated

**Phase 0: Research** (✅ Complete)
- `research.md`: Technology decisions and best practices
  - 10 key decisions documented (Next.js App Router, JWT storage, state management, API client, responsive design, accessibility, error handling, message history, testing, development workflow)
  - All alternatives considered and rationale provided
  - Dependencies and integration points defined

**Phase 1: Design & Contracts** (✅ Complete)
- `data-model.md`: Frontend state entities
  - 3 entities defined: Message, User Session, Chat State
  - All attributes, validation rules, relationships, and lifecycles documented
  - State management architecture with Context providers
  - API integration contracts defined
- `contracts/api-client.yaml`: API client documentation
  - 3 API endpoints documented: POST /api/auth/login, POST /api/auth/register, POST /api/chat
  - Request/response formats with TypeScript types
  - Error handling strategy and retry logic
  - Security considerations (JWT management, CORS, input sanitization)
- `quickstart.md`: Setup and testing guide
  - Installation instructions
  - Development workflow
  - Testing strategy (unit, E2E, manual)
  - Validation checklists for all functional requirements and success criteria
  - Troubleshooting guide
- `CLAUDE.md`: Agent context updated with new technology stack

### Next Steps

1. **Run /sp.tasks**: Generate tasks.md with implementation tasks organized by user story
2. **Implementation**: Use nextjs-ui-builder agent for all frontend code
3. **Testing**: Execute unit tests, E2E tests, and manual validation
4. **Integration**: Validate frontend works with backend APIs (Specs 002, 005, 006)
5. **Commit & PR**: Use /sp.git.commit_pr to commit and create pull request
