---
id: 002
title: Phase III Constitution Update
stage: constitution
date: 2026-02-06
surface: agent
model: claude-sonnet-4-5
feature: none
branch: 004-frontend-fullstack-ui
user: Ali Haider
command: /sp.constitution
labels: ["constitution", "phase-iii", "ai-chatbot", "mcp-tools", "agents", "governance"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - N/A (documentation artifact)
---

## Prompt

Project: Phase III – AI-Powered Todo Chatbot (Full-Stack)

Objective:
Extend the existing authenticated, multi-user Todo web application with a
production-grade AI chatbot that manages tasks through natural language.
The system must use a stateless server architecture, MCP tools, and agent-based
reasoning while preserving all security and data-isolation guarantees from
Phase I & II.

--------------------------------------------------
CORE PRINCIPLES
--------------------------------------------------

1. Spec-Driven Development
- Every change must originate from an approved spec
- No manual coding outside Claude Code execution
- Specs → Plan → Tasks → Implement is mandatory

2. Separation of Concerns
- UI, Agent logic, and MCP tools must be isolated
- Frontend never calls MCP directly
- Agents never contain business logic
- MCP tools never contain conversational logic

3. Stateless Architecture
- Backend holds NO in-memory session state
- Conversation context must be reconstructed from database per request
- MCP tools must be stateless and idempotent

4. Security First
- JWT authentication required for all endpoints
- User identity derived ONLY from verified JWT
- No trust in client-supplied user_id
- Cross-user data access is strictly forbidden

5. Backward Compatibility
- Phase I & II APIs must remain unchanged
- Existing REST endpoints must continue to work
- No breaking schema changes allowed

--------------------------------------------------
SPEC BOUNDARIES
--------------------------------------------------

Phase III must be implemented as MULTIPLE specs, each with a single
responsibility:

- AI Chat Backend (agent orchestration + chat endpoint)
- MCP Tool Server (task actions as tools)
- Chat Frontend (ChatKit UI)

Each spec must:
- Be independently understandable
- Be independently testable
- Have clear inputs and outputs
- Declare dependencies explicitly

--------------------------------------------------
AGENT BEHAVIOR RULES
--------------------------------------------------

- Agents may only decide *what* to do
- Agents may never directly mutate the database
- All state changes must happen via MCP tools
- Agents must confirm actions in natural language
- Errors must be handled gracefully with user-friendly responses

--------------------------------------------------
MCP TOOL RULES
--------------------------------------------------

- Tools must map 1:1 to domain actions
- Tools must validate authorization server-side
- Tools must be stateless
- Tools must persist all changes to the database
- Tools must return structured, predictable outputs

--------------------------------------------------
FRONTEND RULES
--------------------------------------------------

- Frontend communicates ONLY with FastAPI
- JWT must be attached to every request
- Frontend does not infer permissions
- UI must support conversation resume via conversation_id
- Chat UI is functional, not design-focused

--------------------------------------------------
QUALITY BAR
--------------------------------------------------

- Zero unauthorized data access
- No privilege escalation paths
- Deterministic behavior
- Clear auditability of actions
- Production-ready security posture
- Resume conversations after server restart

--------------------------------------------------
SUCCESS CRITERIA
--------------------------------------------------

Phase III is successful when:

- Users manage todos via natural language
- AI uses MCP tools correctly and transparently
- Conversations persist across requests
- Backend remains stateless
- All Phase I & II functionality remains stable
- Specs pass checklist validation before implementation

## Response snapshot

Updated project constitution from v1.0.0 to v1.1.0 with Phase III AI-Powered Chatbot principles:

**6 New Principles Added (VI-XI)**:
- VI. Stateless Architecture - No in-memory state, conversation persistence in database
- VII. Agent Behavior Constraints - Agents decide, tools execute, no direct DB access
- VIII. MCP Tool Design - 1:1 domain mapping, server-side auth, stateless & idempotent
- IX. Frontend-Backend Integration - FastAPI only, JWT required, no MCP direct calls
- X. Backward Compatibility - Phase I & II APIs unchanged, additive schema changes only
- XI. Multi-Spec Architecture - Phase III split into 3+ independent specs

**Modified Principles**:
- Principle V (Separation of Concerns) - Expanded to include AI agent and MCP tool boundaries

**New Standards Added**:
- AI/Agent Standards: Agent behavior, MCP tool design, conversation management
- Phase III Technology Stack: OpenAI Agents SDK, MCP SDK, ChatKit
- Phase III Security: MCP tool JWT validation, user-scoped conversations, authorized tool calls

**Functional Scope Expanded**:
- Natural Language Task Management (create, list, update, delete via chat)
- Conversation Persistence (unique IDs, database storage, resume after restart)
- MCP Tool Integration (5 tools with server-side auth)
- Agent Orchestration (intent detection, action confirmation, error handling)
- Chat UI (ChatKit-based, message history, loading states)

**Key Constraints Enforced**:
- No vendor-specific hacks
- No server-side memory storage for conversation state
- No hardcoded secrets or API keys
- No UI-driven authorization decisions
- Full backward compatibility with Phase I & II

**Version Bump Rationale**: MINOR (1.0.0 → 1.1.0)
- Added 6 new principles without breaking existing ones
- Expanded existing principle (Separation of Concerns)
- Added new sections (AI/Agent Standards, Phase III stack, features)
- No removal or backward-incompatible changes
- All Phase I & II requirements remain intact

## Outcome

- ✅ Impact: Extended constitution to v1.1.0 with comprehensive Phase III governance covering AI agents, MCP tools, stateless architecture, and multi-spec requirements while maintaining full backward compatibility
- 🧪 Tests: N/A (documentation artifact)
- 📁 Files: Updated `.specify/memory/constitution.md` with Phase III principles and sync impact report
- 🔁 Next prompts: Ready to proceed with `/sp.specify` to create Phase III feature specifications (AI Chat Backend, MCP Tool Server, Chat Frontend) following new constitutional principles
- 🧠 Reflection: Constitution successfully expanded to govern AI-powered features while preserving all Phase I & II guarantees. Multi-spec architecture requirement ensures clear separation of concerns. Stateless architecture principle critical for production scalability. All 11 principles remain testable and enforceable.

## Evaluation notes (flywheel)

- Failure modes observed: None - constitution update successful, all placeholders filled, backward compatibility maintained
- Graders run and results (PASS/FAIL): PASS - Version bump correct (MINOR), no bracketed tokens, all Phase III principles clearly defined, templates compatible
- Prompt variant (if applicable): N/A - Standard constitution amendment workflow
- Next experiment (smallest change to try): Create first Phase III spec (MCP Tool Server) to validate new constitutional principles in practice, particularly stateless architecture and tool design requirements
