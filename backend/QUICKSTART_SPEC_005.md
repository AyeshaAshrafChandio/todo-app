# AI Chat Backend - Quick Start Guide

## Prerequisites

1. **OpenAI API Key**: You must have a valid OpenAI API key
2. **Python 3.11+**: Ensure Python is installed
3. **Dependencies**: All dependencies installed via pip

## Setup Steps

### 1. Configure OpenAI API Key

Edit `backend/.env` and replace the placeholder with your actual OpenAI API key:

```bash
# Before (placeholder)
OPENAI_API_KEY=your-openai-api-key-here

# After (your actual key)
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Get your API key**: https://platform.openai.com/api-keys

### 2. Verify Database Migration

The migration should have already run, but you can verify:

```bash
cd backend
python migrations/005_add_conversation_message_tables.py
```

Expected output:
```
Starting Migration 005: Add Conversation and Message tables...
Creating conversations table...
Creating indexes for conversations table...
Creating messages table...
Creating indexes for messages table...
Migration 005 completed successfully!
```

### 3. Start the Backend Server

```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
Starting up: Initializing database...
Database initialized successfully
INFO:     Application startup complete.
```

### 4. Verify Chat Endpoint is Available

Open your browser and go to: http://localhost:8000/docs

You should see the Swagger UI with the new `/api/chat` endpoint listed under the "chat" tag.

## Testing the Chat Endpoint

### Step 1: Create a Test User (if needed)

```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "chattest@example.com",
    "password": "Test1234"
  }'
```

Save the `token` from the response.

### Step 2: Send Your First Chat Message

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "conversation_id": null,
    "message": "Add buy groceries to my list"
  }'
```

**Expected Response**:
```json
{
  "conversation_id": 1,
  "response": "I've added 'buy groceries' to your task list.",
  "tool_calls": [
    {
      "tool": "create_task",
      "arguments": {
        "title": "buy groceries"
      }
    }
  ]
}
```

### Step 3: Continue the Conversation

Use the `conversation_id` from the previous response:

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "conversation_id": 1,
    "message": "Also add call dentist"
  }'
```

### Step 4: Test Conversation Resume

1. Stop the server (Ctrl+C)
2. Restart the server
3. Send another message with the same `conversation_id`
4. The agent should maintain context from previous messages

## Using Swagger UI (Easier Testing)

1. Go to http://localhost:8000/docs
2. Click on "Authorize" button (top right)
3. Enter your JWT token: `Bearer YOUR_TOKEN_HERE`
4. Click "Authorize" then "Close"
5. Find the `POST /api/chat` endpoint
6. Click "Try it out"
7. Enter your request body:
   ```json
   {
     "conversation_id": null,
     "message": "Add buy groceries to my list"
   }
   ```
8. Click "Execute"
9. View the response

## Troubleshooting

### Error: "OPENAI_API_KEY environment variable is required"

**Solution**: Edit `backend/.env` and add your actual OpenAI API key.

### Error: "Not authenticated" (401)

**Solution**: Make sure you're including the JWT token in the Authorization header:
```
Authorization: Bearer YOUR_TOKEN_HERE
```

### Error: "Conversation not found or access denied" (403)

**Solution**: The conversation_id doesn't exist or belongs to another user. Use `null` to start a new conversation.

### Error: "An error occurred processing your request" (500)

**Possible causes**:
1. Invalid OpenAI API key
2. OpenAI API rate limit exceeded
3. Network connectivity issues

**Solution**: Check the server logs for detailed error messages.

### MCP Tools Return Placeholder Responses

**This is expected in MVP**: The MCP tools are placeholders. Actual task creation will be implemented in Spec 006 (MCP Tool Server).

Current behavior:
- Agent responds as if task was created
- `tool_calls` array shows which tools would be invoked
- But tasks are NOT actually created in database yet

## Verification Checklist

- [ ] OpenAI API key configured in `.env`
- [ ] Database migration ran successfully
- [ ] Server starts without errors
- [ ] `/api/chat` endpoint visible in Swagger UI
- [ ] Can create user and get JWT token
- [ ] Can send chat message and get response
- [ ] `conversation_id` is returned in response
- [ ] Can continue conversation with same `conversation_id`
- [ ] Conversation persists after server restart

## Next Steps

### To Complete Full Functionality

1. **Implement Spec 006 (MCP Tool Server)**:
   - Replace placeholder MCP tools with actual implementations
   - Connect to existing task CRUD endpoints
   - Enable real task creation via natural language

2. **Test End-to-End**:
   - Send "Add buy groceries to my list"
   - Verify task appears in `GET /api/{user_id}/tasks`
   - Confirm task was actually created in database

3. **Implement Additional User Stories** (Optional):
   - User Story 2: Task querying ("Show me my tasks")
   - User Story 3: Task updates ("Mark buy groceries as done")
   - User Story 4: Task deletion ("Delete buy groceries")
   - User Story 5: Conversation resume (already supported)

### Production Readiness

Before deploying to production:
- [ ] Add rate limiting (60 requests/minute per user)
- [ ] Implement retry logic for OpenAI API failures
- [ ] Add comprehensive logging and monitoring
- [ ] Set up error alerting
- [ ] Configure proper CORS origins
- [ ] Use PostgreSQL instead of SQLite
- [ ] Add integration tests
- [ ] Document API in OpenAPI spec
- [ ] Set up CI/CD pipeline

## Support

For issues or questions:
1. Check server logs for detailed error messages
2. Review the implementation summary: `backend/IMPLEMENTATION_SUMMARY_SPEC_005.md`
3. Consult the specification: `specs/005-ai-chat-backend/spec.md`

---

**Status**: MVP Complete (25/25 tasks)
**Ready for Testing**: Yes (requires valid OpenAI API key)
**Ready for Production**: No (requires Spec 006 implementation)
