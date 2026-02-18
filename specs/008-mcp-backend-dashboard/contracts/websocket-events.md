# WebSocket Events Specification

**Feature**: MCP Backend Dashboard - Real-Time Updates
**Version**: 1.0.0
**Protocol**: WebSocket (RFC 6455)

## Connection

### Endpoint
```
ws://localhost:8001/api/ws
```

### Authentication
JWT token must be provided in one of two ways:

**Option 1: Query Parameter**
```
ws://localhost:8001/api/ws?token={jwt_token}
```

**Option 2: First Message**
```json
{
  "type": "auth",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Connection Lifecycle

1. **Client connects** to WebSocket endpoint
2. **Server accepts** connection
3. **Client authenticates** (via query param or first message)
4. **Server validates** JWT token and extracts user_id
5. **Server subscribes** client to user-specific events
6. **Server sends** events when tasks change
7. **Client receives** events and updates UI
8. **Connection closes** on disconnect or error

### Reconnection Strategy

**Client-side reconnection logic**:
- Initial retry: 1 second
- Exponential backoff: 2s, 4s, 8s, 16s, 32s (max)
- Max retries: Unlimited (until user closes page)
- On reconnect: Re-authenticate and sync state

---

## Event Types

### 1. task_created

**Sent when**: A new task is created by the user

**Payload**:
```json
{
  "event_type": "task_created",
  "timestamp": "2026-02-07T12:34:56.789Z",
  "data": {
    "task_id": 123,
    "user_id": 456,
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "status": "pending",
    "created_at": "2026-02-07T12:34:56.789Z"
  }
}
```

**Dashboard Action**: Increment `total_tasks` and `pending_tasks` by 1

---

### 2. task_updated

**Sent when**: An existing task is updated (title, description, or status changed)

**Payload**:
```json
{
  "event_type": "task_updated",
  "timestamp": "2026-02-07T12:35:00.123Z",
  "data": {
    "task_id": 123,
    "user_id": 456,
    "title": "Buy groceries",
    "description": "Milk, eggs, bread, cheese",
    "status": "pending",
    "updated_at": "2026-02-07T12:35:00.123Z"
  }
}
```

**Dashboard Action**: No change to counts (unless status changed)

---

### 3. task_completed

**Sent when**: A task status changes from 'pending' to 'completed'

**Payload**:
```json
{
  "event_type": "task_completed",
  "timestamp": "2026-02-07T12:36:00.456Z",
  "data": {
    "task_id": 123,
    "user_id": 456,
    "title": "Buy groceries",
    "status": "completed",
    "updated_at": "2026-02-07T12:36:00.456Z"
  }
}
```

**Dashboard Action**:
- Decrement `pending_tasks` by 1
- Increment `completed_tasks` by 1
- `total_tasks` remains unchanged

---

### 4. task_reopened

**Sent when**: A task status changes from 'completed' to 'pending'

**Payload**:
```json
{
  "event_type": "task_reopened",
  "timestamp": "2026-02-07T12:37:00.789Z",
  "data": {
    "task_id": 123,
    "user_id": 456,
    "title": "Buy groceries",
    "status": "pending",
    "updated_at": "2026-02-07T12:37:00.789Z"
  }
}
```

**Dashboard Action**:
- Increment `pending_tasks` by 1
- Decrement `completed_tasks` by 1
- `total_tasks` remains unchanged

---

### 5. task_deleted

**Sent when**: A task is permanently deleted

**Payload**:
```json
{
  "event_type": "task_deleted",
  "timestamp": "2026-02-07T12:38:00.012Z",
  "data": {
    "task_id": 123,
    "user_id": 456,
    "status": "pending"
  }
}
```

**Dashboard Action**:
- Decrement `total_tasks` by 1
- Decrement `pending_tasks` or `completed_tasks` by 1 (based on status)

---

### 6. task_shared

**Sent when**: A task is shared with the user by another user

**Payload**:
```json
{
  "event_type": "task_shared",
  "timestamp": "2026-02-07T12:39:00.345Z",
  "data": {
    "task_id": 789,
    "shared_by_user_id": 999,
    "shared_with_user_id": 456,
    "permission": "view",
    "created_at": "2026-02-07T12:39:00.345Z"
  }
}
```

**Dashboard Action**: Increment `shared_tasks` by 1

---

### 7. connection_ack

**Sent when**: Server acknowledges successful connection and authentication

**Payload**:
```json
{
  "event_type": "connection_ack",
  "timestamp": "2026-02-07T12:30:00.000Z",
  "data": {
    "user_id": 456,
    "message": "Connected successfully"
  }
}
```

**Dashboard Action**: Update connection status indicator to "Connected"

---

### 8. error

**Sent when**: An error occurs (authentication failure, invalid message, etc.)

**Payload**:
```json
{
  "event_type": "error",
  "timestamp": "2026-02-07T12:40:00.678Z",
  "data": {
    "error": "Authentication failed",
    "detail": "Invalid JWT token",
    "code": "AUTH_ERROR"
  }
}
```

**Dashboard Action**: Display error message, attempt reconnection

---

## Client Implementation Example

### JavaScript/TypeScript

```typescript
class DashboardWebSocket {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectDelay = 32000; // 32 seconds

  connect(token: string) {
    const url = `ws://localhost:8001/api/ws?token=${token}`;
    this.ws = new WebSocket(url);

    this.ws.onopen = () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
    };

    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      this.handleEvent(message);
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    this.ws.onclose = () => {
      console.log('WebSocket disconnected');
      this.reconnect(token);
    };
  }

  private handleEvent(message: any) {
    switch (message.event_type) {
      case 'task_created':
        // Update dashboard: increment total and pending
        break;
      case 'task_completed':
        // Update dashboard: decrement pending, increment completed
        break;
      case 'task_deleted':
        // Update dashboard: decrement total and status count
        break;
      // ... handle other events
    }
  }

  private reconnect(token: string) {
    const delay = Math.min(
      1000 * Math.pow(2, this.reconnectAttempts),
      this.maxReconnectDelay
    );
    this.reconnectAttempts++;

    setTimeout(() => {
      console.log(`Reconnecting... (attempt ${this.reconnectAttempts})`);
      this.connect(token);
    }, delay);
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}
```

---

## Server Implementation Notes

### Broadcasting Strategy

**User-specific events**: Only send to connections belonging to that user
```python
async def broadcast_to_user(user_id: int, event: dict):
    for connection in active_connections:
        if connection.user_id == user_id:
            await connection.send_json(event)
```

**Team events**: Send to all team members
```python
async def broadcast_to_team(team_id: int, event: dict):
    team_member_ids = get_team_member_ids(team_id)
    for connection in active_connections:
        if connection.user_id in team_member_ids:
            await connection.send_json(event)
```

### Connection Management

**Track active connections**:
```python
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)

    def disconnect(self, websocket: WebSocket, user_id: int):
        self.active_connections[user_id].remove(websocket)
        if not self.active_connections[user_id]:
            del self.active_connections[user_id]
```

---

## Security Considerations

1. **Authentication**: Always validate JWT token before accepting connection
2. **Authorization**: Only send events for tasks the user owns or has access to
3. **Rate Limiting**: Limit number of connections per user (e.g., max 5)
4. **Message Validation**: Validate all incoming messages from client
5. **Connection Timeout**: Close idle connections after 1 hour
6. **CORS**: Configure WebSocket CORS for production domains

---

## Performance Considerations

1. **Connection Pooling**: Reuse database connections for event queries
2. **Event Batching**: Batch multiple events if many tasks change simultaneously
3. **Selective Broadcasting**: Only send events to affected users
4. **Heartbeat**: Send ping/pong every 30 seconds to keep connection alive
5. **Graceful Shutdown**: Close all connections cleanly on server shutdown

---

## Testing Checklist

- [ ] Connection establishes successfully with valid JWT
- [ ] Connection rejected with invalid JWT
- [ ] Events received when tasks are created
- [ ] Events received when tasks are updated
- [ ] Events received when tasks are deleted
- [ ] Events received when tasks are completed
- [ ] Events received when tasks are shared
- [ ] Reconnection works after disconnect
- [ ] Multiple connections per user work correctly
- [ ] No events leak to unauthorized users
- [ ] Connection closes gracefully on logout
- [ ] Heartbeat keeps connection alive

---

## Fallback Strategy

If WebSocket connection fails or is unavailable:
1. Dashboard falls back to polling (5-second interval)
2. Display warning: "Real-time updates unavailable, using polling"
3. Retry WebSocket connection every 30 seconds
4. User experience remains functional (just slower updates)

---

## Future Enhancements

1. **Presence**: Show which team members are online
2. **Typing Indicators**: Show when someone is creating a task
3. **Notifications**: Browser notifications for important events
4. **Message History**: Replay missed events on reconnect
5. **Compression**: Use WebSocket compression for large payloads
