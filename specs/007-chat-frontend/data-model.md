# Data Model: Chat Frontend

**Feature**: 007-chat-frontend
**Date**: 2026-02-06
**Phase**: Phase 1 - Frontend State Entities

## Overview

This document defines the frontend state entities for the Chat Frontend. These are **client-side state objects** only - they do not represent database tables. The frontend communicates with backend APIs (Specs 002, 005, 006) and manages local state for UI rendering and user interaction.

## Entity Definitions

### Entity 1: Message

**Purpose**: Represents a single message in the chat conversation (user or AI)

**Attributes**:
- `id` (string, required): Unique identifier for the message (UUID or timestamp-based)
- `role` (enum, required): Message sender - "user" or "assistant"
- `content` (string, required): Message text content (1-10,000 characters)
- `timestamp` (Date, required): When the message was created
- `status` (enum, required): Message delivery status - "sending", "sent", "error"

**Validation Rules**:
- `id` must be unique within the conversation
- `role` must be exactly "user" or "assistant"
- `content` must not be empty (min 1 character)
- `content` must not exceed 10,000 characters
- `timestamp` must be valid Date object
- `status` must be one of: "sending", "sent", "error"

**Relationships**:
- Part of messages array in ChatState
- No backend persistence (session-based unless backend adds support)

**Lifecycle**:
1. **Created**: When user sends message (status: "sending") or AI responds (status: "sent")
2. **Updated**: Status changes from "sending" to "sent" (success) or "error" (failure)
3. **Persisted**: In React state (ChatContext) during session
4. **Cleared**: On page refresh or logout

**State Transitions**:
```
User Message:
  [Created: sending] → [API Success: sent] → [Displayed]
                    → [API Failure: error] → [Retry or Clear]

AI Message:
  [Created: sent] → [Displayed]
```

**TypeScript Type**:
```typescript
type MessageRole = 'user' | 'assistant';
type MessageStatus = 'sending' | 'sent' | 'error';

interface Message {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: Date;
  status: MessageStatus;
}
```

---

### Entity 2: User Session

**Purpose**: Represents the current authenticated user's session state

**Attributes**:
- `token` (string | null, required): JWT token from authentication (null if not authenticated)
- `user` (object | null, required): User information (null if not authenticated)
  - `id` (string): User UUID
  - `email` (string): User email address
- `isAuthenticated` (boolean, required): Whether user is currently authenticated
- `isLoading` (boolean, required): Whether authentication check is in progress
- `error` (string | null, required): Authentication error message (null if no error)

**Validation Rules**:
- `token` must be valid JWT format if present
- `user.email` must be valid email format
- `isAuthenticated` is true only if token and user are present
- `isLoading` is true during login/register/token verification
- `error` is set only when authentication fails

**Relationships**:
- Required for all API requests (token in Authorization header)
- Determines access to protected routes (/chat)
- Independent of ChatState

**Lifecycle**:
1. **Initialized**: On app load (check for existing token)
2. **Authenticated**: On successful login/register (token and user set)
3. **Updated**: On token refresh (new token)
4. **Cleared**: On logout or token expiration (token and user set to null)

**State Transitions**:
```
[Unauthenticated] → [Login/Register] → [Authenticated] → [Access /chat]
                                     → [Failure] → [Show Error]

[Authenticated] → [Token Expires] → [Redirect to Login]
               → [Logout] → [Unauthenticated]
```

**TypeScript Type**:
```typescript
interface User {
  id: string;
  email: string;
}

interface UserSession {
  token: string | null;
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}
```

---

### Entity 3: Chat State

**Purpose**: Represents the current state of the chat interface

**Attributes**:
- `messages` (array, required): Array of Message objects in chronological order
- `isLoading` (boolean, required): Whether AI is processing a message
- `error` (string | null, required): Current error message (null if no error)
- `inputValue` (string, required): Current value of message input field

**Validation Rules**:
- `messages` array can be empty (new conversation)
- `messages` must be ordered by timestamp (oldest first)
- `isLoading` is true only when waiting for AI response
- `error` is cleared when user retries or sends new message
- `inputValue` can be empty (no validation until send)

**Relationships**:
- Contains all Message entities for current session
- Requires UserSession for API calls (JWT token)
- Independent state from UserSession

**Lifecycle**:
1. **Initialized**: On /chat page load (empty messages array)
2. **Updated**: On each message send/receive
3. **Cleared**: On page refresh (session-based)
4. **Persisted**: In React state (ChatContext) during session

**State Transitions**:
```
[Empty Chat] → [User Sends Message] → [Loading: true] → [AI Responds] → [Loading: false]
                                                      → [Error] → [Show Error + Retry]

[Has Messages] → [User Scrolls Up] → [Preserve Position]
               → [New Message] → [Auto-scroll to Bottom]
```

**TypeScript Type**:
```typescript
interface ChatState {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  inputValue: string;
}
```

---

## State Management Architecture

### Context Providers

**AuthContext** (Global - Root Level):
- Provides: UserSession state and authentication functions
- Functions: `login(email, password)`, `register(email, password)`, `logout()`
- Consumers: All pages (for route protection), API client (for token)

**ChatContext** (Page Level - /chat only):
- Provides: ChatState and chat functions
- Functions: `sendMessage(content)`, `retryMessage(messageId)`, `clearError()`
- Consumers: Chat components (MessageList, MessageInput, etc.)

### State Flow

```
User Action → Component → Context Function → API Call → Update State → Re-render

Example: Send Message
1. User types in MessageInput, clicks Send
2. MessageInput calls chatContext.sendMessage(content)
3. sendMessage() creates Message with status "sending", adds to messages array
4. sendMessage() calls API client with JWT token from authContext
5. API responds → Update message status to "sent", add AI response
6. ChatState updates → Components re-render with new messages
```

### State Persistence

**Session-Based (Default)**:
- All state cleared on page refresh
- No localStorage/sessionStorage for messages
- Token stored securely (httpOnly cookie or secure localStorage)

**Optional Backend Persistence**:
- If backend adds conversation_id support:
  - Fetch conversation history on /chat page load
  - Send conversation_id with each message
  - Resume conversations after refresh

## API Integration

### Authentication APIs (Spec 002)

**POST /api/auth/login**:
- Request: `{ email: string, password: string }`
- Response: `{ token: string, user: { id: string, email: string } }`
- Updates: UserSession (token, user, isAuthenticated)

**POST /api/auth/register**:
- Request: `{ email: string, password: string }`
- Response: `{ token: string, user: { id: string, email: string } }`
- Updates: UserSession (token, user, isAuthenticated)

### Chat API (Spec 005)

**POST /api/chat**:
- Request: `{ message: string }`
- Headers: `{ Authorization: "Bearer <token>" }`
- Response: `{ reply: string }`
- Updates: ChatState (adds user message, adds AI response, clears loading)

## Validation Summary

### Client-Side Validation (Before API Call)

**Authentication**:
- Email format validation (regex)
- Password minimum length (8 characters)
- Password confirmation match (register only)

**Chat**:
- Message not empty (min 1 character)
- Message length limit (max 10,000 characters)
- User is authenticated (has valid token)

### Server-Side Validation (Backend Responsibility)

**Authentication**:
- Email uniqueness (register)
- Password strength requirements
- Credentials correctness (login)

**Chat**:
- JWT token validity
- User authorization
- Message content safety (XSS prevention)

## Error Handling

### Authentication Errors

- **Invalid Credentials**: "Invalid email or password"
- **Email Already Exists**: "Email already registered"
- **Network Error**: "Network error - please check your connection"
- **Server Error**: "Something went wrong - please try again"

### Chat Errors

- **Token Expired (401)**: Redirect to login with "Session expired, please log in again"
- **Network Error**: "Network error - please check your connection" + Retry button
- **Server Error (500)**: "Something went wrong - please try again" + Retry button
- **Empty Response**: "No response from AI - please try again" + Retry button

## Performance Considerations

### Message List Rendering

- **Virtualization**: Not needed for MVP (assume <100 messages per session)
- **Optimization**: Use React.memo for Message component to prevent unnecessary re-renders
- **Auto-scroll**: Only scroll to bottom if user is already at bottom (preserve scroll position)

### State Updates

- **Batching**: React 18 automatic batching handles multiple state updates
- **Memoization**: Use useMemo for derived state (e.g., filtered messages)
- **Callbacks**: Use useCallback for event handlers to prevent re-renders

## Security Considerations

### Token Storage

- **Preferred**: httpOnly cookie (not accessible via JavaScript)
- **Fallback**: Secure localStorage with `secure-` prefix
- **Never**: Regular cookie, sessionStorage, or in-memory only (poor UX)

### XSS Prevention

- **Input Sanitization**: Sanitize user input before sending to API
- **Output Encoding**: React automatically escapes JSX content
- **CSP Headers**: Implement Content Security Policy to prevent script injection

### CSRF Prevention

- **JWT in Header**: Authorization header (not cookie) prevents CSRF
- **SameSite Cookie**: If using httpOnly cookie, set SameSite=Strict

## Testing Strategy

### Unit Tests

- **Message Entity**: Validation, state transitions
- **UserSession Entity**: Authentication state changes
- **ChatState Entity**: Message array operations, loading states

### Integration Tests

- **AuthContext**: Login/register/logout flows
- **ChatContext**: Send message, receive response, error handling

### E2E Tests

- **Authentication Flow**: Register → Login → Redirect to /chat
- **Chat Flow**: Send message → See AI response → Message history
- **Error Handling**: Network error → Retry → Success

## Next Steps

1. ✅ Data model documented
2. → Generate contracts/api-client.yaml (API client documentation)
3. → Generate quickstart.md (setup and testing guide)
4. → Update agent context (CLAUDE.md)
5. → Run /sp.tasks to generate tasks.md
