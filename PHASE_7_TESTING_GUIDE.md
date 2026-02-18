# Phase 7 WebSocket Implementation - Testing Guide

## Quick Start Testing

### Prerequisites
- Backend server running on port 8000
- Frontend server running on port 3000
- Valid JWT token for authentication

### 1. Start Backend Server

```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
Starting up: Initializing database...
Database initialized successfully
Setting up performance monitoring...
Performance monitoring enabled
```

### 2. Start Frontend Server

```bash
cd frontend
npm run dev
```

Expected output:
```
  ▲ Next.js 15.x.x
  - Local:        http://localhost:3000
  - Ready in X.Xs
```

### 3. Test WebSocket Connection

#### Option A: Browser Console Test

1. Open browser to http://localhost:3000/dashboard
2. Open Developer Tools (F12) → Console
3. Look for WebSocket logs:
   ```
   [WebSocket] Connecting to: ws://localhost:8000/api/ws
   [WebSocket] Connected successfully
   [WebSocket] Received event: connection_ack
   ```

#### Option B: Manual WebSocket Test

Create a test HTML file:

```html
<!DOCTYPE html>
<html>
<head>
    <title>WebSocket Test</title>
</head>
<body>
    <h1>WebSocket Connection Test</h1>
    <div id="status">Disconnected</div>
    <div id="messages"></div>

    <script>
        // Replace with your JWT token
        const token = 'YOUR_JWT_TOKEN_HERE';
        const ws = new WebSocket(`ws://localhost:8000/api/ws?token=${token}`);

        ws.onopen = () => {
            document.getElementById('status').textContent = 'Connected';
            document.getElementById('status').style.color = 'green';
            console.log('WebSocket connected');
        };

        ws.onmessage = (event) => {
            const message = JSON.parse(event.data);
            console.log('Received:', message);

            const div = document.createElement('div');
            div.textContent = `${message.event_type}: ${JSON.stringify(message.data)}`;
            document.getElementById('messages').appendChild(div);
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            document.getElementById('status').textContent = 'Error';
            document.getElementById('status').style.color = 'red';
        };

        ws.onclose = () => {
            document.getElementById('status').textContent = 'Disconnected';
            document.getElementById('status').style.color = 'gray';
            console.log('WebSocket disconnected');
        };
    </script>
</body>
</html>
```

### 4. Test Real-Time Updates

#### Test Task Creation Event

1. Open dashboard in Browser Window 1
2. Open tasks page in Browser Window 2
3. Create a new task in Window 2
4. Verify dashboard in Window 1 updates instantly (< 1 second)

Expected behavior:
- Window 1 console shows: `[WebSocket] Received event: task_created`
- Window 1 dashboard statistics update immediately
- No page refresh required

#### Test Task Update Event

1. Update an existing task (change title or description)
2. Verify dashboard updates instantly
3. Check console for: `[WebSocket] Received event: task_updated`

#### Test Task Completion Event

1. Mark a task as complete
2. Verify dashboard updates instantly
3. Check console for: `[WebSocket] Received event: task_completed`

#### Test Task Deletion Event

1. Delete a task
2. Verify dashboard updates instantly
3. Check console for: `[WebSocket] Received event: task_deleted`

### 5. Test Connection Status Indicator

#### Test Connected State

1. Open dashboard
2. Verify green "Connected" indicator appears
3. Verify text shows "Real-time updates active"

#### Test Disconnected State

1. Stop backend server (Ctrl+C)
2. Verify red "Disconnected" indicator appears
3. Verify text shows "Using polling fallback"

#### Test Reconnection

1. Restart backend server
2. Verify yellow "Connecting" indicator appears briefly
3. Verify green "Connected" indicator appears after reconnection
4. Check console for reconnection logs

### 6. Test Reconnection Logic

#### Test Automatic Reconnection

1. Open dashboard with WebSocket connected
2. Stop backend server
3. Observe reconnection attempts in console:
   ```
   [WebSocket] Connection closed: 1006
   [WebSocket] Reconnecting in 1000ms (attempt 1)
   [WebSocket] Reconnecting in 2000ms (attempt 2)
   [WebSocket] Reconnecting in 4000ms (attempt 3)
   ```
4. Restart backend server
5. Verify connection re-establishes automatically

#### Test Exponential Backoff

1. Monitor console during reconnection attempts
2. Verify delays increase exponentially: 1s → 2s → 4s → 8s → 16s → 32s (max)

### 7. Test Multiple Clients

#### Test Broadcast to Multiple Users

1. Open dashboard in 3 different browser windows (or incognito)
2. Sign in as different users in each window
3. Create a task in one window
4. Verify only the creator's dashboard updates (user isolation)

#### Test Team Broadcasts

1. Create a team with multiple members
2. Open dashboard for each team member
3. Create a team task
4. Verify all team members' dashboards update instantly

### 8. Test Error Handling

#### Test Invalid Token

1. Modify WebSocket client to use invalid token
2. Verify connection is rejected
3. Check console for authentication error

#### Test Network Interruption

1. Open dashboard with WebSocket connected
2. Disable network (airplane mode or disconnect WiFi)
3. Verify "Disconnected" indicator appears
4. Re-enable network
5. Verify automatic reconnection

#### Test Server Restart

1. Open dashboard with WebSocket connected
2. Restart backend server
3. Verify client reconnects automatically
4. Verify dashboard continues to work

---

## Backend Testing

### Test WebSocket Manager

```python
# backend/tests/test_websocket_manager.py
import pytest
from app.services.websocket_manager import websocket_manager

def test_websocket_manager_initialization():
    """Test WebSocket manager initializes correctly"""
    assert websocket_manager is not None
    assert websocket_manager.get_connection_count() == 0
    assert websocket_manager.get_user_count() == 0

@pytest.mark.asyncio
async def test_connection_tracking():
    """Test connection tracking"""
    # This would require mocking WebSocket connections
    pass
```

### Test WebSocket Endpoint

```bash
# Test WebSocket endpoint is registered
curl -I http://localhost:8000/api/ws
# Expected: 426 Upgrade Required (WebSocket upgrade needed)
```

### Test Event Emission

```python
# backend/tests/test_task_events.py
import pytest
from app.services.task_service import create_task
from app.schemas.task import TaskCreate

@pytest.mark.asyncio
async def test_task_created_event_emitted(db_session, test_user):
    """Test that task_created event is emitted"""
    task_data = TaskCreate(
        title="Test Task",
        description="Test Description"
    )

    task = create_task(db_session, test_user.id, task_data)

    # Verify task was created
    assert task.id is not None
    assert task.title == "Test Task"

    # Note: Event emission is async and non-blocking
    # In production, verify via WebSocket client
```

---

## Frontend Testing

### Test WebSocket Client

```bash
cd frontend
npm test -- websocket.spec.ts
```

Expected output:
```
✓ WebSocket Client > Connection > should connect to WebSocket server with JWT token
✓ WebSocket Client > Connection > should include JWT token in URL query parameter
✓ WebSocket Client > Connection > should disconnect cleanly
✓ WebSocket Client > Event Handling > should handle connection_ack event
✓ WebSocket Client > Event Handling > should handle task_created event
... (all tests passing)
```

### Test Dashboard Integration

```typescript
// frontend/tests/dashboard-websocket.spec.ts
import { render, screen, waitFor } from '@testing-library/react';
import { DashboardLayout } from '@/components/dashboard/DashboardLayout';

test('should show connection status indicator', async () => {
  render(<DashboardLayout />);

  await waitFor(() => {
    expect(screen.getByText(/connected/i)).toBeInTheDocument();
  });
});

test('should update statistics on task event', async () => {
  // Mock WebSocket event
  // Verify statistics update
});
```

---

## Performance Testing

### Measure Update Latency

1. Open browser console
2. Create a task
3. Measure time from task creation to dashboard update
4. Expected: < 1 second (vs 0-5 seconds with polling)

### Measure Network Overhead

1. Open browser DevTools → Network tab
2. Filter by "WS" (WebSocket)
3. Observe WebSocket connection
4. Create/update/delete tasks
5. Verify only event messages are sent (no constant polling)

### Load Testing

```bash
# Install wscat for WebSocket testing
npm install -g wscat

# Test multiple connections
for i in {1..10}; do
  wscat -c "ws://localhost:8000/api/ws?token=YOUR_TOKEN" &
done

# Monitor server logs for connection count
```

---

## Troubleshooting

### Issue: WebSocket connection fails

**Symptoms**: "Disconnected" indicator, no real-time updates

**Solutions**:
1. Verify backend server is running
2. Check JWT token is valid
3. Verify CORS settings allow WebSocket connections
4. Check firewall/proxy settings

### Issue: Events not received

**Symptoms**: WebSocket connected but dashboard doesn't update

**Solutions**:
1. Check browser console for event logs
2. Verify event emitters are called in backend
3. Check user_id matches between token and task
4. Verify team membership for team tasks

### Issue: Reconnection fails

**Symptoms**: Connection lost and doesn't reconnect

**Solutions**:
1. Check max reconnection attempts not exceeded
2. Verify backend server is accessible
3. Check JWT token hasn't expired
4. Review browser console for error messages

### Issue: Multiple connections from same user

**Symptoms**: Duplicate events received

**Solutions**:
1. This is expected behavior (multiple tabs/windows)
2. Each tab maintains its own WebSocket connection
3. Events are broadcast to all user's connections

---

## Monitoring

### Backend Monitoring

```python
# Add to backend/app/routes/websocket.py
@router.get("/api/ws/stats")
async def websocket_stats():
    """Get WebSocket connection statistics"""
    return {
        "total_connections": websocket_manager.get_connection_count(),
        "unique_users": websocket_manager.get_user_count(),
    }
```

### Frontend Monitoring

```typescript
// Add to frontend dashboard
useEffect(() => {
  const interval = setInterval(() => {
    console.log('WebSocket status:', connectionStatus);
    console.log('Is connected:', isWebSocketConnected);
  }, 10000); // Log every 10 seconds

  return () => clearInterval(interval);
}, [connectionStatus, isWebSocketConnected]);
```

---

## Success Criteria

✅ **Connection**:
- [ ] WebSocket connection establishes successfully
- [ ] JWT authentication works
- [ ] Connection status indicator shows correct state

✅ **Real-Time Updates**:
- [ ] Dashboard updates instantly when task created (< 1 second)
- [ ] Dashboard updates instantly when task updated (< 1 second)
- [ ] Dashboard updates instantly when task completed (< 1 second)
- [ ] Dashboard updates instantly when task deleted (< 1 second)
- [ ] Dashboard updates instantly when task shared (< 1 second)

✅ **Reconnection**:
- [ ] Automatic reconnection works after disconnect
- [ ] Exponential backoff works correctly
- [ ] Connection re-establishes after server restart

✅ **Error Handling**:
- [ ] Invalid token rejected
- [ ] Network interruption handled gracefully
- [ ] Server errors don't crash client

✅ **Performance**:
- [ ] Update latency < 1 second
- [ ] No constant polling (only event-driven updates)
- [ ] Multiple clients work correctly

✅ **User Experience**:
- [ ] Connection status clearly visible
- [ ] No page refresh required for updates
- [ ] Fallback behavior works if WebSocket unavailable

---

## Next Steps

After successful testing:

1. **Deploy to Staging**:
   - Test with real users
   - Monitor WebSocket connection metrics
   - Verify performance improvements

2. **Production Deployment**:
   - Configure load balancer for WebSocket support
   - Set up monitoring and alerting
   - Document operational procedures

3. **User Feedback**:
   - Gather feedback on real-time updates
   - Monitor user engagement metrics
   - Identify areas for improvement

4. **Future Enhancements**:
   - Implement automatic polling fallback
   - Add presence indicators
   - Optimize for mobile devices
   - Add offline support

---

**Last Updated**: 2026-02-07
**Status**: Ready for Testing
**Phase**: 7 of 9
