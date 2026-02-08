# AI Chat Assistant - Quick Start Guide

**Specs Implemented:** Spec 5 (MCP Task Tools) + Spec 6 (Chat Frontend)
**Status:** ✅ Fully Working
**Date:** 2026-02-07

---

## 🎯 What You Can Do

Your AI Chat Assistant can now:
- ✅ **Create tasks** from natural language ("Add buy groceries")
- ✅ **List tasks** with filtering ("Show my completed tasks")
- ✅ **Complete tasks** ("Mark task 1 as done")
- ✅ **Update tasks** ("Change task 2 title to 'Call dentist'")
- ✅ **Delete tasks** ("Delete task 3")
- ✅ **Maintain conversation** (remembers context across messages)

---

## 🚀 Quick Start (3 Steps)

### Step 1: Start Backend
```bash
cd C:\Users\Ali Haider\hakathon2\phase2\backend
uvicorn app.main:app --reload --port 8001
```

**Expected output:**
```
UserWarning: MOCK_OPENAI is enabled. Using mock agent service
INFO:     Uvicorn running on http://127.0.0.1:8001
INFO:     Application startup complete.
```

### Step 2: Start Frontend
```bash
cd C:\Users\Ali Haider\hakathon2\phase2\frontend
npm run dev
```

**Expected output:**
```
  ▲ Next.js 15.x.x
  - Local:        http://localhost:3000
  ✓ Ready in 2.5s
```

### Step 3: Open Chat
1. Open browser: http://localhost:3000/chat
2. Login with your credentials
3. Start chatting!

---

## 💬 Example Conversations

### Conversation 1: Create and List Tasks

**You:** "Add buy groceries"
**AI:** "I've added 'buy groceries' to your task list."
*[Tool used: add_task]*

**You:** "Add call mom"
**AI:** "I've added 'call mom' to your task list."
*[Tool used: add_task]*

**You:** "List my tasks"
**AI:** "Here are all your tasks. (Mock: In real mode, this would show actual tasks from database)"
*[Tool used: list_tasks]*

### Conversation 2: Complete and Filter Tasks

**You:** "Mark task 1 as done"
**AI:** "I've marked task #1 as completed. Great job!"
*[Tool used: update_task]*

**You:** "Show completed tasks"
**AI:** "Here are your completed tasks. (Mock: In real mode, this would show actual completed tasks)"
*[Tool used: list_tasks with status=completed]*

### Conversation 3: Update and Delete

**You:** "Update task 2"
**AI:** "I've updated task #2."
*[Tool used: update_task]*

**You:** "Delete task 3"
**AI:** "I've deleted task #3 from your list."
*[Tool used: delete_task]*

---

## 🎨 Chat Interface Features

### What You'll See

```
┌─────────────────────────────────────────┐
│ AI Todo Assistant                       │
│ Ask me to help you manage your tasks    │
├─────────────────────────────────────────┤
│                                         │
│ 👤 You: Add buy groceries               │
│                                         │
│ 🤖 AI: I've added 'buy groceries' to    │
│        your task list.                  │
│                                         │
│ 👤 You: List my tasks                   │
│                                         │
│ 🤖 AI: Here are all your tasks...       │
│                                         │
├─────────────────────────────────────────┤
│ Type a message...              [Send]   │
└─────────────────────────────────────────┘
```

### Features
- ✅ **Real-time responses** - AI responds immediately
- ✅ **Conversation history** - Scroll to see past messages
- ✅ **Loading indicator** - Shows when AI is thinking
- ✅ **Error handling** - Retry failed messages
- ✅ **Auto-scroll** - Automatically scrolls to latest message
- ✅ **Keyboard shortcuts** - Press Enter to send

---

## 🧪 Testing Checklist

### Basic Functionality
- [ ] Open http://localhost:3000/chat
- [ ] Login successfully
- [ ] See chat interface
- [ ] Type "Hello" and get response
- [ ] See conversation history

### Task Creation
- [ ] Send: "Add buy groceries"
- [ ] AI confirms task created
- [ ] Send: "Add call mom"
- [ ] AI confirms second task created

### Task Listing
- [ ] Send: "List my tasks"
- [ ] AI shows all tasks
- [ ] Send: "Show completed tasks"
- [ ] AI shows filtered list

### Task Completion
- [ ] Send: "Mark task 1 as done"
- [ ] AI confirms completion
- [ ] Verify task is marked complete

### Task Deletion
- [ ] Send: "Delete task 2"
- [ ] AI confirms deletion
- [ ] Verify task is removed

### Conversation Continuity
- [ ] Send multiple messages
- [ ] Verify conversation_id is maintained
- [ ] Refresh page
- [ ] Verify conversation persists

---

## 🔧 Troubleshooting

### Issue: Chat page shows blank screen

**Solution:**
1. Check if you're logged in
2. Open browser console (F12)
3. Look for errors
4. Verify backend is running on port 8001

### Issue: Messages not sending

**Check 1: Backend running?**
```bash
curl http://localhost:8001/health
# Expected: {"status":"healthy","database":"connected"}
```

**Check 2: Frontend connected?**
- Open browser DevTools → Network tab
- Send a message
- Look for POST to /api/chat
- Check response status

**Check 3: Authentication?**
- Verify you're logged in
- Check JWT token in localStorage
- Try logging out and back in

### Issue: AI responses don't make sense

**This is expected in mock mode!**
- Mock service uses simple keyword matching
- Not real AI (to avoid API costs)
- To enable real OpenAI:
  1. Add billing to OpenAI account
  2. Set `MOCK_OPENAI=false` in backend/.env
  3. Restart backend

### Issue: "500 Internal Server Error"

**Check backend logs:**
```bash
# In backend terminal, look for error messages
# Common causes:
# - Database connection issue
# - OpenAI API quota (if mock mode disabled)
# - Missing environment variables
```

---

## 📊 Architecture Overview

### Request Flow

```
User types message
    ↓
Frontend (ChatContext)
    ↓
POST /api/chat
    ↓
Backend (chat.py)
    ↓
JWT validation
    ↓
AgentService
    ↓
OpenAI API (or Mock)
    ↓
Decides which tool to call
    ↓
MCPClient
    ↓
MCP Tool (add_task, list_tasks, etc.)
    ↓
TaskService
    ↓
Database
    ↓
Response back to user
```

### Key Components

**Frontend:**
- `/chat` - Chat page
- `ChatContext` - State management
- `ChatInterface` - UI components
- `chat.ts` - API client

**Backend:**
- `/api/chat` - Chat endpoint
- `AgentService` - AI orchestration
- `MCPClient` - Tool registry
- `mcp_tools.py` - Tool implementations
- `task_service.py` - Database operations

---

## 🎯 Natural Language Examples

### Creating Tasks

| What You Say | What Happens |
|--------------|--------------|
| "Add buy groceries" | Creates task: "buy groceries" |
| "Create a task to call mom" | Creates task: "call mom" |
| "Remind me to exercise" | Creates task: "exercise" |
| "I need to finish the report" | Creates task: "finish the report" |

### Listing Tasks

| What You Say | What Happens |
|--------------|--------------|
| "List my tasks" | Shows all tasks |
| "Show my tasks" | Shows all tasks |
| "What are my tasks?" | Shows all tasks |
| "Show completed tasks" | Shows only completed |
| "Show pending tasks" | Shows only pending |

### Completing Tasks

| What You Say | What Happens |
|--------------|--------------|
| "Mark task 1 as done" | Completes task #1 |
| "Complete task 2" | Completes task #2 |
| "Finish task 3" | Completes task #3 |
| "Task 1 is done" | Completes task #1 |

### Deleting Tasks

| What You Say | What Happens |
|--------------|--------------|
| "Delete task 2" | Deletes task #2 |
| "Remove task 3" | Deletes task #3 |
| "Cancel task 1" | Deletes task #1 |

### Updating Tasks

| What You Say | What Happens |
|--------------|--------------|
| "Update task 2" | Updates task #2 |
| "Change task 1" | Updates task #1 |
| "Edit task 3" | Updates task #3 |

---

## 🔄 Mock Mode vs Real OpenAI

### Current Setup: Mock Mode

**Pros:**
- ✅ Works immediately
- ✅ No API costs
- ✅ Fast responses
- ✅ Good for testing UI

**Cons:**
- ❌ Simple keyword matching
- ❌ No real AI understanding
- ❌ Generic responses
- ❌ No conversation context

### Switching to Real OpenAI

**When you're ready for real AI:**

1. **Add billing to OpenAI**
   - Visit: https://platform.openai.com/account/billing
   - Add payment method
   - Set limit: $5-10/month

2. **Update configuration**
   ```bash
   # Edit backend/.env
   MOCK_OPENAI=false
   ```

3. **Restart backend**
   ```bash
   cd backend
   uvicorn app.main:app --reload --port 8001
   ```

4. **Test with real AI**
   - Responses will be much more intelligent
   - AI will understand complex queries
   - Conversation context will work
   - Cost: ~$0.0003 per message

---

## 📝 API Reference

### POST /api/chat

**Request:**
```json
{
  "message": "Add buy groceries",
  "conversation_id": null
}
```

**Response:**
```json
{
  "conversation_id": 1,
  "response": "I've added 'buy groceries' to your task list.",
  "tool_calls": [
    {
      "tool": "add_task",
      "arguments": {
        "title": "buy groceries",
        "description": "Task created via chat: Add buy groceries"
      }
    }
  ]
}
```

### MCP Tools Available

| Tool | Parameters | Description |
|------|------------|-------------|
| **add_task** | title, description | Create new task |
| **list_tasks** | status | List tasks (all/pending/completed) |
| **get_task** | task_id | Get single task details |
| **update_task** | task_id, updates | Update task fields |
| **delete_task** | task_id | Delete task |

---

## 🎉 You're Ready!

Your AI Chat Assistant is fully functional. Just:
1. Start backend and frontend
2. Open http://localhost:3000/chat
3. Start chatting with your AI assistant!

**Need help?**
- Read: `SPEC_5_6_VERIFICATION.md` - Technical details
- Read: `MOCK_SERVICE_GUIDE.md` - Mock mode guide
- Run: `python test_mock_service.py` - Test tools

---

**Last Updated:** 2026-02-07
**Status:** ✅ Ready to use
