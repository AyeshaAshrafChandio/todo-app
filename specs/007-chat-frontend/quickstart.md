# Quickstart Guide: Chat Frontend

**Feature**: 007-chat-frontend
**Date**: 2026-02-06
**Phase**: Phase 1 - Setup and Testing Guide

## Overview

This guide provides step-by-step instructions for setting up, developing, and testing the Chat Frontend feature. Follow these instructions to get the development environment running and validate the implementation.

## Prerequisites

### Required Software
- **Node.js**: 18.x or higher
- **npm**: 9.x or higher (or yarn/pnpm)
- **Git**: For version control
- **Modern Browser**: Chrome 90+, Firefox 88+, Safari 14+, or Edge 90+

### Required Backend Services
- **Backend API**: Must be running (Spec 002, 005, 006)
  - Authentication endpoints: POST /api/auth/login, POST /api/auth/register
  - Chat endpoint: POST /api/chat
  - Default URL: http://localhost:8000

### Environment Setup
- **Operating System**: Windows, macOS, or Linux
- **IDE**: VS Code recommended (with TypeScript and Tailwind CSS extensions)

## Installation

### Step 1: Clone Repository

```bash
# If not already cloned
git clone <repository-url>
cd hakathon2/phase2

# Switch to feature branch
git checkout 007-chat-frontend
```

### Step 2: Install Frontend Dependencies

```bash
cd frontend

# Install dependencies
npm install

# Expected dependencies:
# - next@^14.0.0
# - react@^18.0.0
# - react-dom@^18.0.0
# - typescript@^5.0.0
# - tailwindcss@^3.0.0
# - @testing-library/react@^14.0.0
# - jest@^29.0.0
# - playwright@^1.40.0
```

### Step 3: Configure Environment Variables

```bash
# Create .env.local file in frontend directory
cd frontend
cp .env.example .env.local

# Edit .env.local with your configuration
# Required variables:
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Environment Variables**:
```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000  # Backend API base URL
```

### Step 4: Verify Backend is Running

```bash
# In a separate terminal, start the backend
cd backend
uvicorn app.main:app --reload --port 8000

# Verify backend is accessible
curl http://localhost:8000/health
# Expected: {"status": "ok"}
```

## Development

### Start Development Server

```bash
cd frontend
npm run dev

# Development server starts at http://localhost:3000
# Open browser to http://localhost:3000
```

### Development Workflow

1. **Make Changes**: Edit files in `frontend/src/`
2. **Hot Reload**: Changes automatically reload in browser
3. **Check Console**: Monitor browser console for errors
4. **Test Manually**: Navigate through authentication and chat flows

### Project Structure

```
frontend/src/
├── app/                    # Next.js App Router pages
│   ├── auth/login/         # Login page
│   ├── auth/register/      # Registration page
│   └── chat/               # Chat interface
├── components/             # Reusable components
│   ├── auth/               # Authentication components
│   ├── chat/               # Chat components
│   └── common/             # Common components
├── lib/                    # Utilities and API client
│   ├── api/                # API client functions
│   ├── hooks/              # Custom React hooks
│   └── types/              # TypeScript types
└── context/                # React Context providers
    ├── AuthContext.tsx     # Authentication state
    └── ChatContext.tsx     # Chat state
```

## Testing

### Unit Tests

**Run All Unit Tests**:
```bash
cd frontend
npm run test

# Run with coverage
npm run test:coverage

# Run in watch mode
npm run test:watch
```

**Test Specific Component**:
```bash
npm run test -- components/auth/LoginForm.test.tsx
```

**Expected Test Coverage**:
- Components: 80%+ coverage
- API client: 90%+ coverage
- Hooks: 80%+ coverage
- Context providers: 80%+ coverage

### E2E Tests

**Run E2E Tests**:
```bash
cd frontend

# Install Playwright browsers (first time only)
npx playwright install

# Run E2E tests
npm run test:e2e

# Run E2E tests in UI mode (interactive)
npm run test:e2e:ui

# Run specific test file
npx playwright test tests/e2e/auth.spec.ts
```

**E2E Test Scenarios**:
1. **Authentication Flow**:
   - User registers new account → Redirected to /chat
   - User logs in with valid credentials → Redirected to /chat
   - User logs in with invalid credentials → Error message shown
   - Unauthenticated user accesses /chat → Redirected to /auth/login

2. **Chat Flow**:
   - User sends message → Message appears in chat
   - AI responds → Response appears in chat
   - User scrolls up → Scroll position preserved
   - New message arrives → Auto-scrolls to bottom

3. **Error Handling**:
   - Network error → Error message with retry button
   - Token expires → Redirected to login
   - Server error → Error message with retry button

### Manual Testing

**Test Checklist**:

**Authentication (User Story 1)**:
- [ ] Navigate to /auth/login
- [ ] Enter valid email and password
- [ ] Click "Login" button
- [ ] Verify redirected to /chat
- [ ] Verify JWT token stored (check localStorage or cookies)
- [ ] Navigate to /auth/register
- [ ] Enter new email and password
- [ ] Click "Register" button
- [ ] Verify redirected to /chat
- [ ] Try invalid credentials → Verify error message

**Basic Chat (User Story 2)**:
- [ ] Navigate to /chat (authenticated)
- [ ] Type message in input field
- [ ] Press Enter or click Send
- [ ] Verify message appears in chat window
- [ ] Verify "AI is typing..." indicator appears
- [ ] Verify AI response appears
- [ ] Verify Send button disabled during AI processing
- [ ] Try Shift+Enter → Verify new line added (not sent)

**Message History (User Story 3)**:
- [ ] Send multiple messages (5+)
- [ ] Verify all messages displayed in chronological order
- [ ] Scroll up to view older messages
- [ ] Send new message → Verify auto-scrolls to bottom
- [ ] Refresh page → Verify messages cleared (session-based)

**Error Handling (User Story 4)**:
- [ ] Disconnect network → Send message → Verify error message
- [ ] Click "Retry" → Verify message sent successfully
- [ ] Wait for token expiration → Send message → Verify redirected to login
- [ ] Stop backend → Send message → Verify error message

**Responsive Design (User Story 5)**:
- [ ] Open on mobile device (or browser DevTools mobile view)
- [ ] Verify chat interface fits screen width
- [ ] Tap message input → Verify keyboard appears
- [ ] Verify touch targets are large enough (44x44px minimum)
- [ ] Test on tablet and desktop → Verify responsive layout

**Accessibility (User Story 6)**:
- [ ] Navigate with Tab key → Verify focus moves logically
- [ ] Press Enter on focused Send button → Verify message sent
- [ ] Press Escape in input → Verify input cleared
- [ ] Use screen reader (NVDA/JAWS/VoiceOver) → Verify messages announced
- [ ] Check color contrast → Verify meets WCAG AA (4.5:1)

## Validation

### Functional Requirements Validation

**Authentication Flow (FR-001 to FR-012)**:
- [ ] Login page exists at /auth/login
- [ ] Registration page exists at /auth/register
- [ ] Email format validated client-side
- [ ] Password minimum length validated (8+ characters)
- [ ] JWT token stored securely after authentication
- [ ] Authenticated users redirected from /auth/* to /chat
- [ ] Unauthenticated users redirected from /chat to /auth/login
- [ ] JWT token included in Authorization header for API requests
- [ ] 401 responses trigger redirect to login

**Chat Interface (FR-013 to FR-026)**:
- [ ] Chat interface exists at /chat route
- [ ] Scrollable message list displays user and AI messages
- [ ] Multiline textarea for message input
- [ ] Send button submits messages
- [ ] User message displayed immediately after submission
- [ ] "AI is typing..." indicator shown while waiting
- [ ] Send button and input disabled during AI processing
- [ ] AI response displayed when received
- [ ] Chat window auto-scrolls to latest message
- [ ] Enter key sends message (without Shift)
- [ ] Shift+Enter adds new line
- [ ] Message input cleared after successful send
- [ ] Send button disabled when input is empty

**Message Display (FR-027 to FR-032)**:
- [ ] User messages right-aligned with user color
- [ ] AI messages left-aligned with AI color and avatar
- [ ] Messages in chronological order (oldest at top)
- [ ] Scrolling works for long conversations
- [ ] Scroll position preserved when user scrolls up
- [ ] Auto-scroll to bottom when new message arrives (if at bottom)

**Error Handling (FR-033 to FR-040)**:
- [ ] Error message displayed on login failure
- [ ] Error message displayed on registration failure
- [ ] Error message displayed on chat API failure
- [ ] "Retry" option provided for failed messages
- [ ] Redirect to login on JWT token expiration
- [ ] Network error message on request timeout
- [ ] Generic error message for 500 server errors
- [ ] Error messages cleared on successful retry

**Responsive Design (FR-041 to FR-045)**:
- [ ] Correct rendering on desktop (1024px+ width)
- [ ] Correct rendering on tablet (768px-1023px width)
- [ ] Correct rendering on mobile (320px-767px width)
- [ ] Touch targets minimum 44x44px on mobile
- [ ] No horizontal scrolling on any screen size

**Accessibility (FR-046 to FR-050)**:
- [ ] Keyboard navigation works (Tab, Enter, Escape)
- [ ] ARIA labels provided for interactive elements
- [ ] New messages announced to screen readers
- [ ] Color contrast ratio 4.5:1 for text
- [ ] Focus indicators visible for keyboard navigation

**Security (FR-051 to FR-055)**:
- [ ] No MCP tools or backend details exposed in frontend
- [ ] No API keys or secrets in frontend code
- [ ] JWT token stored securely (httpOnly cookie or secure localStorage)
- [ ] No authorization decisions made client-side
- [ ] User input sanitized to prevent XSS

### Success Criteria Validation

- [ ] **SC-001**: Authentication completes in <30 seconds
- [ ] **SC-002**: Message send/receive in <10 seconds (excluding AI processing)
- [ ] **SC-003**: Chat interface loads in <2 seconds
- [ ] **SC-004**: 95% first message success rate
- [ ] **SC-005**: Works on Chrome, Firefox, Safari, Edge
- [ ] **SC-006**: Fully functional on mobile (iOS and Android)
- [ ] **SC-007**: 100% keyboard navigation coverage
- [ ] **SC-008**: WCAG AA color contrast (4.5:1 ratio)
- [ ] **SC-009**: Zero security vulnerabilities (JWT handling, XSS)
- [ ] **SC-010**: Judges evaluate UX-to-AI flow in <5 minutes

## Troubleshooting

### Common Issues

**Issue: "Cannot connect to backend"**
- **Cause**: Backend not running or wrong URL
- **Solution**:
  1. Verify backend is running: `curl http://localhost:8000/health`
  2. Check NEXT_PUBLIC_API_URL in .env.local
  3. Restart frontend dev server after changing .env.local

**Issue: "401 Unauthorized on /api/chat"**
- **Cause**: JWT token expired or invalid
- **Solution**:
  1. Check token in localStorage/cookies
  2. Try logging out and logging back in
  3. Verify backend JWT secret matches frontend expectation

**Issue: "CORS error in browser console"**
- **Cause**: Backend CORS not configured correctly
- **Solution**:
  1. Verify backend allows origin: http://localhost:3000
  2. Check backend CORS middleware configuration
  3. Ensure credentials: true in CORS config

**Issue: "Messages not appearing in chat"**
- **Cause**: State not updating or API response format mismatch
- **Solution**:
  1. Check browser console for errors
  2. Verify API response format matches expected: `{ reply: string }`
  3. Check ChatContext state updates in React DevTools

**Issue: "Styles not loading"**
- **Cause**: Tailwind CSS not configured correctly
- **Solution**:
  1. Verify tailwind.config.js exists
  2. Check globals.css imports Tailwind directives
  3. Restart dev server

**Issue: "TypeScript errors"**
- **Cause**: Type mismatches or missing types
- **Solution**:
  1. Run `npm run type-check` to see all errors
  2. Verify types in lib/types/ match API responses
  3. Check tsconfig.json configuration

## Performance Optimization

### Development Mode
- Hot reload enabled for fast iteration
- Source maps enabled for debugging
- No minification for readable errors

### Production Build

```bash
cd frontend

# Build for production
npm run build

# Test production build locally
npm run start

# Production optimizations:
# - Code minification
# - Tree shaking (unused code removed)
# - Image optimization
# - CSS purging (unused Tailwind classes removed)
```

### Performance Metrics

**Lighthouse Scores** (Target):
- Performance: 90+
- Accessibility: 95+
- Best Practices: 90+
- SEO: 90+

**Core Web Vitals** (Target):
- LCP (Largest Contentful Paint): <2.5s
- FID (First Input Delay): <100ms
- CLS (Cumulative Layout Shift): <0.1

## Deployment

### Build for Production

```bash
cd frontend
npm run build

# Output: .next/ directory with production build
```

### Environment Variables (Production)

```bash
# .env.production
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

### Deployment Platforms

**Vercel** (Recommended for Next.js):
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
cd frontend
vercel

# Follow prompts to configure deployment
```

**Other Platforms**:
- Netlify: Supports Next.js with adapter
- AWS Amplify: Supports Next.js
- Docker: Use official Next.js Docker image

## Next Steps

1. ✅ Quickstart guide documented
2. → Update agent context (CLAUDE.md)
3. → Run /sp.tasks to generate tasks.md
4. → Implementation phase with nextjs-ui-builder agent

## Support

### Documentation
- Next.js: https://nextjs.org/docs
- React: https://react.dev
- Tailwind CSS: https://tailwindcss.com/docs
- TypeScript: https://www.typescriptlang.org/docs

### Project Documentation
- Specification: specs/007-chat-frontend/spec.md
- Implementation Plan: specs/007-chat-frontend/plan.md
- Research: specs/007-chat-frontend/research.md
- Data Model: specs/007-chat-frontend/data-model.md
- API Contracts: specs/007-chat-frontend/contracts/api-client.yaml

### Getting Help
- Check browser console for errors
- Review backend logs for API issues
- Use React DevTools to inspect component state
- Check Network tab for API request/response details
