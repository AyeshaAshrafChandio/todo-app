# Quickstart Guide: Authentication & API Security

**Feature**: 002-auth-api-security
**Date**: 2026-02-04
**Prerequisites**: Spec 1 (Backend Core & Data Layer) must be implemented

This guide provides step-by-step instructions for setting up and testing the authentication and authorization system.

## Table of Contents

1. [Environment Setup](#environment-setup)
2. [Backend Setup](#backend-setup)
3. [Frontend Setup](#frontend-setup)
4. [Database Migration](#database-migration)
5. [Testing Authentication](#testing-authentication)
6. [Troubleshooting](#troubleshooting)

---

## Environment Setup

### 1. Generate Shared Secret

Generate a strong secret for JWT signing/verification:

```bash
# Generate a 32-character random secret
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2. Configure Environment Variables

Create or update `.env` file in the project root:

```bash
# Backend Configuration
DATABASE_URL=postgresql://user:password@host:5432/dbname  # Existing from Spec 1
BETTER_AUTH_SECRET=<your-generated-secret-here>           # NEW - Must be same for frontend and backend
JWT_ALGORITHM=HS256                                        # NEW
JWT_EXPIRATION_SECONDS=86400                               # NEW - 24 hours

# Frontend Configuration (if separate .env)
NEXT_PUBLIC_API_URL=http://localhost:8000                  # NEW
BETTER_AUTH_SECRET=<same-secret-as-backend>                # NEW - Must match backend
```

**Important**:
- The `BETTER_AUTH_SECRET` MUST be identical in both frontend and backend
- Never commit `.env` files to version control
- Use a different secret for production

### 3. Update `.env.example`

Document the new environment variables:

```bash
# Add to .env.example
BETTER_AUTH_SECRET=your-secret-here-minimum-32-characters
JWT_ALGORITHM=HS256
JWT_EXPIRATION_SECONDS=86400
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Backend Setup

### 1. Install Dependencies

Add authentication-related packages to `backend/requirements.txt`:

```txt
# Existing dependencies from Spec 1
fastapi
sqlmodel
uvicorn
python-dotenv
psycopg2-binary

# NEW - Authentication dependencies
PyJWT==2.8.0
bcrypt==4.1.2
```

Install dependencies:

```bash
cd backend
pip install -r requirements.txt
```

### 2. Verify Configuration

Check that `app/config.py` includes the new settings:

```python
# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Existing from Spec 1
    DATABASE_URL: str
    APP_NAME: str = "Todo Backend API"
    APP_VERSION: str = "2.0.0"

    # NEW - Authentication settings
    BETTER_AUTH_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_SECONDS: int = 86400

    class Config:
        env_file = ".env"

settings = Settings()
```

### 3. Run Database Migration

The User table and user_id column will be created automatically when the application starts:

```bash
cd backend
python -m app.main
```

Expected output:
```
Starting up: Initializing database...
Creating table: users
Altering table: tasks (adding user_id column)
Database initialized successfully
```

### 4. Verify Backend is Running

Test the health endpoint:

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected"
}
```

---

## Frontend Setup

### 1. Install Dependencies

Add Better Auth and related packages to `frontend/package.json`:

```bash
cd frontend
npm install better-auth@latest
npm install @tanstack/react-query  # For API state management
```

### 2. Configure Better Auth

Verify `lib/auth.ts` is configured correctly:

```typescript
// lib/auth.ts
import { betterAuth } from "better-auth"

export const auth = betterAuth({
  secret: process.env.BETTER_AUTH_SECRET!,
  session: {
    strategy: "jwt",
    expiresIn: 60 * 60 * 24, // 24 hours
    updateAge: 60 * 60,      // Refresh if older than 1 hour
  },
  jwt: {
    claims: {
      userId: "user.id",
      email: "user.email"
    }
  }
})

export type Session = typeof auth.$Infer.Session
```

### 3. Start Frontend Development Server

```bash
cd frontend
npm run dev
```

Expected output:
```
▲ Next.js 16.0.0
- Local:        http://localhost:3000
- Ready in 2.3s
```

---

## Database Migration

### Verify Database Schema

Connect to your Neon PostgreSQL database and verify the schema:

```sql
-- Check users table exists
SELECT table_name
FROM information_schema.tables
WHERE table_name = 'users';

-- Check tasks table has user_id column
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'tasks' AND column_name = 'user_id';

-- Expected result:
-- column_name | data_type | is_nullable
-- user_id     | varchar   | YES
```

### Handle Existing Tasks (Optional)

If you have existing tasks from Spec 1, they will have `user_id = NULL`. You can:

**Option A: Leave them as-is** (recommended)
- Existing tasks won't be visible to any user
- New tasks will be properly assigned

**Option B: Assign to a system user**
```sql
-- Create a system user
INSERT INTO users (id, email, password_hash, created_at, updated_at)
VALUES (
  'system-user-id',
  'system@todo.app',
  '$2b$12$...',  -- Dummy hash
  NOW(),
  NOW()
);

-- Assign legacy tasks to system user
UPDATE tasks
SET user_id = 'system-user-id'
WHERE user_id IS NULL;
```

---

## Testing Authentication

### 1. Test User Registration

```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123"
  }'
```

Expected response (201 Created):
```json
{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "test@example.com",
    "created_at": "2026-02-04T10:30:00Z"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_at": "2026-02-05T10:30:00Z"
}
```

### 2. Test User Login

```bash
curl -X POST http://localhost:8000/api/auth/signin \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123"
  }'
```

Expected response (200 OK):
```json
{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "test@example.com",
    "created_at": "2026-02-04T10:30:00Z"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_at": "2026-02-05T10:30:00Z"
}
```

### 3. Test Protected Endpoint (Create Task)

Save the token from step 1 or 2, then:

```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
USER_ID="550e8400-e29b-41d4-a716-446655440000"

curl -X POST http://localhost:8000/api/$USER_ID/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "title": "Buy groceries",
    "description": "Milk, eggs, bread"
  }'
```

Expected response (201 Created):
```json
{
  "id": 1,
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2026-02-04T10:30:00Z",
  "updated_at": "2026-02-04T10:30:00Z"
}
```

### 4. Test Unauthorized Access

Try accessing tasks without a token:

```bash
curl -X GET http://localhost:8000/api/$USER_ID/tasks
```

Expected response (401 Unauthorized):
```json
{
  "detail": "Authentication required. Please provide a valid token.",
  "error_code": "TOKEN_MISSING"
}
```

### 5. Test Cross-User Access

Create a second user and try to access the first user's tasks:

```bash
# Create second user
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user2@example.com",
    "password": "SecurePass456"
  }'

# Save the second user's token
TOKEN2="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Try to access first user's tasks with second user's token
curl -X GET http://localhost:8000/api/$USER_ID/tasks \
  -H "Authorization: Bearer $TOKEN2"
```

Expected response (403 Forbidden):
```json
{
  "detail": "Access denied. You can only access your own tasks."
}
```

---

## Troubleshooting

### Issue: "BETTER_AUTH_SECRET not found"

**Cause**: Environment variable not set or .env file not loaded

**Solution**:
1. Verify `.env` file exists in project root
2. Check that `BETTER_AUTH_SECRET` is defined in `.env`
3. Restart the backend server

### Issue: "Invalid token signature"

**Cause**: Frontend and backend using different secrets

**Solution**:
1. Verify `BETTER_AUTH_SECRET` is identical in both frontend and backend `.env` files
2. Restart both servers after updating

### Issue: "Token expired"

**Cause**: Token is older than 24 hours

**Solution**:
1. Log in again to get a fresh token
2. Better Auth should automatically refresh tokens on the frontend

### Issue: "Task not found" when accessing own task

**Cause**: Task's user_id doesn't match authenticated user

**Solution**:
1. Verify the task was created with the correct user_id
2. Check database: `SELECT * FROM tasks WHERE id = <task_id>;`
3. Ensure JWT token contains correct userId claim

### Issue: Database migration fails

**Cause**: Existing tasks table conflicts with new schema

**Solution**:
1. Backup your database first
2. Manually add user_id column:
   ```sql
   ALTER TABLE tasks ADD COLUMN user_id VARCHAR(36) NULL;
   ALTER TABLE tasks ADD CONSTRAINT fk_tasks_user_id
     FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
   CREATE INDEX idx_tasks_user_id ON tasks(user_id);
   ```

### Issue: "bcrypt not found" error

**Cause**: bcrypt package not installed

**Solution**:
```bash
pip install bcrypt==4.1.2
```

### Issue: CORS errors in browser

**Cause**: Frontend and backend on different origins

**Solution**:
1. Verify CORS is configured in `backend/app/main.py`:
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://localhost:3000"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

---

## Next Steps

After completing this setup:

1. ✅ Backend authentication endpoints are functional
2. ✅ Frontend can register and login users
3. ✅ JWT tokens are issued and verified
4. ✅ Task endpoints are protected
5. ✅ User data isolation is enforced

**Ready for**: Task breakdown (`/sp.tasks`) and implementation (`/sp.implement`)

---

## Security Checklist

Before deploying to production:

- [ ] Use strong, randomly generated `BETTER_AUTH_SECRET` (minimum 32 characters)
- [ ] Enable HTTPS for all API requests
- [ ] Set secure cookie flags (httpOnly, secure, sameSite)
- [ ] Implement rate limiting on auth endpoints
- [ ] Add logging for authentication failures
- [ ] Configure proper CORS origins (not wildcard)
- [ ] Use environment-specific secrets (dev, staging, prod)
- [ ] Enable database connection pooling
- [ ] Set up monitoring for failed auth attempts
- [ ] Document secret rotation procedure

---

## API Documentation

Once the backend is running, access interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

The documentation will show all endpoints with authentication requirements and example requests/responses.
