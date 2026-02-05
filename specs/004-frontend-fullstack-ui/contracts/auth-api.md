# Authentication API Contract

**Feature**: Frontend Full-Stack UI (004-frontend-fullstack-ui)
**Date**: 2026-02-05
**Backend Feature**: 002-authentication-and-api-security

## Overview

This document defines the authentication API endpoints that the frontend will consume. All endpoints are provided by the Better Auth integration in the backend.

## Base URL

```
{NEXT_PUBLIC_API_URL}/api/auth
```

## Endpoints

### 1. User Signup

**Endpoint**: `POST /api/auth/signup`

**Description**: Register a new user account

**Authentication**: None (public endpoint)

**Request Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Request Schema**:
```typescript
{
  email: string      // Valid email format
  password: string   // Minimum 8 characters
}
```

**Success Response** (201 Created):
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "created_at": "2026-02-05T10:30:00Z"
  }
}
```

**Error Responses**:

400 Bad Request - Invalid input:
```json
{
  "error": "Invalid email format",
  "detail": "Email must be a valid email address"
}
```

409 Conflict - Email already exists:
```json
{
  "error": "Email already registered",
  "detail": "An account with this email already exists"
}
```

**Frontend Usage**:
- Store token securely (httpOnly cookie or localStorage)
- Redirect to /dashboard on success
- Display error message on failure

---

### 2. User Signin

**Endpoint**: `POST /api/auth/signin`

**Description**: Authenticate an existing user

**Authentication**: None (public endpoint)

**Request Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Request Schema**:
```typescript
{
  email: string
  password: string
}
```

**Success Response** (200 OK):
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "created_at": "2026-02-05T10:30:00Z"
  }
}
```

**Error Responses**:

401 Unauthorized - Invalid credentials:
```json
{
  "error": "Invalid credentials",
  "detail": "Email or password is incorrect"
}
```

400 Bad Request - Missing fields:
```json
{
  "error": "Missing required fields",
  "detail": "Email and password are required"
}
```

**Frontend Usage**:
- Store token securely (httpOnly cookie or localStorage)
- Redirect to /dashboard on success
- Display error message on failure
- Do not reveal whether email or password is incorrect (security)

---

### 3. User Signout

**Endpoint**: `POST /api/auth/signout`

**Description**: Terminate user session

**Authentication**: Required (JWT token)

**Request Headers**:
```
Authorization: Bearer {token}
```

**Request Body**: None

**Success Response** (200 OK):
```json
{
  "message": "Successfully signed out"
}
```

**Error Responses**:

401 Unauthorized - Invalid or missing token:
```json
{
  "error": "Unauthorized",
  "detail": "Invalid or expired token"
}
```

**Frontend Usage**:
- Clear stored token (remove from cookie or localStorage)
- Redirect to /login
- Always succeed locally even if API call fails

---

### 4. Get Session

**Endpoint**: `GET /api/auth/session`

**Description**: Validate current session and get user info

**Authentication**: Required (JWT token)

**Request Headers**:
```
Authorization: Bearer {token}
```

**Success Response** (200 OK):
```json
{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "created_at": "2026-02-05T10:30:00Z"
  },
  "expires_at": "2026-02-05T11:30:00Z"
}
```

**Error Responses**:

401 Unauthorized - Invalid or expired token:
```json
{
  "error": "Unauthorized",
  "detail": "Session expired or invalid"
}
```

**Frontend Usage**:
- Call on app initialization to validate session
- Call periodically to check token validity
- Redirect to /login on 401 response
- Use to populate auth state in application

---

## Token Format

JWT tokens issued by Better Auth contain:

**Header**:
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

**Payload**:
```json
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",  // User ID
  "email": "user@example.com",
  "iat": 1612345678,  // Issued at (Unix timestamp)
  "exp": 1612349278   // Expires at (Unix timestamp)
}
```

**Signature**: HMACSHA256(base64UrlEncode(header) + "." + base64UrlEncode(payload), BETTER_AUTH_SECRET)

## Token Storage

**Recommended**: httpOnly cookies
- Prevents XSS attacks
- Automatically included in requests
- Requires CSRF protection

**Alternative**: localStorage
- Vulnerable to XSS attacks
- Must manually include in Authorization header
- No CSRF risk

## Token Refresh

Better Auth SDK handles token refresh automatically:
- On 401 response, SDK attempts to refresh token
- If refresh succeeds, original request is retried
- If refresh fails, user is logged out

## Error Handling

All authentication errors should:
1. Clear stored token
2. Redirect to /login
3. Display user-friendly error message
4. Log error for debugging (not sensitive info)

## Security Considerations

1. **Never log tokens**: Tokens should never appear in console logs or error messages
2. **HTTPS only**: All authentication requests must use HTTPS in production
3. **Token expiration**: Tokens expire after 1 hour (configurable)
4. **Rate limiting**: Backend implements rate limiting on auth endpoints
5. **Password requirements**: Minimum 8 characters (enforced by backend)
6. **Email validation**: Valid email format required (enforced by backend)

## Frontend Implementation Example

```typescript
// lib/api/auth.ts
import { apiClient } from './client'
import type { AuthResponse, SessionResponse, SignupInput, SigninInput } from '@/lib/types'

export async function signup(data: SignupInput): Promise<AuthResponse> {
  return apiClient<AuthResponse>('/api/auth/signup', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function signin(data: SigninInput): Promise<AuthResponse> {
  return apiClient<AuthResponse>('/api/auth/signin', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function signout(): Promise<void> {
  await apiClient('/api/auth/signout', {
    method: 'POST',
  })
}

export async function getSession(): Promise<SessionResponse> {
  return apiClient<SessionResponse>('/api/auth/session')
}
```

## Testing Checklist

- [ ] Signup with valid credentials succeeds
- [ ] Signup with invalid email fails with 400
- [ ] Signup with existing email fails with 409
- [ ] Signin with valid credentials succeeds
- [ ] Signin with invalid credentials fails with 401
- [ ] Signout clears token and redirects to /login
- [ ] Session validation with valid token succeeds
- [ ] Session validation with expired token fails with 401
- [ ] Token is automatically included in subsequent requests
- [ ] Token refresh works automatically on expiration
