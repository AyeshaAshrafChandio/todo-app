# Research & Technology Decisions

**Feature**: Frontend Full-Stack UI (004-frontend-fullstack-ui)
**Date**: 2026-02-05
**Phase**: Phase 0 - Research

## Overview

This document captures all technology decisions and implementation patterns for the frontend full-stack UI feature. All research resolves technical unknowns identified in the Technical Context section of plan.md.

## 1. Better Auth Client Integration

### Decision: Better Auth Client-Side with JWT Token Flow

**Research Findings**:
- Better Auth provides a client-side SDK for Next.js integration
- JWT tokens are issued by Better Auth on successful authentication
- Tokens can be stored in httpOnly cookies (preferred) or localStorage
- Client-side SDK handles token refresh automatically

**Implementation Pattern**:
```typescript
// lib/auth/client.ts
import { createAuthClient } from 'better-auth/client'

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  credentials: 'include', // For httpOnly cookies
})

// Usage in components
const { signIn, signUp, signOut, session } = authClient
```

**Token Storage Strategy**:
- **Primary**: httpOnly cookies (prevents XSS attacks)
- **Fallback**: Secure localStorage with appropriate warnings
- **Rationale**: httpOnly cookies are more secure but require CSRF protection

**Token Refresh Pattern**:
- Better Auth SDK handles refresh automatically
- On 401 response, SDK attempts token refresh
- If refresh fails, trigger logout and redirect to /login

**Alternatives Considered**:
- Manual JWT handling: Rejected due to complexity and error-prone implementation
- NextAuth.js: Rejected because Better Auth is already integrated in backend

## 2. Next.js App Router Patterns

### Decision: Server Components by Default, Client Components for Interactivity

**Research Findings**:
- Server Components are the default in Next.js App Router
- Client Components must be explicitly marked with `'use client'`
- Server Components can fetch data directly without API calls
- Client Components are needed for interactivity (forms, buttons, state)

**Component Architecture**:
```
Server Components (default):
- Page layouts
- Static content
- Data fetching from backend APIs
- SEO-critical content

Client Components ('use client'):
- Forms with user input
- Interactive buttons (toggle, delete)
- State management (loading, errors)
- Event handlers
```

**Route Groups Pattern**:
```
app/
├── (auth)/          # Public routes (login, register)
│   └── layout.tsx   # Auth layout (no header/nav)
└── (protected)/     # Protected routes (dashboard, tasks, teams)
    └── layout.tsx   # Protected layout (with auth check, header, nav)
```

**Middleware for Route Protection**:
```typescript
// middleware.ts
export function middleware(request: NextRequest) {
  const token = request.cookies.get('auth-token')

  if (!token && request.nextUrl.pathname.startsWith('/dashboard')) {
    return NextResponse.redirect(new URL('/login', request.url))
  }

  if (token && (request.nextUrl.pathname === '/login' || request.nextUrl.pathname === '/register')) {
    return NextResponse.redirect(new URL('/dashboard', request.url))
  }
}
```

**Loading and Error Boundaries**:
- `loading.tsx`: Automatic loading UI during navigation
- `error.tsx`: Error boundary for runtime errors
- Place at route level for granular control

**Alternatives Considered**:
- Pages Router: Rejected because App Router is modern standard
- Client-side only: Rejected due to SEO and performance concerns

## 3. API Client Architecture

### Decision: Custom Fetch Wrapper with JWT Injection

**Research Findings**:
- Native Fetch API is sufficient for REST API calls
- Interceptors can be implemented with wrapper functions
- TypeScript provides type safety for requests/responses
- No need for external libraries (axios, ky)

**Implementation Pattern**:
```typescript
// lib/api/client.ts
export async function apiClient<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getAuthToken() // From cookies or localStorage

  const config: RequestInit = {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': token ? `Bearer ${token}` : '',
      ...options.headers,
    },
  }

  const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}${endpoint}`, config)

  if (response.status === 401) {
    // Token expired or invalid
    clearAuthToken()
    window.location.href = '/login'
    throw new Error('Unauthorized')
  }

  if (response.status === 403) {
    throw new Error('Access denied')
  }

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.message || 'API request failed')
  }

  return response.json()
}
```

**Global Error Handling**:
- 401: Clear token, redirect to /login
- 403: Display "Access Denied" message
- 4xx: Display user-friendly error message
- 5xx: Display "Server error, please try again"

**Type-Safe API Calls**:
```typescript
// lib/api/tasks.ts
export async function getTasks(userId: string): Promise<Task[]> {
  return apiClient<Task[]>(`/api/users/${userId}/tasks`)
}

export async function createTask(userId: string, data: CreateTaskInput): Promise<Task> {
  return apiClient<Task>(`/api/users/${userId}/tasks`, {
    method: 'POST',
    body: JSON.stringify(data),
  })
}
```

**Alternatives Considered**:
- Axios: Rejected due to bundle size and unnecessary features
- React Query: Rejected to avoid external state management complexity
- SWR: Rejected for same reason as React Query

## 4. State Management

### Decision: Server Components + React State (No External Library)

**Research Findings**:
- Server Components can fetch data directly from backend
- Client Components use React useState/useReducer for local state
- No need for global state management (Redux, Zustand)
- Data refetching after mutations keeps state synchronized

**State Management Strategy**:

**Server-Side Data Fetching** (Server Components):
```typescript
// app/(protected)/tasks/page.tsx
export default async function TasksPage() {
  const session = await getSession()
  const tasks = await getTasks(session.user.id)

  return <TaskList tasks={tasks} />
}
```

**Client-Side State** (Client Components):
```typescript
// components/tasks/TaskForm.tsx
'use client'

export function TaskForm() {
  const [title, setTitle] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      await createTask(userId, { title })
      router.refresh() // Refetch server data
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return <form onSubmit={handleSubmit}>...</form>
}
```

**Optimistic Updates**:
- For better UX, update UI immediately
- Revert on error
- Example: Toggle task completion

**Cache Invalidation**:
- Use `router.refresh()` to refetch server data
- Use `revalidatePath()` for specific routes
- No manual cache management needed

**Alternatives Considered**:
- Redux: Rejected due to complexity and boilerplate
- Zustand: Rejected because Server Components reduce need for global state
- React Query: Rejected to keep dependencies minimal

## 5. Responsive Design Patterns

### Decision: Mobile-First with Tailwind CSS Responsive Utilities

**Research Findings**:
- Tailwind CSS provides responsive utilities (sm:, md:, lg:, xl:)
- Mobile-first approach: base styles for mobile, breakpoints for larger screens
- Touch targets should be minimum 44x44px for mobile
- Flexbox and Grid for responsive layouts

**Responsive Design Guidelines**:

**Breakpoints** (Tailwind defaults):
- `sm`: 640px (small tablets)
- `md`: 768px (tablets)
- `lg`: 1024px (laptops)
- `xl`: 1280px (desktops)

**Mobile-First Pattern**:
```tsx
<div className="
  flex flex-col gap-4        // Mobile: vertical stack
  md:flex-row md:gap-6       // Tablet+: horizontal layout
  lg:gap-8                   // Desktop: larger gaps
">
  <TaskList />
  <TaskDetail />
</div>
```

**Touch-Friendly Components**:
```tsx
<button className="
  min-h-[44px] min-w-[44px]  // Minimum touch target
  px-4 py-2                   // Comfortable padding
  text-base                   // Readable text size
  active:scale-95             // Touch feedback
">
  Create Task
</button>
```

**Responsive Navigation**:
- Mobile: Hamburger menu
- Tablet+: Horizontal navigation bar
- Desktop: Sidebar + top navigation

**Responsive Typography**:
```tsx
<h1 className="
  text-2xl font-bold         // Mobile
  md:text-3xl                // Tablet
  lg:text-4xl                // Desktop
">
  Dashboard
</h1>
```

**Alternatives Considered**:
- Desktop-first: Rejected because mobile traffic is significant
- CSS-in-JS: Rejected because Tailwind is already in tech stack
- Custom media queries: Rejected in favor of Tailwind utilities

## Summary of Key Decisions

| Area | Decision | Rationale |
|------|----------|-----------|
| Auth Integration | Better Auth client SDK with httpOnly cookies | Security (XSS prevention), automatic token refresh |
| Component Pattern | Server Components by default, Client for interactivity | Performance, SEO, reduced JavaScript bundle |
| Route Protection | Middleware + route groups | Centralized auth logic, clean separation |
| API Client | Custom Fetch wrapper with JWT injection | Type safety, full control, no external dependencies |
| State Management | Server Components + React state | Simplicity, leverage Next.js patterns |
| Responsive Design | Mobile-first with Tailwind utilities | Mobile traffic, progressive enhancement |

## Implementation Risks & Mitigations

1. **Token Expiration During Session**
   - Risk: User loses work if token expires
   - Mitigation: Better Auth SDK handles refresh automatically
   - Fallback: Save form data to localStorage before API calls

2. **Server Component Data Staleness**
   - Risk: User sees outdated data after mutations
   - Mitigation: Use `router.refresh()` after mutations
   - Fallback: Add manual refresh button

3. **Mobile Performance**
   - Risk: Large JavaScript bundle on mobile
   - Mitigation: Use Server Components, code splitting by route
   - Fallback: Lazy load non-critical components

4. **CSRF Attacks** (if using httpOnly cookies)
   - Risk: Cross-site request forgery
   - Mitigation: Implement CSRF tokens or SameSite cookie attribute
   - Fallback: Use localStorage instead (less secure but no CSRF risk)

## Next Steps

1. Generate data-model.md with TypeScript type definitions
2. Generate API contracts in contracts/ directory
3. Generate quickstart.md with setup instructions
4. Update agent context with these decisions
5. Proceed to task breakdown (/sp.tasks)
