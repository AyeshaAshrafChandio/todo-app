# Quick Start Guide: MCP Backend Data & Dashboard

**Feature**: 008-mcp-backend-dashboard
**Date**: 2026-02-07
**Prerequisites**: Python 3.11+, Node.js 18+, Neon PostgreSQL database

## Overview

This guide walks you through setting up the MCP Backend Data & Dashboard feature, which includes:
- Database schema for AI chat (tasks, conversations, messages)
- Team collaboration tables (teams, team_members, task_shares)
- Dashboard API for task statistics
- Live dashboard UI with real-time updates

---

## Prerequisites

### Required Software
- **Python**: 3.11 or higher
- **Node.js**: 18 or higher
- **npm**: 9 or higher
- **Git**: For version control
- **Neon Account**: Serverless PostgreSQL database

### Required Environment
- **Backend**: FastAPI, SQLModel, Alembic
- **Frontend**: Next.js 14+, React 18+, TypeScript
- **Database**: Neon Serverless PostgreSQL (connection string required)

---

## Step 1: Database Setup

### 1.1 Verify Neon Connection

Check that your Neon database connection is configured:

```bash
# Backend .env file should contain:
DATABASE_URL=postgresql://user:password@host.neon.tech/dbname?sslmode=require
```

### 1.2 Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

**Required packages** (should be in requirements.txt):
- fastapi
- sqlmodel
- alembic
- asyncpg
- python-jose[cryptography]
- pydantic
- uvicorn

### 1.3 Run Database Migrations

```bash
cd backend

# Initialize Alembic (if not already done)
alembic init alembic

# Run migrations to create tables
alembic upgrade head
```

**Expected output**:
```
INFO  [alembic.runtime.migration] Running upgrade -> 001, create tasks table
INFO  [alembic.runtime.migration] Running upgrade 001 -> 002, create conversations table
INFO  [alembic.runtime.migration] Running upgrade 002 -> 003, create messages table
INFO  [alembic.runtime.migration] Running upgrade 003 -> 004, add indexes
INFO  [alembic.runtime.migration] Running upgrade 004 -> 005, create teams table
INFO  [alembic.runtime.migration] Running upgrade 005 -> 006, create team_members table
INFO  [alembic.runtime.migration] Running upgrade 006 -> 007, create task_shares table
INFO  [alembic.runtime.migration] Running upgrade 007 -> 008, add team indexes
```

### 1.4 Verify Tables Created

```bash
# Connect to Neon database and verify tables
psql $DATABASE_URL -c "\dt"
```

**Expected tables**:
- tasks
- conversations
- messages
- teams
- team_members
- task_shares
- users (existing)

---

## Step 2: Backend Setup

### 2.1 Configure Environment Variables

Create or update `backend/.env`:

```bash
# Database
DATABASE_URL=postgresql://user:password@host.neon.tech/dbname?sslmode=require

# Authentication
BETTER_AUTH_SECRET=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=60

# API Configuration
API_HOST=0.0.0.0
API_PORT=8001
CORS_ORIGINS=http://localhost:3000

# Feature Flags
ENABLE_WEBSOCKETS=false  # Set to true to enable WebSocket updates
CACHE_TTL_SECONDS=5      # Dashboard statistics cache duration
```

### 2.2 Start Backend Server

```bash
cd backend
uvicorn app.main:app --reload --port 8001
```

**Expected output**:
```
INFO:     Uvicorn running on http://127.0.0.1:8001 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 2.3 Verify Backend Health

```bash
curl http://localhost:8001/health
```

**Expected response**:
```json
{
  "status": "healthy",
  "database": "connected",
  "version": "1.0.0"
}
```

### 2.4 Test Dashboard API

```bash
# Get JWT token (login first)
TOKEN=$(curl -X POST http://localhost:8001/api/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password"}' \
  | jq -r '.access_token')

# Get dashboard statistics
curl http://localhost:8001/api/dashboard/statistics \
  -H "Authorization: Bearer $TOKEN"
```

**Expected response**:
```json
{
  "total_tasks": 0,
  "pending_tasks": 0,
  "completed_tasks": 0,
  "shared_tasks": 0
}
```

---

## Step 3: Frontend Setup

### 3.1 Install Frontend Dependencies

```bash
cd frontend
npm install
```

**New dependencies** (should be added to package.json):
- swr (for data fetching with polling)

```bash
npm install swr
```

### 3.2 Configure Environment Variables

Create or update `frontend/.env`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8001
```

**Important**: Delete `frontend/.env.local` if it exists (it overrides .env)

### 3.3 Start Frontend Server

```bash
cd frontend
npm run dev
```

**Expected output**:
```
  ▲ Next.js 14.x.x
  - Local:        http://localhost:3000
  - Network:      http://192.168.1.x:3000

 ✓ Ready in 2.5s
```

---

## Step 4: Access Dashboard

### 4.1 Login

1. Open browser: http://localhost:3000
2. Navigate to login page
3. Login with your credentials

### 4.2 Navigate to Dashboard

1. Click "Dashboard" in navigation menu
2. Or directly visit: http://localhost:3000/dashboard

### 4.3 Verify Dashboard Display

You should see:
- **Total Tasks**: Count of all your tasks
- **Pending Tasks**: Count of tasks with status 'pending'
- **Completed Tasks**: Count of tasks with status 'completed'
- **Shared Tasks**: Count of tasks shared with you

**Dashboard updates every 5 seconds automatically**

---

## Step 5: Testing the Dashboard

### 5.1 Create a Task

```bash
# Via API
curl -X POST http://localhost:8001/api/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test task","description":"Testing dashboard"}'
```

**Expected**: Dashboard updates within 5 seconds showing:
- Total Tasks: 1
- Pending Tasks: 1

### 5.2 Complete a Task

```bash
# Via API
curl -X PUT http://localhost:8001/api/tasks/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status":"completed"}'
```

**Expected**: Dashboard updates within 5 seconds showing:
- Total Tasks: 1
- Pending Tasks: 0
- Completed Tasks: 1

### 5.3 Delete a Task

```bash
# Via API
curl -X DELETE http://localhost:8001/api/tasks/1 \
  -H "Authorization: Bearer $TOKEN"
```

**Expected**: Dashboard updates within 5 seconds showing:
- Total Tasks: 0
- Completed Tasks: 0

---

## Step 6: Enable WebSocket Updates (Optional)

### 6.1 Enable WebSocket in Backend

Edit `backend/.env`:
```bash
ENABLE_WEBSOCKETS=true
```

Restart backend server.

### 6.2 Verify WebSocket Connection

Open browser DevTools → Network tab → WS filter

You should see:
- WebSocket connection to `ws://localhost:8001/api/ws`
- Status: 101 Switching Protocols
- Connection: Upgrade

### 6.3 Test Real-Time Updates

1. Open dashboard in browser
2. Create a task via API (see Step 5.1)
3. Dashboard should update **instantly** (< 1 second)

---

## Troubleshooting

### Issue: Database connection failed

**Symptoms**: Backend fails to start with database error

**Solution**:
1. Verify DATABASE_URL in backend/.env
2. Check Neon database is running
3. Verify SSL mode is set to 'require'
4. Test connection: `psql $DATABASE_URL -c "SELECT 1"`

---

### Issue: Migrations fail

**Symptoms**: `alembic upgrade head` returns errors

**Solution**:
1. Check if tables already exist: `psql $DATABASE_URL -c "\dt"`
2. If tables exist, mark migrations as applied: `alembic stamp head`
3. If migrations are out of sync, reset: `alembic downgrade base && alembic upgrade head`
4. Check migration files for syntax errors

---

### Issue: Dashboard shows 401 Unauthorized

**Symptoms**: Dashboard API returns 401 error

**Solution**:
1. Verify you're logged in
2. Check JWT token in browser localStorage
3. Verify BETTER_AUTH_SECRET matches between frontend and backend
4. Try logging out and back in
5. Check backend logs for authentication errors

---

### Issue: Dashboard not updating

**Symptoms**: Statistics don't change after creating/updating tasks

**Solution**:
1. Check browser console for errors
2. Verify polling is working (Network tab → XHR filter)
3. Check backend logs for API errors
4. Verify cache TTL is not too long (should be 5 seconds)
5. Try hard refresh (Ctrl+Shift+R)

---

### Issue: WebSocket connection fails

**Symptoms**: WebSocket shows "Disconnected" or fails to connect

**Solution**:
1. Verify ENABLE_WEBSOCKETS=true in backend/.env
2. Check backend logs for WebSocket errors
3. Verify JWT token is valid
4. Check CORS configuration allows WebSocket
5. Try disabling browser extensions (ad blockers)
6. Fall back to polling if WebSocket unavailable

---

### Issue: Frontend shows blank page

**Symptoms**: Dashboard page is blank or shows loading forever

**Solution**:
1. Check browser console for errors
2. Verify API_URL in frontend/.env
3. Delete frontend/.env.local if it exists
4. Verify backend is running on correct port
5. Check CORS configuration in backend
6. Try clearing browser cache

---

## Development Workflow

### Running Tests

**Backend tests**:
```bash
cd backend
pytest tests/test_dashboard_api.py -v
pytest tests/test_data_isolation.py -v
pytest tests/test_security.py -v
```

**Frontend tests**:
```bash
cd frontend
npm test tests/dashboard.spec.ts
```

### Database Seeding

Create test data for development:

```bash
cd backend
python -m app.database.seed
```

This creates:
- 10 sample tasks (5 pending, 5 completed)
- 2 sample conversations with messages
- 1 sample team with members

### Viewing Logs

**Backend logs**:
```bash
# Backend terminal shows all API requests and errors
# Look for lines starting with INFO, WARNING, ERROR
```

**Frontend logs**:
```bash
# Browser DevTools → Console tab
# Look for API errors, WebSocket status, component errors
```

### Database Inspection

**View all tasks**:
```bash
psql $DATABASE_URL -c "SELECT id, user_id, title, status FROM tasks;"
```

**View statistics manually**:
```bash
psql $DATABASE_URL -c "
SELECT
  COUNT(*) as total,
  COUNT(*) FILTER (WHERE status = 'pending') as pending,
  COUNT(*) FILTER (WHERE status = 'completed') as completed
FROM tasks
WHERE user_id = 1;
"
```

---

## Production Deployment

### Backend Deployment

1. Set production environment variables
2. Run migrations: `alembic upgrade head`
3. Start with production ASGI server: `gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker`
4. Configure reverse proxy (nginx) for WebSocket support
5. Enable HTTPS (required for production)

### Frontend Deployment

1. Build production bundle: `npm run build`
2. Deploy to Vercel or similar platform
3. Set NEXT_PUBLIC_API_URL to production backend URL
4. Verify CORS allows production frontend origin

### Database Optimization

1. Monitor query performance with EXPLAIN ANALYZE
2. Add additional indexes if needed
3. Set up connection pooling (Neon handles this)
4. Configure database backups
5. Monitor database metrics (connections, query time)

---

## Next Steps

1. ✅ Database schema created
2. ✅ Dashboard API working
3. ✅ Dashboard UI displaying statistics
4. ⏳ Implement team collaboration features (Phase 4)
5. ⏳ Add WebSocket real-time updates (Phase 7)
6. ⏳ Implement security hardening (Phase 8)
7. ⏳ Performance optimization (Phase 9)

---

## Support

**Documentation**:
- spec.md - Feature specification
- plan.md - Implementation plan
- data-model.md - Database schema
- contracts/ - API contracts

**Common Commands**:
```bash
# Start backend
cd backend && uvicorn app.main:app --reload --port 8001

# Start frontend
cd frontend && npm run dev

# Run migrations
cd backend && alembic upgrade head

# Run tests
cd backend && pytest -v
cd frontend && npm test

# View logs
# Backend: Check terminal output
# Frontend: Browser DevTools → Console
```

---

**Last Updated**: 2026-02-07
**Status**: Ready for implementation
