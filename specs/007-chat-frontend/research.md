# Research: Chat Frontend

**Feature**: 007-chat-frontend
**Date**: 2026-02-06
**Phase**: Phase 0 - Technology Research & Best Practices

## Overview

This document captures research findings and technology decisions for the Chat Frontend implementation. All decisions are based on industry best practices, framework recommendations, and alignment with constitutional principles.

## Technology Decisions

### Decision 1: Next.js 14+ App Router

**Decision**: Use Next.js 14+ with App Router (not Pages Router)

**Rationale**:
- **Modern Architecture**: App Router is the recommended approach for new Next.js projects (official Next.js documentation)
- **Server Components**: Enables better performance with React Server Components by default
- **File-based Routing**: Intuitive routing structure with `app/` directory
- **Built-in Layouts**: Shared layouts reduce code duplication
- **Loading States**: Built-in loading.tsx and error.tsx patterns
- **Streaming**: Better UX with progressive rendering

**Alternatives Considered**:
- **Pages Router**: Older approach, still supported but not recommended for new projects
- **React Router**: Would require additional setup, Next.js provides routing out of the box
- **Remix**: Alternative framework, but Next.js is specified in constitution

**Implementation Notes**:
- Use `'use client'` directive only when client-side interactivity is required (forms, state management)
- Prefer Server Components for static content (layouts, landing pages)
- Client Components for: authentication forms, chat interface, message input

### Decision 2: JWT Token Storage Strategy

**Decision**: Use httpOnly cookies for JWT storage (preferred), with secure localStorage as fallback

**Rationale**:
- **httpOnly Cookies (Preferred)**:
  - Not accessible via JavaScript (XSS protection)
  - Automatically included in requests
  - Secure flag prevents transmission over HTTP
  - SameSite attribute prevents CSRF attacks
- **Secure localStorage (Fallback)**:
  - If backend doesn't support httpOnly cookies
  - Requires manual Authorization header management
  - Vulnerable to XSS but mitigated with Content Security Policy

**Alternatives Considered**:
- **sessionStorage**: Lost on tab close, poor UX for users
- **In-memory only**: Lost on page refresh, poor UX
- **Regular cookies (not httpOnly)**: Vulnerable to XSS attacks

**Implementation Notes**:
- Check if backend (Spec 002) supports httpOnly cookies
- If yes: Backend sets cookie on login, frontend reads from cookie automatically
- If no: Store in localStorage with `secure-` prefix, implement CSP headers
- Always use HTTPS in production
- Implement token refresh mechanism for session continuity

### Decision 3: State Management Approach

**Decision**: Use React Context + hooks for global state (authentication, chat messages)

**Rationale**:
- **Simplicity**: No external state management library needed for this scope
- **React Native**: Context API is built into React, no additional dependencies
- **Sufficient for Scope**: 2 global states (auth, chat) don't require Redux/Zustand complexity
- **Type Safety**: Works well with TypeScript
- **Performance**: Context re-renders can be optimized with useMemo/useCallback

**Alternatives Considered**:
- **Redux**: Overkill for 2 global states, adds boilerplate
- **Zustand**: Lightweight but unnecessary for this scope
- **Recoil**: Experimental, not production-ready
- **Jotai**: Good alternative but Context is sufficient

**Implementation Notes**:
- Create `AuthContext` for: JWT token, user email, authentication status, login/logout functions
- Create `ChatContext` for: messages array, loading state, error state, send message function
- Use custom hooks: `useAuth()`, `useChat()` for consuming context
- Optimize with `useMemo` for context values to prevent unnecessary re-renders
- Keep context providers at appropriate levels (AuthContext at root, ChatContext at /chat page)

### Decision 4: API Client Architecture

**Decision**: Create centralized API client with interceptors for JWT handling and error management

**Rationale**:
- **DRY Principle**: Single place for API configuration
- **Consistent Error Handling**: Centralized error interceptor
- **JWT Management**: Automatic Authorization header injection
- **Type Safety**: TypeScript types for all API responses
- **Testability**: Easy to mock for unit tests

**Alternatives Considered**:
- **Direct fetch calls**: Repetitive, error-prone, no centralized error handling
- **SWR/React Query**: Overkill for simple request/response pattern, adds complexity
- **Axios**: Popular but fetch API is native and sufficient

**Implementation Notes**:
```typescript
// lib/api/client.ts
- Base client with fetch wrapper
- Request interceptor: Add Authorization header from token
- Response interceptor: Handle 401 (redirect to login), 500 (show error)
- Type-safe response parsing

// lib/api/auth.ts
- login(email, password): Promise<{ token: string, user: User }>
- register(email, password): Promise<{ token: string, user: User }>

// lib/api/chat.ts
- sendMessage(message: string): Promise<{ reply: string }>
```

### Decision 5: Responsive Design Strategy

**Decision**: Mobile-first approach with Tailwind CSS utility classes and responsive breakpoints

**Rationale**:
- **Mobile-First**: Design for smallest screen first, progressively enhance
- **Tailwind CSS**: Utility-first CSS framework specified in constitution
- **Responsive Utilities**: Built-in breakpoint system (sm, md, lg, xl)
- **Consistency**: Design system with consistent spacing, colors, typography
- **Performance**: Purges unused CSS in production

**Alternatives Considered**:
- **Desktop-first**: Harder to scale down, mobile experience suffers
- **CSS Modules**: More verbose, less consistent than utility classes
- **Styled Components**: Runtime overhead, not specified in constitution

**Implementation Notes**:
- Breakpoints: mobile (default, 320-767px), tablet (md: 768-1023px), desktop (lg: 1024px+)
- Touch targets: Minimum 44x44px on mobile (Tailwind: `min-h-11 min-w-11`)
- Typography: Responsive font sizes (`text-sm md:text-base lg:text-lg`)
- Layout: Flexbox/Grid with responsive columns (`flex-col md:flex-row`)
- Test on real devices: iOS Safari, Android Chrome

### Decision 6: Accessibility Implementation

**Decision**: Follow WCAG AA standards with semantic HTML, ARIA labels, and keyboard navigation

**Rationale**:
- **Legal Compliance**: WCAG AA is industry standard
- **Inclusive Design**: Makes app usable for users with disabilities
- **SEO Benefits**: Semantic HTML improves search engine indexing
- **Keyboard Navigation**: Essential for power users and accessibility

**Alternatives Considered**:
- **WCAG AAA**: Too strict for MVP, can be enhanced later
- **No accessibility**: Violates constitutional principles and best practices

**Implementation Notes**:
- **Semantic HTML**: Use `<button>`, `<form>`, `<input>`, `<nav>` (not `<div>` with onClick)
- **ARIA Labels**: `aria-label`, `aria-describedby`, `aria-live` for screen readers
- **Keyboard Navigation**: Tab order, Enter to submit, Escape to clear
- **Color Contrast**: 4.5:1 ratio for normal text (Tailwind: `text-gray-900` on `bg-white`)
- **Focus Indicators**: Visible focus rings (Tailwind: `focus:ring-2 focus:ring-blue-500`)
- **Screen Reader Announcements**: Use `aria-live="polite"` for new messages

### Decision 7: Error Handling Strategy

**Decision**: Implement comprehensive error handling with user-friendly messages and retry options

**Rationale**:
- **User Experience**: Clear feedback on what went wrong and how to fix it
- **Resilience**: Graceful degradation when backend is unavailable
- **Debugging**: Detailed error logging for development
- **Recovery**: Retry mechanisms for transient failures

**Alternatives Considered**:
- **Generic errors only**: Poor UX, users don't know what to do
- **No retry options**: Forces page refresh, poor UX

**Implementation Notes**:
- **Error Types**:
  - Network errors: "Network error - please check your connection" + Retry button
  - 401 Unauthorized: Redirect to login with "Session expired" message
  - 500 Server errors: "Something went wrong - please try again" + Retry button
  - Validation errors: Field-specific messages (e.g., "Email is required")
- **Error Display**: Toast notifications or inline error messages
- **Retry Logic**: Exponential backoff for network errors (1s, 2s, 4s)
- **Error Boundaries**: React Error Boundary for component crashes

### Decision 8: Message History Management

**Decision**: Session-based message history stored in React state, with optional backend persistence

**Rationale**:
- **Simplicity**: No complex state synchronization required
- **Performance**: Fast access to messages in memory
- **Flexibility**: Backend can add persistence later without frontend changes
- **Scope Alignment**: Spec assumes session-based unless backend supports persistence

**Alternatives Considered**:
- **IndexedDB**: Overkill for session-based history, adds complexity
- **LocalStorage**: Limited storage, not suitable for large conversations
- **Backend-only**: Requires API call for every message display, poor performance

**Implementation Notes**:
- Store messages in ChatContext state: `messages: Message[]`
- Message type: `{ id: string, role: 'user' | 'assistant', content: string, timestamp: Date, status: 'sending' | 'sent' | 'error' }`
- Auto-scroll to bottom when new message arrives
- Preserve scroll position when user scrolls up to view history
- Clear messages on page refresh (session-based)
- If backend adds conversation_id support: Fetch history on page load

### Decision 9: Testing Strategy

**Decision**: Unit tests for components/utilities, E2E tests for critical user flows

**Rationale**:
- **Unit Tests**: Fast, isolated, test individual components
- **E2E Tests**: Slow but comprehensive, test full user flows
- **Balance**: Focus on critical paths (auth, chat) with E2E, everything else with unit tests

**Alternatives Considered**:
- **Unit tests only**: Miss integration issues
- **E2E tests only**: Slow, expensive, hard to debug
- **No tests**: Violates quality standards

**Implementation Notes**:
- **Unit Tests** (Jest + React Testing Library):
  - Component rendering tests
  - User interaction tests (click, type, submit)
  - API client tests (mocked responses)
  - Hook tests (useAuth, useChat)
- **E2E Tests** (Playwright or Cypress):
  - Authentication flow: Register → Login → Redirect to chat
  - Chat flow: Send message → See AI response → Message history
  - Error handling: Network error → Retry → Success
- **Coverage Target**: 80%+ for critical paths

### Decision 10: Development Workflow

**Decision**: Use nextjs-ui-builder agent for all implementation, following spec-driven workflow

**Rationale**:
- **Constitutional Requirement**: Principle II mandates agentic workflow
- **Consistency**: All code generated through same process
- **Auditability**: Full development history in PHRs
- **Quality**: Agent follows best practices and patterns

**Alternatives Considered**:
- **Manual coding**: Violates constitutional principles
- **Mixed approach**: Inconsistent, hard to audit

**Implementation Notes**:
- After planning phase: Run `/sp.tasks` to generate tasks.md
- Use `nextjs-ui-builder` agent for all frontend implementation tasks
- Agent will create components, pages, API client, context providers
- Agent will implement responsive design with Tailwind CSS
- Agent will add accessibility features (ARIA labels, keyboard navigation)
- Agent will write unit tests for components
- Commit after each task or logical group

## Best Practices Summary

### Next.js 14+ App Router
- Use Server Components by default, Client Components only when needed
- Implement loading.tsx and error.tsx for better UX
- Use Next.js Image component for optimized images
- Implement proper metadata for SEO

### TypeScript
- Define types for all API responses
- Use strict mode for better type safety
- Create shared types in lib/types/
- Avoid `any` type, use `unknown` if type is truly unknown

### Tailwind CSS
- Use utility classes for styling
- Create custom components for repeated patterns
- Use responsive utilities (sm:, md:, lg:)
- Implement dark mode support if time permits (not in MVP)

### React Best Practices
- Use functional components with hooks
- Implement proper error boundaries
- Optimize re-renders with useMemo/useCallback
- Keep components small and focused (single responsibility)

### Security Best Practices
- Never store sensitive data in localStorage without encryption
- Implement Content Security Policy headers
- Sanitize user input to prevent XSS
- Use HTTPS in production
- Validate JWT on every backend request (backend responsibility)

### Accessibility Best Practices
- Use semantic HTML elements
- Provide ARIA labels for interactive elements
- Ensure keyboard navigation works
- Maintain 4.5:1 color contrast ratio
- Test with screen readers (NVDA, JAWS, VoiceOver)

### Performance Best Practices
- Lazy load components when appropriate
- Optimize images with Next.js Image component
- Minimize bundle size (tree shaking, code splitting)
- Use React.memo for expensive components
- Implement proper loading states

## Dependencies

### Required Dependencies
```json
{
  "dependencies": {
    "next": "^14.0.0",
    "react": "^18.0.0",
    "react-dom": "^18.0.0",
    "typescript": "^5.0.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "@types/react": "^18.0.0",
    "@types/react-dom": "^18.0.0",
    "tailwindcss": "^3.0.0",
    "postcss": "^8.0.0",
    "autoprefixer": "^10.0.0",
    "jest": "^29.0.0",
    "@testing-library/react": "^14.0.0",
    "@testing-library/jest-dom": "^6.0.0",
    "playwright": "^1.40.0"
  }
}
```

### Optional Dependencies (if needed)
- `date-fns`: Date formatting (if timestamps need formatting)
- `clsx`: Conditional class names (if complex styling logic)
- `react-hot-toast`: Toast notifications (for error messages)

## Integration Points

### Backend APIs (Existing)
- **POST /api/auth/login** (Spec 002): Returns JWT token
- **POST /api/auth/register** (Spec 002): Returns JWT token
- **POST /api/chat** (Spec 005): Accepts message, returns AI response

### Expected API Contracts
```typescript
// POST /api/auth/login
Request: { email: string, password: string }
Response: { token: string, user: { id: string, email: string } }

// POST /api/auth/register
Request: { email: string, password: string }
Response: { token: string, user: { id: string, email: string } }

// POST /api/chat
Request: { message: string }
Headers: { Authorization: "Bearer <token>" }
Response: { reply: string }
```

## Risk Mitigation

### Risk 1: Backend API Contract Mismatch
**Mitigation**: Define clear TypeScript types for API responses. Add API version handling. Implement graceful degradation if response format changes.

### Risk 2: JWT Token Security
**Mitigation**: Use httpOnly cookies if possible. If localStorage required, implement CSP headers and input sanitization. Never expose token in URL or logs.

### Risk 3: Poor Mobile Experience
**Mitigation**: Test on real mobile devices early. Use mobile-first responsive design. Ensure touch targets meet 44x44px minimum. Test with mobile keyboard.

### Risk 4: Accessibility Gaps
**Mitigation**: Follow WCAG AA guidelines from start. Test with screen readers. Ensure keyboard navigation. Use semantic HTML. Add ARIA labels.

### Risk 5: Slow AI Response Times
**Mitigation**: Show clear loading indicators. Set user expectations with "AI is thinking..." message. Implement 30-second timeout. Provide retry option.

## Next Steps

1. ✅ Phase 0 Complete: Research documented
2. → Phase 1: Generate data-model.md (frontend state entities)
3. → Phase 1: Generate contracts/api-client.yaml (API client documentation)
4. → Phase 1: Generate quickstart.md (setup and testing guide)
5. → Phase 1: Update agent context (CLAUDE.md)
6. → Phase 2: Run /sp.tasks to generate tasks.md
7. → Implementation: Use nextjs-ui-builder agent for all frontend code
