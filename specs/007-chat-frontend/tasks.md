# Tasks: Chat Frontend

**Input**: Design documents from `/specs/007-chat-frontend/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api-client.yaml, quickstart.md

**Tests**: Not explicitly requested in specification - focusing on implementation tasks only

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each feature.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Frontend: `frontend/src/`
- Tests: `frontend/tests/`
- All paths relative to repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and verification of existing structure

- [ ] T001 Verify Next.js 14+ is installed in frontend environment with App Router support
- [ ] T002 Verify TypeScript 5.x and Tailwind CSS 3.x are configured in frontend/
- [ ] T003 Verify backend APIs are accessible (POST /api/auth/login, POST /api/auth/register, POST /api/chat)
- [ ] T004 Create environment variables template at frontend/.env.example with NEXT_PUBLIC_API_URL
- [ ] T005 Verify frontend/src/ directory structure exists (app/, components/, lib/, context/)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core types and utilities that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story implementation can begin until this phase is complete

- [ ] T006 Create TypeScript types in frontend/src/lib/types/auth.ts
  - User interface (id, email)
  - LoginRequest, RegisterRequest, AuthResponse interfaces
  - UserSession interface (token, user, isAuthenticated, isLoading, error)

- [ ] T007 Create TypeScript types in frontend/src/lib/types/chat.ts
  - MessageRole type ('user' | 'assistant')
  - MessageStatus type ('sending' | 'sent' | 'error')
  - Message interface (id, role, content, timestamp, status)
  - ChatState interface (messages, isLoading, error, inputValue)

- [ ] T008 Create TypeScript types in frontend/src/lib/types/api.ts
  - ApiError interface (error, detail)
  - Generic API response types

- [ ] T009 Create base API client in frontend/src/lib/api/client.ts
  - ApiClient class with request interceptors
  - Automatic Authorization header injection
  - Error handling for 401 (SESSION_EXPIRED), network errors, 500 errors
  - get() and post() methods with TypeScript generics

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - User Authentication (Priority: P1) 🎯 MVP

**Goal**: Enable users to authenticate with the system before accessing the AI chat interface to ensure secure, personalized task management

**Independent Test**: User can navigate to login page, enter credentials, receive JWT token, and be redirected to chat interface. Token is stored securely and included in subsequent API requests. User can also register a new account.

### Implementation for User Story 1

- [ ] T010 [P] [US1] Create AuthContext provider in frontend/src/context/AuthContext.tsx
  - UserSession state management
  - login(email, password) function
  - register(email, password) function
  - logout() function
  - Token storage/retrieval (localStorage or httpOnly cookie)
  - 401 handling (redirect to login)

- [ ] T011 [P] [US1] Create useAuth custom hook in frontend/src/lib/hooks/useAuth.ts
  - Exports AuthContext consumer hook
  - Returns { user, token, isAuthenticated, isLoading, error, login, register, logout }

- [ ] T012 [P] [US1] Create authentication API client in frontend/src/lib/api/auth.ts
  - login(email, password): Promise<AuthResponse>
  - register(email, password): Promise<AuthResponse>
  - Uses base ApiClient from T009

- [ ] T013 [US1] Create LoginForm component in frontend/src/components/auth/LoginForm.tsx
  - Email and password input fields
  - Client-side validation (email format, password min 8 chars)
  - Submit handler calls useAuth().login()
  - Error message display
  - Loading state during submission
  - Link to registration page

- [ ] T014 [US1] Create RegisterForm component in frontend/src/components/auth/RegisterForm.tsx
  - Email, password, and confirm password fields
  - Client-side validation (email format, password min 8 chars, passwords match)
  - Submit handler calls useAuth().register()
  - Error message display (including "Email already registered")
  - Loading state during submission
  - Link to login page

- [ ] T015 [US1] Create login page at frontend/src/app/auth/login/page.tsx
  - Renders LoginForm component
  - Redirects to /chat if already authenticated
  - Uses Next.js App Router

- [ ] T016 [US1] Create registration page at frontend/src/app/auth/register/page.tsx
  - Renders RegisterForm component
  - Redirects to /chat if already authenticated
  - Uses Next.js App Router

- [ ] T017 [US1] Create root layout in frontend/src/app/layout.tsx
  - Wraps app with AuthContext provider
  - Includes global styles and Tailwind CSS
  - Sets up metadata for SEO

- [ ] T018 [US1] Implement route protection for /chat page
  - Check authentication status in chat page
  - Redirect to /auth/login if not authenticated
  - Handle token expiration (401 responses)

**Checkpoint**: At this point, User Story 1 (authentication) should be fully functional and testable independently

---

## Phase 4: User Story 2 - Basic Chat Interaction (Priority: P1) 🎯 MVP

**Goal**: Enable users to send natural language messages to the AI assistant and receive responses to manage tasks through conversation

**Independent Test**: Authenticated user can type message in input field, press Enter or click Send, see message appear in chat window, see AI "typing..." indicator, and receive AI response. Messages are displayed with distinct styling for user vs AI.

### Implementation for User Story 2

- [ ] T019 [P] [US2] Create ChatContext provider in frontend/src/context/ChatContext.tsx
  - ChatState state management (messages, isLoading, error, inputValue)
  - sendMessage(content: string) function
  - retryMessage(messageId: string) function
  - clearError() function
  - Message state updates (add user message, add AI response, update status)

- [ ] T020 [P] [US2] Create useChat custom hook in frontend/src/lib/hooks/useChat.ts
  - Exports ChatContext consumer hook
  - Returns { messages, isLoading, error, inputValue, sendMessage, retryMessage, clearError }

- [ ] T021 [P] [US2] Create chat API client in frontend/src/lib/api/chat.ts
  - sendMessage(message: string): Promise<ChatResponse>
  - Uses base ApiClient with JWT token from AuthContext
  - Handles 401 (token expired), network errors, 500 errors

- [ ] T022 [US2] Create Message component in frontend/src/components/chat/Message.tsx
  - Displays single message bubble
  - Different styling for user vs AI messages (role-based)
  - User messages: right-aligned, user color
  - AI messages: left-aligned, AI color, avatar/icon
  - Timestamp display
  - Status indicator for "sending" or "error" states

- [ ] T023 [US2] Create TypingIndicator component in frontend/src/components/chat/TypingIndicator.tsx
  - Displays "AI is typing..." indicator
  - Animated dots or spinner
  - Only shown when isLoading is true

- [ ] T024 [US2] Create MessageInput component in frontend/src/components/chat/MessageInput.tsx
  - Multiline textarea for message input
  - Send button
  - Enter key sends message (without Shift)
  - Shift+Enter adds new line
  - Disable input and button when isLoading is true
  - Disable Send button when input is empty
  - Clear input after successful send
  - Character counter (max 10,000 characters)

- [ ] T025 [US2] Create MessageList component in frontend/src/components/chat/MessageList.tsx
  - Scrollable container for messages
  - Renders Message components for each message in chronological order (oldest at top)
  - Auto-scroll to bottom when new message arrives (if user is at bottom)
  - Preserve scroll position when user scrolls up

- [ ] T026 [US2] Create ChatInterface component in frontend/src/components/chat/ChatInterface.tsx
  - Main chat container
  - Renders MessageList and MessageInput
  - Renders TypingIndicator when AI is processing
  - Handles message submission via useChat().sendMessage()

- [ ] T027 [US2] Create chat page at frontend/src/app/chat/page.tsx
  - Wraps ChatInterface with ChatContext provider
  - Requires authentication (redirects to /auth/login if not authenticated)
  - Uses Next.js App Router

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently (MVP complete!)

---

## Phase 5: User Story 3 - Message History Display (Priority: P2)

**Goal**: Enable users to see the history of their conversation with the AI assistant to maintain context and review previous task operations

**Independent Test**: User can see all messages from current session displayed in chronological order with clear visual distinction between user and AI messages. Scrolling works correctly for long conversations.

### Implementation for User Story 3

- [ ] T028 [P] [US3] Enhance MessageList component in frontend/src/components/chat/MessageList.tsx
  - Implement scroll position preservation when user scrolls up
  - Auto-scroll to bottom only if user is already at bottom (not if scrolled up)
  - Handle long conversations (10+ messages) with proper scrolling

- [ ] T029 [P] [US3] Add message timestamps to Message component in frontend/src/components/chat/Message.tsx
  - Display timestamp for each message
  - Format timestamp (e.g., "2:30 PM" or "2 hours ago")
  - Optional: Use date-fns library for formatting

- [ ] T030 [US3] Implement session-based message persistence in ChatContext
  - Messages persist during session (in React state)
  - Messages cleared on page refresh (session-based)
  - Optional: Add support for conversation_id if backend provides it

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently

---

## Phase 6: User Story 4 - Error Handling and Recovery (Priority: P2)

**Goal**: Provide users with clear feedback when errors occur (network issues, authentication failures, API errors) and options to recover gracefully

**Independent Test**: User can trigger various error scenarios (network disconnect, expired token, API error) and see appropriate error messages with recovery options. System handles errors gracefully without crashing.

### Implementation for User Story 4

- [ ] T031 [P] [US4] Create ErrorMessage component in frontend/src/components/chat/ErrorMessage.tsx
  - Displays error message with icon
  - Retry button for recoverable errors
  - Close button to dismiss error
  - Different styling for different error types (network, auth, server)

- [ ] T032 [US4] Enhance ChatContext error handling in frontend/src/context/ChatContext.tsx
  - Distinguish error types: network, 401 (token expired), 500 (server error)
  - Implement retry logic with exponential backoff (1s, 2s, 4s)
  - Clear error on successful retry
  - Handle SESSION_EXPIRED error (redirect to login)

- [ ] T033 [US4] Enhance AuthContext error handling in frontend/src/context/AuthContext.tsx
  - Display specific error messages: "Invalid email or password", "Email already registered"
  - Handle network errors: "Network error - please check your connection"
  - Handle server errors: "Something went wrong - please try again"
  - Clear error on successful login/register

- [ ] T034 [US4] Add error display to ChatInterface component in frontend/src/components/chat/ChatInterface.tsx
  - Render ErrorMessage component when error exists
  - Pass retry handler to ErrorMessage
  - Handle token expiration (redirect to login with message)

- [ ] T035 [US4] Add error display to LoginForm and RegisterForm components
  - Display error messages below form
  - Clear error on new submission attempt
  - Show loading state during submission

**Checkpoint**: At this point, User Stories 1, 2, 3, AND 4 should all work independently

---

## Phase 7: User Story 5 - Responsive Mobile Experience (Priority: P3)

**Goal**: Enable the chat interface to work well on mobile devices with appropriate touch interactions and responsive layout

**Independent Test**: User can access chat interface on mobile device (or browser with mobile viewport), see properly sized UI elements, interact with touch gestures, and complete full chat workflow.

### Implementation for User Story 5

- [ ] T036 [P] [US5] Add responsive styles to ChatInterface component in frontend/src/components/chat/ChatInterface.tsx
  - Mobile (320-767px): Full-width layout, vertical stacking
  - Tablet (768-1023px): Optimized layout with proper spacing
  - Desktop (1024px+): Centered layout with max-width
  - Use Tailwind CSS responsive utilities (sm:, md:, lg:)

- [ ] T037 [P] [US5] Add responsive styles to MessageInput component in frontend/src/components/chat/MessageInput.tsx
  - Mobile: Full-width input, larger touch targets (min 44x44px)
  - Tablet/Desktop: Optimized width with proper spacing
  - Handle mobile keyboard appearance (input remains visible)

- [ ] T038 [P] [US5] Add responsive styles to Message component in frontend/src/components/chat/Message.tsx
  - Mobile: Smaller font size, compact layout
  - Tablet/Desktop: Standard font size and spacing
  - Ensure message bubbles don't overflow on small screens

- [ ] T039 [P] [US5] Add responsive styles to LoginForm and RegisterForm components
  - Mobile: Full-width inputs, larger buttons
  - Tablet/Desktop: Centered form with max-width
  - Touch-friendly input fields and buttons

- [ ] T040 [US5] Test responsive design on real mobile devices
  - iOS Safari: Test touch interactions, keyboard behavior
  - Android Chrome: Test touch interactions, keyboard behavior
  - Verify no horizontal scrolling on any screen size

**Checkpoint**: At this point, User Stories 1-5 should all work independently

---

## Phase 8: User Story 6 - Accessibility Support (Priority: P3)

**Goal**: Enable users with accessibility needs (screen reader, keyboard-only navigation) to use the chat interface effectively

**Independent Test**: User can navigate entire chat interface using only keyboard (Tab, Enter, Escape), screen reader announces messages correctly, and UI has proper contrast ratios.

### Implementation for User Story 6

- [ ] T041 [P] [US6] Add ARIA labels to MessageInput component in frontend/src/components/chat/MessageInput.tsx
  - aria-label for textarea: "Type your message"
  - aria-label for Send button: "Send message"
  - aria-disabled when button is disabled

- [ ] T042 [P] [US6] Add ARIA labels to Message component in frontend/src/components/chat/Message.tsx
  - role="article" for message container
  - aria-label with role and content: "User message: [content]" or "AI assistant: [content]"

- [ ] T043 [P] [US6] Add ARIA live region to MessageList component in frontend/src/components/chat/MessageList.tsx
  - aria-live="polite" for new message announcements
  - Screen reader announces new AI messages

- [ ] T044 [P] [US6] Add keyboard navigation support to ChatInterface component
  - Tab key moves focus through interactive elements (input → send button)
  - Enter key sends message (when input is focused)
  - Escape key clears input (when input is focused)

- [ ] T045 [P] [US6] Add keyboard navigation support to LoginForm and RegisterForm components
  - Tab key moves through form fields
  - Enter key submits form
  - Escape key clears form (optional)

- [ ] T046 [P] [US6] Ensure color contrast meets WCAG AA standards (4.5:1 ratio)
  - Text on background: 4.5:1 minimum
  - Interactive elements: Clear focus indicators
  - Use Tailwind CSS colors that meet contrast requirements

- [ ] T047 [US6] Add focus indicators to all interactive elements
  - Visible focus ring on buttons, inputs, links
  - Use Tailwind CSS focus utilities (focus:ring-2 focus:ring-blue-500)
  - Test keyboard navigation flow

**Checkpoint**: All 6 user stories should now be independently functional

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple components and ensure production readiness

- [ ] T048 [P] Create common Button component in frontend/src/components/common/Button.tsx
  - Reusable button with variants (primary, secondary, danger)
  - Loading state with spinner
  - Disabled state
  - Accessible (ARIA labels, keyboard support)

- [ ] T049 [P] Create common Input component in frontend/src/components/common/Input.tsx
  - Reusable input with label and error message
  - Email and password variants
  - Accessible (ARIA labels, error announcements)

- [ ] T050 [P] Create common LoadingSpinner component in frontend/src/components/common/LoadingSpinner.tsx
  - Animated spinner for loading states
  - Accessible (aria-label="Loading")

- [ ] T051 [P] Add global styles in frontend/src/styles/globals.css
  - Tailwind CSS directives (@tailwind base, components, utilities)
  - Custom CSS for animations (typing indicator, spinner)
  - Reset styles for consistent cross-browser rendering

- [ ] T052 [P] Configure Tailwind CSS in frontend/tailwind.config.js
  - Custom colors for user/AI messages
  - Responsive breakpoints (mobile, tablet, desktop)
  - Custom utilities for chat interface

- [ ] T053 [P] Configure TypeScript in frontend/tsconfig.json
  - Strict mode enabled
  - Path aliases (@/ for src/)
  - Next.js-specific settings

- [ ] T054 [P] Create useLocalStorage hook in frontend/src/lib/hooks/useLocalStorage.ts
  - Secure token storage/retrieval
  - Handles localStorage errors gracefully
  - Used by AuthContext for token persistence

- [ ] T055 Verify all components use semantic HTML
  - Use <button> for buttons (not <div> with onClick)
  - Use <form> for forms
  - Use <input> for inputs
  - Use <nav> for navigation

- [ ] T056 Verify all error messages are user-friendly
  - No technical jargon or stack traces
  - Clear instructions on how to fix
  - Consistent error message format

- [ ] T057 Verify all loading states are implemented
  - Login/register: Button shows loading spinner
  - Chat: TypingIndicator shows while AI processes
  - Message: Status shows "sending" while submitting

- [ ] T058 Verify all success states are implemented
  - Login/register: Redirect to /chat on success
  - Chat: Message status changes to "sent" on success
  - Error: Error cleared on successful retry

- [ ] T059 Update frontend/README.md with setup instructions
  - Installation steps
  - Environment variables
  - Development workflow
  - Testing instructions

- [ ] T060 Create frontend/.env.example with required variables
  - NEXT_PUBLIC_API_URL=http://localhost:8000

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user story implementations
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1) - Authentication**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1) - Basic Chat**: Can start after Foundational (Phase 2) - No dependencies on other stories (but requires US1 for authentication)
- **User Story 3 (P2) - Message History**: Can start after Foundational (Phase 2) - Enhances US2 components
- **User Story 4 (P2) - Error Handling**: Can start after Foundational (Phase 2) - Enhances US1 and US2 components
- **User Story 5 (P3) - Responsive Mobile**: Can start after Foundational (Phase 2) - Enhances all components
- **User Story 6 (P3) - Accessibility**: Can start after Foundational (Phase 2) - Enhances all components

### Within Each User Story

- Component implementations can run in parallel (different files)
- Page implementations depend on component completion
- Context providers should be implemented before components that use them

### Parallel Opportunities

- All Setup tasks (T001-T005) can run in parallel
- Phase 2 tasks (T006-T009) can run in parallel (different files)
- Once Phase 2 completes, user story implementations can start in parallel:
  - T010-T018 (US1 Authentication) || T019-T027 (US2 Basic Chat) || T028-T030 (US3 Message History) || T031-T035 (US4 Error Handling) || T036-T040 (US5 Responsive) || T041-T047 (US6 Accessibility)
- All Polish tasks (T048-T054) can run in parallel

---

## Parallel Example: All User Stories After Foundation

```bash
# After Phase 2 (T006-T009) completes, launch user story implementations in parallel:
Task: "Implement User Story 1 - Authentication (T010-T018)"
Task: "Implement User Story 2 - Basic Chat (T019-T027)"
Task: "Implement User Story 3 - Message History (T028-T030)"
Task: "Implement User Story 4 - Error Handling (T031-T035)"
Task: "Implement User Story 5 - Responsive Mobile (T036-T040)"
Task: "Implement User Story 6 - Accessibility (T041-T047)"

# Then complete Polish phase:
Task: "Implement Polish & Cross-Cutting Concerns (T048-T060)"
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only)

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Foundational (T006-T009) - CRITICAL
3. Complete Phase 3: User Story 1 - Authentication (T010-T018)
4. Complete Phase 4: User Story 2 - Basic Chat (T019-T027)
5. **STOP and VALIDATE**: Test authentication and chat independently
   - User can register/login → Redirected to /chat
   - User can send message → AI responds
   - Messages displayed correctly
   - Token stored securely
   - Errors handled gracefully
6. Deploy/demo if ready (MVP complete!)

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 (Authentication) → Test independently → Deploy/Demo (MVP Part 1)
3. Add User Story 2 (Basic Chat) → Test independently → Deploy/Demo (MVP Complete!)
4. Add User Story 3 (Message History) → Test independently → Deploy/Demo
5. Add User Story 4 (Error Handling) → Test independently → Deploy/Demo
6. Add User Story 5 (Responsive Mobile) → Test independently → Deploy/Demo
7. Add User Story 6 (Accessibility) → Test independently → Deploy/Demo
8. Each user story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T009)
2. Once Foundational is done:
   - Developer A: User Story 1 (Authentication) - T010-T018
   - Developer B: User Story 2 (Basic Chat) - T019-T027
   - Developer C: User Story 3 (Message History) - T028-T030
   - Developer D: User Story 4 (Error Handling) - T031-T035
   - Developer E: User Story 5 (Responsive Mobile) - T036-T040
   - Developer F: User Story 6 (Accessibility) - T041-T047
3. User stories complete and integrate independently
4. Team collaborates on Polish phase (T048-T060)

---

## Notes

- [P] tasks = different files or independent sections, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- All components use TypeScript for type safety
- All components use Tailwind CSS for styling
- All components follow Next.js 14+ App Router conventions
- All API calls use centralized API client with JWT handling
- All state management uses React Context + hooks
- Commit after each task or logical group
- Stop at any checkpoint to validate user story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
