# Manual Testing Verification Guide
## MCP Backend Data & Dashboard Feature

**Date**: 2026-02-07
**Feature**: 008-mcp-backend-dashboard
**Purpose**: Verify all implemented features work correctly before deployment

---

## Pre-Testing Setup

### 1. Verify Database Migrations

```bash
cd C:\Users\Ali Haider\hakathon2\phase2\backend

# Check current migration status
alembic current

# Apply all migrations if needed
alembic upgrade head

# Verify tables exist
python -c "
from app.database.connection import engine
from sqlalchemy import inspect
inspector = inspect(engine)
tables = inspector.get_table_names()
print('Tables in database:')
for table in sorted(tables):
    print(f'  - {table}')
"
```

**Expected Output**:
```
Tables in database:
  - alembic_version
  - conversations
  - messages
  - task_shares
  - tasks
  - team_members
  - teams
  - users
```

### 2. Start Backend Server

```bash
cd C:\Users\Ali Haider\hakathon2\phase2\backend

# Start with reload for development
uvicorn app.main:app --reload --port 8001
```

**Expected Output**:
```
INFO:     Uvicorn running on http://127.0.0.1:8001 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**✅ Checkpoint**: Backend should start without errors

### 3. Verify Backend Health

Open a new terminal:

```bash
curl http://localhost:8001/health
```

**Expected Response**:
```json
{
  "status": "healthy",
  "database": "connected",
  "version": "1.0.0"
}
```

**✅ Checkpoint**: Health check returns 200 OK

### 4. Check API Documentation

Open browser: http://localhost:8001/docs

**Expected**: Swagger UI should load showing all API endpoints

**✅ Checkpoint**: API docs accessible

### 5. Start Frontend Server

Open a new terminal:

```bash
cd C:\Users\Ali Haider\hakathon2\phase2\frontend

# Install dependencies if needed
npm install

# Start development server
npm run dev
```

**Expected Output**:
```
  ▲ Next.js 14.x.x
  - Local:        http://localhost:3000
  - Network:      http://192.168.x.x:3000

 ✓ Ready in 2.5s
```

**✅ Checkpoint**: Frontend starts without errors

---

## Test Suite 1: Authentication & Basic Access

### Test 1.1: User Registration

1. Open browser: http://localhost:3000
2. Navigate to signup/register page
3. Create a test account:
   - Email: `test1@example.com`
   - Password: `TestPass123!`
   - Name: `Test User 1`

**Expected**:
- ✅ Registration succeeds
- ✅ Redirected to dashboard or login page
- ✅ No errors in browser console

### Test 1.2: User Login

1. Navigate to login page
2. Login with credentials from Test 1.1

**Expected**:
- ✅ Login succeeds
- ✅ JWT token stored in localStorage
- ✅ Redirected to dashboard

**Verify JWT Token**:
- Open browser DevTools (F12) → Application → Local Storage
- Look for token or auth-related keys
- Token should be present

### Test 1.3: Dashboard Access

1. Navigate to: http://localhost:3000/dashboard

**Expected**:
- ✅ Dashboard page loads
- ✅ Statistics cards visible (Total, Pending, Completed, Shared)
- ✅ All counts show 0 (no tasks yet)
- ✅ Connection status indicator shows "Connected" (green)

**✅ Checkpoint**: Authentication and dashboard access working

---

## Test Suite 2: Dashboard Statistics

### Test 2.1: Create First Task

1. Navigate to tasks page (or use API)
2. Create a new task:
   - Title: "Test Task 1"
   - Description: "Testing dashboard updates"

**Using API (alternative)**:
```bash
# Get JWT token from browser localStorage first
TOKEN="your-jwt-token-here"

curl -X POST http://localhost:8001/api/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Task 1","description":"Testing dashboard updates"}'
```

**Expected**:
- ✅ Task created successfully
- ✅ Dashboard updates within 1 second (WebSocket) or 5 seconds (polling)
- ✅ Total Tasks: 1
- ✅ Pending Tasks: 1
- ✅ Completed Tasks: 0

**Check Browser Console**:
- Should see: `[WebSocket] Received event: task_created`

### Test 2.2: Create Multiple Tasks

Create 4 more tasks with different titles:
- "Test Task 2"
- "Test Task 3"
- "Test Task 4"
- "Test Task 5"

**Expected**:
- ✅ Dashboard updates after each task
- ✅ Total Tasks: 5
- ✅ Pending Tasks: 5
- ✅ Completed Tasks: 0

### Test 2.3: Complete Tasks

Mark 2 tasks as completed:

```bash
# Complete Task 1
curl -X PUT http://localhost:8001/api/tasks/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status":"completed"}'

# Complete Task 2
curl -X PUT http://localhost:8001/api/tasks/2 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status":"completed"}'
```

**Expected**:
- ✅ Dashboard updates instantly
- ✅ Total Tasks: 5
- ✅ Pending Tasks: 3
- ✅ Completed Tasks: 2

**Check Browser Console**:
- Should see: `[WebSocket] Received event: task_completed` (twice)

### Test 2.4: Delete Task

Delete one task:

```bash
curl -X DELETE http://localhost:8001/api/tasks/3 \
  -H "Authorization: Bearer $TOKEN"
```

**Expected**:
- ✅ Dashboard updates instantly
- ✅ Total Tasks: 4
- ✅ Pending Tasks: 2
- ✅ Completed Tasks: 2

**✅ Checkpoint**: Dashboard statistics updating correctly

---

## Test Suite 3: Real-Time Updates (WebSocket)

### Test 3.1: Verify WebSocket Connection

1. Open dashboard in browser
2. Open DevTools (F12) → Console tab

**Expected Console Logs**:
```
[WebSocket] Connecting to: ws://localhost:8001/api/ws?token=...
[WebSocket] Connected successfully
[WebSocket] Received event: connection_ack
```

**Check Network Tab**:
- Filter by "WS" (WebSocket)
- Should see connection to `/api/ws`
- Status: 101 Switching Protocols

### Test 3.2: Multi-Window Real-Time Test

1. Open dashboard in **two browser windows** side-by-side
2. In Window 1: Create a new task
3. Watch Window 2: Dashboard should update **instantly** (< 1 second)

**Expected**:
- ✅ Window 2 updates without refresh
- ✅ Both windows show same statistics
- ✅ Update happens in < 1 second

### Test 3.3: WebSocket Reconnection

1. With dashboard open, stop the backend server (Ctrl+C in backend terminal)
2. Observe dashboard:
   - Connection status should change to "Disconnected" (red)
   - Console should show reconnection attempts

3. Restart backend server:
   ```bash
   uvicorn app.main:app --reload --port 8001
   ```

4. Observe dashboard:
   - Connection status should change to "Connecting..." (yellow)
   - Then "Connected" (green)
   - Console should show successful reconnection

**Expected**:
- ✅ Automatic reconnection works
- ✅ Connection status indicator updates correctly
- ✅ Dashboard syncs after reconnection

**✅ Checkpoint**: WebSocket real-time updates working

---

## Test Suite 4: Team Collaboration

### Test 4.1: Create Second User

1. Logout from current session
2. Register a second user:
   - Email: `test2@example.com`
   - Password: `TestPass123!`
   - Name: `Test User 2`

### Test 4.2: Create Team

Using User 1's token:

```bash
TOKEN1="user1-jwt-token"

curl -X POST http://localhost:8001/api/teams \
  -H "Authorization: Bearer $TOKEN1" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Team","description":"Testing team collaboration"}'
```

**Expected**:
- ✅ Team created successfully
- ✅ User 1 is automatically added as owner

### Test 4.3: Add Team Member

Add User 2 to the team:

```bash
# Get team ID from previous response (e.g., team_id=1)
curl -X POST http://localhost:8001/api/teams/1/members \
  -H "Authorization: Bearer $TOKEN1" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test2@example.com","role":"member"}'
```

**Expected**:
- ✅ User 2 added to team
- ✅ User 2 can now see team tasks

### Test 4.4: Share Task

Share a task with User 2:

```bash
curl -X POST http://localhost:8001/api/tasks/4/share \
  -H "Authorization: Bearer $TOKEN1" \
  -H "Content-Type: application/json" \
  -d '{"shared_with_user_id":"test2-user-id","permission":"view"}'
```

**Expected**:
- ✅ Task shared successfully
- ✅ User 2 can see shared task
- ✅ Dashboard shows shared task count

### Test 4.5: Verify Data Isolation

1. Login as User 2
2. Navigate to dashboard

**Expected**:
- ✅ User 2 sees only their own tasks
- ✅ User 2 sees tasks shared with them
- ✅ User 2 does NOT see User 1's private tasks
- ✅ Shared Tasks count > 0

**✅ Checkpoint**: Team collaboration and data isolation working

---

## Test Suite 5: Security & Authorization

### Test 5.1: Unauthorized Access

Try accessing API without token:

```bash
curl http://localhost:8001/api/dashboard/statistics
```

**Expected**:
- ✅ Returns 401 Unauthorized
- ✅ Error message: "Invalid or missing authentication token"

### Test 5.2: Invalid Token

Try with invalid token:

```bash
curl http://localhost:8001/api/dashboard/statistics \
  -H "Authorization: Bearer invalid-token-here"
```

**Expected**:
- ✅ Returns 401 Unauthorized
- ✅ Token validation fails

### Test 5.3: Cross-User Access

Try to access User 1's task as User 2:

```bash
TOKEN2="user2-jwt-token"

# Try to get User 1's task (task_id=1)
curl http://localhost:8001/api/tasks/1 \
  -H "Authorization: Bearer $TOKEN2"
```

**Expected**:
- ✅ Returns 404 Not Found (not 403, to prevent information leakage)
- ✅ User 2 cannot access User 1's private tasks

**✅ Checkpoint**: Security and authorization working correctly

---

## Test Suite 6: Performance & Optimization

### Test 6.1: Dashboard Load Time

1. Open dashboard with DevTools Network tab open
2. Refresh page (Ctrl+R)
3. Check timing:
   - Look for `/api/dashboard/statistics` request
   - Check response time

**Expected**:
- ✅ API response time < 100ms
- ✅ Page loads in < 2 seconds
- ✅ No slow queries in backend logs

### Test 6.2: Query Performance

Check backend logs for slow queries:

```bash
# Backend terminal should show query times
# Look for lines like: "Query executed in 45ms"
```

**Expected**:
- ✅ Dashboard queries < 50ms
- ✅ Task queries < 50ms
- ✅ No queries > 100ms

### Test 6.3: Concurrent Users

Open dashboard in 3-4 browser tabs simultaneously:

**Expected**:
- ✅ All tabs load correctly
- ✅ All tabs receive real-time updates
- ✅ No performance degradation
- ✅ Backend handles concurrent connections

**✅ Checkpoint**: Performance meets requirements

---

## Test Suite 7: Responsive Design

### Test 7.1: Mobile View

1. Open dashboard in browser
2. Open DevTools (F12) → Toggle device toolbar (Ctrl+Shift+M)
3. Select "iPhone 12 Pro" or similar mobile device

**Expected**:
- ✅ Dashboard layout adapts to mobile (1 column)
- ✅ Statistics cards stack vertically
- ✅ All text readable
- ✅ Touch targets appropriately sized

### Test 7.2: Tablet View

Select "iPad" or similar tablet device:

**Expected**:
- ✅ Dashboard layout shows 2 columns
- ✅ Cards arranged in 2x2 grid
- ✅ Responsive to orientation changes

### Test 7.3: Desktop View

Return to desktop view:

**Expected**:
- ✅ Dashboard layout shows 4 columns
- ✅ All cards visible in single row
- ✅ Optimal use of screen space

**✅ Checkpoint**: Responsive design working across devices

---

## Test Suite 8: Error Handling

### Test 8.1: Network Error

1. With dashboard open, disconnect from internet (or block backend port)
2. Observe dashboard behavior

**Expected**:
- ✅ Error message displayed
- ✅ Retry button available
- ✅ Connection status shows "Disconnected"
- ✅ No crashes or blank screens

### Test 8.2: Database Connection Error

1. Stop the database (or change DATABASE_URL to invalid)
2. Try to access dashboard

**Expected**:
- ✅ Graceful error handling
- ✅ User-friendly error message
- ✅ Backend doesn't crash
- ✅ Retry logic attempts reconnection

### Test 8.3: Invalid Input

Try creating task with invalid data:

```bash
curl -X POST http://localhost:8001/api/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"","description":"Empty title test"}'
```

**Expected**:
- ✅ Returns 400 Bad Request
- ✅ Clear validation error message
- ✅ Specifies which field is invalid

**✅ Checkpoint**: Error handling working correctly

---

## Final Verification Checklist

### Backend ✅
- [ ] Backend starts without errors
- [ ] Health endpoint returns 200 OK
- [ ] All 8 tables exist in database
- [ ] API documentation accessible
- [ ] WebSocket endpoint working
- [ ] No errors in backend logs

### Frontend ✅
- [ ] Frontend starts without errors
- [ ] Dashboard page loads correctly
- [ ] Statistics display accurately
- [ ] Real-time updates working (< 1s)
- [ ] Connection status indicator working
- [ ] No errors in browser console

### Features ✅
- [ ] User authentication working
- [ ] Task CRUD operations working
- [ ] Dashboard statistics accurate
- [ ] WebSocket real-time updates working
- [ ] Team collaboration working
- [ ] Task sharing working
- [ ] Data isolation enforced

### Security ✅
- [ ] JWT authentication required
- [ ] Unauthorized access blocked (401)
- [ ] Cross-user access prevented (404)
- [ ] Token validation working
- [ ] Audit logging operational

### Performance ✅
- [ ] Dashboard loads in < 2s
- [ ] API responses < 100ms
- [ ] Queries < 50ms
- [ ] No slow queries (> 100ms)
- [ ] Concurrent users supported

### UX ✅
- [ ] Responsive design (mobile/tablet/desktop)
- [ ] Loading states visible
- [ ] Error messages clear
- [ ] Retry functionality working
- [ ] Connection status visible

---

## Troubleshooting Common Issues

### Issue: Backend won't start

**Symptoms**: Error on `uvicorn app.main:app`

**Solutions**:
1. Check DATABASE_URL is correct in `.env`
2. Verify all dependencies installed: `pip install -r requirements.txt`
3. Check port 8001 is not in use: `netstat -ano | findstr :8001`
4. Check Python version: `python --version` (should be 3.11+)

### Issue: Frontend won't start

**Symptoms**: Error on `npm run dev`

**Solutions**:
1. Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`
2. Check Node version: `node --version` (should be 18+)
3. Check port 3000 is not in use
4. Clear Next.js cache: `rm -rf .next`

### Issue: Dashboard shows 0 for all statistics

**Symptoms**: All counts are 0 even after creating tasks

**Solutions**:
1. Verify you're logged in (check JWT token in localStorage)
2. Check backend logs for errors
3. Verify tasks were created: `curl http://localhost:8001/api/tasks -H "Authorization: Bearer $TOKEN"`
4. Check database: Tasks should exist in `tasks` table

### Issue: WebSocket not connecting

**Symptoms**: Connection status shows "Disconnected" or "Connecting..."

**Solutions**:
1. Check backend is running on port 8001
2. Verify WebSocket endpoint: `ws://localhost:8001/api/ws`
3. Check browser console for WebSocket errors
4. Verify JWT token is valid
5. Check CORS configuration in backend

### Issue: Real-time updates not working

**Symptoms**: Dashboard doesn't update when tasks change

**Solutions**:
1. Check WebSocket connection status (should be green "Connected")
2. Verify event emitters are working (check backend logs)
3. Test with two browser windows side-by-side
4. Check browser console for WebSocket events
5. Fall back to polling if WebSocket unavailable

---

## Test Results Template

Use this template to record your test results:

```
# Manual Testing Results
Date: 2026-02-07
Tester: [Your Name]
Feature: MCP Backend Data & Dashboard

## Test Suite 1: Authentication & Basic Access
- Test 1.1: User Registration - [ ] PASS / [ ] FAIL
- Test 1.2: User Login - [ ] PASS / [ ] FAIL
- Test 1.3: Dashboard Access - [ ] PASS / [ ] FAIL

## Test Suite 2: Dashboard Statistics
- Test 2.1: Create First Task - [ ] PASS / [ ] FAIL
- Test 2.2: Create Multiple Tasks - [ ] PASS / [ ] FAIL
- Test 2.3: Complete Tasks - [ ] PASS / [ ] FAIL
- Test 2.4: Delete Task - [ ] PASS / [ ] FAIL

## Test Suite 3: Real-Time Updates
- Test 3.1: WebSocket Connection - [ ] PASS / [ ] FAIL
- Test 3.2: Multi-Window Test - [ ] PASS / [ ] FAIL
- Test 3.3: Reconnection - [ ] PASS / [ ] FAIL

## Test Suite 4: Team Collaboration
- Test 4.1: Create Second User - [ ] PASS / [ ] FAIL
- Test 4.2: Create Team - [ ] PASS / [ ] FAIL
- Test 4.3: Add Team Member - [ ] PASS / [ ] FAIL
- Test 4.4: Share Task - [ ] PASS / [ ] FAIL
- Test 4.5: Data Isolation - [ ] PASS / [ ] FAIL

## Test Suite 5: Security
- Test 5.1: Unauthorized Access - [ ] PASS / [ ] FAIL
- Test 5.2: Invalid Token - [ ] PASS / [ ] FAIL
- Test 5.3: Cross-User Access - [ ] PASS / [ ] FAIL

## Test Suite 6: Performance
- Test 6.1: Dashboard Load Time - [ ] PASS / [ ] FAIL
- Test 6.2: Query Performance - [ ] PASS / [ ] FAIL
- Test 6.3: Concurrent Users - [ ] PASS / [ ] FAIL

## Test Suite 7: Responsive Design
- Test 7.1: Mobile View - [ ] PASS / [ ] FAIL
- Test 7.2: Tablet View - [ ] PASS / [ ] FAIL
- Test 7.3: Desktop View - [ ] PASS / [ ] FAIL

## Test Suite 8: Error Handling
- Test 8.1: Network Error - [ ] PASS / [ ] FAIL
- Test 8.2: Database Error - [ ] PASS / [ ] FAIL
- Test 8.3: Invalid Input - [ ] PASS / [ ] FAIL

## Overall Result
- Total Tests: 26
- Passed: __
- Failed: __
- Pass Rate: __%

## Issues Found
1. [Issue description]
2. [Issue description]

## Notes
[Any additional observations]
```

---

## Next Steps After Testing

### If All Tests Pass ✅
1. Create pull request for code review
2. Deploy to staging environment
3. Conduct user acceptance testing
4. Deploy to production

### If Tests Fail ❌
1. Document failing tests
2. Review error messages and logs
3. Fix issues
4. Re-run tests
5. Repeat until all tests pass

---

**Good luck with testing! Let me know if you encounter any issues.**
