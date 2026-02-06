# Quickstart Guide: AI Chat Backend

**Feature**: 005-ai-chat-backend
**Date**: 2026-02-06
**Phase**: 1 - Design & Contracts

## Overview

This guide walks you through setting up the AI Chat Backend for local development. You'll configure OpenAI API access, set up the MCP tool server, run database migrations, and test the chat endpoint.

**Prerequisites**:
- Python 3.11+ installed
- PostgreSQL database (Neon Serverless) configured
- OpenAI API account with API key
- Existing Phase I & II backend running (authentication, tasks API)

**Estimated Setup Time**: 15-20 minutes

---

## Step 1: OpenAI API Configuration

### 1.1 Obtain OpenAI API Key

1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Sign in or create an account
3. Navigate to **API Keys** section
4. Click **Create new secret key**
5. Copy the key (starts with `sk-...`)

**Important**: Store this key securely. You won't be able to see it again.

### 1.2 Add API Key to Environment

Add the OpenAI API key to your `.env` file:

```bash
# .env (backend root)

# Existing environment variables
DATABASE_URL=postgresql://...
JWT_SECRET=...
BETTER_AUTH_SECRET=...

# NEW: OpenAI API Configuration
OPENAI_API_KEY=sk-...  # Replace with your actual key
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_MAX_TOKENS=128000
```

**Security Note**: Never commit `.env` to version control. Ensure `.env` is in `.gitignore`.

### 1.3 Verify Configuration

Test that the API key works:

```bash
cd backend
python -c "
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
response = client.chat.completions.create(
    model='gpt-4-turbo-preview',
    messages=[{'role': 'user', 'content': 'Hello!'}],
    max_tokens=10
)
print('✅ OpenAI API key is valid')
print(f'Response: {response.choices[0].message.content}')
"
```

**Expected Output**:
```
✅ OpenAI API key is valid
Response: Hello! How can I assist you today?
```

---

## Step 2: Database Migration

### 2.1 Create Migration

The migration script creates two new tables: `conversations` and `messages`.

**Migration File**: `backend/alembic/versions/xxx_add_conversation_message_tables.py`

**Tables Created**:
- `conversations`: Stores conversation metadata (id, user_id, timestamps)
- `messages`: Stores individual messages (id, conversation_id, user_id, role, content, timestamp)

### 2.2 Run Migration

```bash
cd backend
alembic upgrade head
```

**Expected Output**:
```
INFO  [alembic.runtime.migration] Running upgrade xxx -> yyy, Add conversation and message tables for AI chat backend
```

### 2.3 Verify Tables

Connect to your database and verify the tables exist:

```bash
psql $DATABASE_URL -c "\dt"
```

**Expected Output**:
```
              List of relations
 Schema |       Name       | Type  |  Owner
--------+------------------+-------+---------
 public | users            | table | ...
 public | tasks            | table | ...
 public | conversations    | table | ...  ← NEW
 public | messages         | table | ...  ← NEW
```

---

## Step 3: MCP Tool Server Setup

**Note**: The MCP Tool Server is defined in a separate spec (006-mcp-tool-server). This section provides a minimal setup for local development.

### 3.1 Install MCP SDK

```bash
cd backend
pip install mcp-python
```

### 3.2 Verify MCP Installation

```bash
python -c "import mcp; print(f'✅ MCP SDK installed: {mcp.__version__}')"
```

### 3.3 MCP Tool Server Configuration

Add MCP tool server URL to `.env`:

```bash
# .env (backend root)

# MCP Tool Server Configuration
MCP_TOOL_SERVER_URL=http://localhost:8002  # Local MCP server
MCP_TOOL_SERVER_TIMEOUT=30  # seconds
```

**Note**: The MCP Tool Server implementation is out of scope for this spec. For now, the chat backend will use placeholder tool implementations. Full MCP integration will be completed in spec 006-mcp-tool-server.

---

## Step 4: Install Dependencies

### 4.1 Update Requirements

Add new dependencies to `backend/requirements.txt`:

```txt
# Existing dependencies
fastapi==0.104.1
sqlmodel==0.0.14
pyjwt==2.8.0
...

# NEW: AI Chat Backend Dependencies
openai==1.6.1
mcp-python==0.1.0
```

### 4.2 Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

---

## Step 5: Start Backend Server

### 5.1 Start FastAPI Server

```bash
cd backend
uvicorn app.main:app --reload --port 8001
```

**Expected Output**:
```
INFO:     Uvicorn running on http://127.0.0.1:8001 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using StatReload
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 5.2 Verify Health Endpoint

```bash
curl http://localhost:8001/health
```

**Expected Output**:
```json
{"status": "healthy"}
```

---

## Step 6: Test Chat Endpoint

### 6.1 Obtain JWT Token

First, authenticate to get a JWT token:

```bash
# Register a test user (if not already registered)
curl -X POST http://localhost:8001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePassword123!",
    "name": "Test User"
  }'

# Login to get JWT token
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePassword123!"
  }'
```

**Expected Output**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Save the token** for the next step.

### 6.2 Send Chat Message (New Conversation)

```bash
# Replace <TOKEN> with your actual JWT token
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{
    "conversation_id": null,
    "message": "Add buy groceries to my list"
  }'
```

**Expected Output**:
```json
{
  "conversation_id": 1,
  "response": "I've added 'buy groceries' to your task list.",
  "tool_calls": [
    {
      "tool": "create_task",
      "arguments": {
        "title": "buy groceries",
        "description": ""
      }
    }
  ]
}
```

### 6.3 Continue Conversation

```bash
# Use the conversation_id from the previous response
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{
    "conversation_id": 1,
    "message": "Show me my tasks"
  }'
```

**Expected Output**:
```json
{
  "conversation_id": 1,
  "response": "You have 1 task: 1. Buy groceries (pending)",
  "tool_calls": [
    {
      "tool": "list_tasks",
      "arguments": {}
    }
  ]
}
```

---

## Step 7: Verify Stateless Architecture

### 7.1 Restart Backend Server

1. Stop the backend server (Ctrl+C)
2. Restart the server:
   ```bash
   uvicorn app.main:app --reload --port 8001
   ```

### 7.2 Resume Conversation

Send another message using the same `conversation_id`:

```bash
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{
    "conversation_id": 1,
    "message": "Mark buy groceries as done"
  }'
```

**Expected Output**:
```json
{
  "conversation_id": 1,
  "response": "I've marked 'buy groceries' as completed.",
  "tool_calls": [
    {
      "tool": "update_task",
      "arguments": {
        "task_id": 1,
        "status": "completed"
      }
    }
  ]
}
```

**✅ Success**: The conversation resumed after server restart, demonstrating stateless architecture.

---

## Step 8: Verify Database Persistence

### 8.1 Check Conversations Table

```bash
psql $DATABASE_URL -c "SELECT * FROM conversations;"
```

**Expected Output**:
```
 id |               user_id                |      created_at       |      updated_at
----+--------------------------------------+-----------------------+-----------------------
  1 | 550e8400-e29b-41d4-a716-446655440000 | 2026-02-06 10:00:00   | 2026-02-06 10:05:00
```

### 8.2 Check Messages Table

```bash
psql $DATABASE_URL -c "SELECT id, conversation_id, role, content FROM messages ORDER BY created_at;"
```

**Expected Output**:
```
 id | conversation_id |    role    |              content
----+-----------------+------------+-----------------------------------
  1 |               1 | user       | Add buy groceries to my list
  2 |               1 | assistant  | I've added 'buy groceries' to your task list.
  3 |               1 | user       | Show me my tasks
  4 |               1 | assistant  | You have 1 task: 1. Buy groceries (pending)
  5 |               1 | user       | Mark buy groceries as done
  6 |               1 | assistant  | I've marked 'buy groceries' as completed.
```

**✅ Success**: All conversation history is persisted in the database.

---

## Troubleshooting

### Issue: "Invalid OpenAI API key"

**Symptoms**:
```
openai.error.AuthenticationError: Incorrect API key provided
```

**Solution**:
1. Verify the API key in `.env` starts with `sk-`
2. Check for extra spaces or newlines in the key
3. Regenerate the key on OpenAI Platform if needed

---

### Issue: "Conversation not found"

**Symptoms**:
```json
{
  "error": "Not Found",
  "detail": "Conversation not found"
}
```

**Solution**:
1. Verify the `conversation_id` exists in the database
2. Ensure the conversation belongs to the authenticated user
3. Check JWT token is valid and not expired

---

### Issue: "Rate limit exceeded"

**Symptoms**:
```json
{
  "error": "Too Many Requests",
  "detail": "Rate limit exceeded. Please try again in 60 seconds."
}
```

**Solution**:
1. Wait 60 seconds before retrying
2. Check OpenAI API usage limits on your account
3. Consider upgrading your OpenAI plan for higher limits

---

### Issue: "Tool invocation failed"

**Symptoms**:
```json
{
  "error": "Internal Server Error",
  "detail": "I encountered an issue managing your tasks. Please try again."
}
```

**Solution**:
1. Check backend logs for detailed error messages
2. Verify MCP Tool Server is running (if implemented)
3. Ensure database connection is healthy
4. Check task API endpoints are working (Phase I & II)

---

## Next Steps

1. **Run `/sp.tasks`**: Generate testable tasks from the implementation plan
2. **Implement Backend**: Use `fastapi-backend` agent to implement chat endpoint, agent service, and conversation service
3. **Implement MCP Tool Server**: Create spec 006-mcp-tool-server for tool implementations
4. **Integration Testing**: Test stateless conversation resume and tool invocations
5. **Frontend Integration**: Create spec 007-chat-frontend for ChatKit UI

---

## Additional Resources

- [OpenAI Agents SDK Documentation](https://platform.openai.com/docs/assistants/overview)
- [MCP SDK Documentation](https://github.com/modelcontextprotocol/python-sdk)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Neon Serverless PostgreSQL](https://neon.tech/docs)

---

## Support

If you encounter issues not covered in this guide:

1. Check backend logs: `tail -f backend/logs/app.log`
2. Review the specification: `specs/005-ai-chat-backend/spec.md`
3. Review the implementation plan: `specs/005-ai-chat-backend/plan.md`
4. Check the data model: `specs/005-ai-chat-backend/data-model.md`
5. Review the API contract: `specs/005-ai-chat-backend/contracts/chat-api.yaml`

For questions or issues, contact the development team.
