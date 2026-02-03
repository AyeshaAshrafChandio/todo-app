---
name: auth-skill
description: Implement secure authentication systems including signup, signin, password hashing, JWT tokens, and best-practice authentication flows.
---

# Authentication Skill

## Instructions

1. **User Authentication Flow**
   - User signup with validated inputs
   - Secure user signin
   - Token-based session handling
   - Logout and token invalidation

2. **Password Security**
   - Hash passwords before storage
   - Use strong hashing algorithms (bcrypt, argon2, scrypt)
   - Never store plain-text passwords
   - Apply salting automatically

3. **JWT Authentication**
   - Generate JWT on successful login
   - Store minimal user data in token payload
   - Set token expiration
   - Verify JWT on protected routes

4. **Authorization**
   - Protect private routes using middleware
   - Role-based or permission-based access
   - Refresh token strategy (optional but recommended)

5. **Better Auth Practices**
   - Input validation & sanitization
   - Rate limiting on auth routes
   - Proper error handling (no sensitive leaks)
   - Secure environment variables for secrets

## Best Practices
- Use HTTPS only
- Keep JWT secret strong and private
- Short-lived access tokens
- Hash passwords with cost factor
- Return generic auth errors
- Follow least-privilege principle

## Example Structure
```js
// Signup
POST /auth/signup

// Signin
POST /auth/signin

// Protected Route
GET /profile
Authorization: Bearer <JWT_TOKEN>
