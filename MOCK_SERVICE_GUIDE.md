# Mock Agent Service - Quick Start Guide

## 🎯 What is This?

The Mock Agent Service allows you to **test your chat frontend without making OpenAI API calls**. This is useful when:
- Your OpenAI API quota is exceeded
- You want to develop offline
- You want to avoid API costs during development

## ✅ Current Status

**Mock mode is now ENABLED** in your backend. The chat will work without any API calls!

---

## 🚀 How to Use

### Step 1: Start the Backend

```bash
cd backend
uvicorn app.main:app --reload --port 8001
```

You should see:
```
UserWarning: MOCK_OPENAI is enabled. Using mock agent service (no real API calls).
```

### Step 2: Test from Frontend

Your frontend chat should now work! Try these messages:

**Create Tasks:**
- "Add buy groceries"
- "Create a task to call mom"
- "Remind me to exercise"

**List Tasks:**
- "Show my tasks"
- "List all tasks"
- "What are my pending tasks?"

**Complete Tasks:**
- "Mark task 1 as done"
- "Complete task 2"

**Delete Tasks:**
- "Delete task 3"
- "Remove task 1"

**Update Tasks:**
- "Update task 2"
- "Change task 1"

**General:**
- "Hello"
- "What can you do?"
- "Help"

### Step 3: Verify It's Working

**Expected Behavior:**
- ✅ Chat messages send successfully
- ✅ You get intelligent responses
- ✅ Tool calls are made (add_task, list_tasks, etc.)
- ✅ No 500 errors
- ✅ No API costs

**Mock Indicators:**
- Responses include "(Mock: ...)" text
- Backend logs show "Using MockAgentService"
- No OpenAI API calls in network logs

---

## 🔄 Switching Between Mock and Real API

### Enable Mock Mode (Current Setting)
```bash
# In backend/.env
MOCK_OPENAI=true
```

### Disable Mock Mode (Use Real OpenAI)
```bash
# In backend/.env
MOCK_OPENAI=false
```

**After changing, restart the backend:**
```bash
cd backend
# Stop current server (Ctrl+C)
uvicorn app.main:app --reload --port 8001
```

---

## 🧪 Testing the Mock Service

### Quick Test
```bash
cd C:\Users\Ali Haider\hakathon2\phase2
python test_mock_service.py
```

### Manual API Test
```bash
# 1. Get JWT token
curl -X POST http://localhost:8001/api/auth/signin \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"test@example.com\",\"password\":\"TestPass123\"}"

# 2. Send chat message (replace YOUR_JWT_TOKEN)
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d "{\"conversation_id\":null,\"message\":\"List my tasks\"}"
```

**Expected Response:**
```json
{
  "conversation_id": 1,
  "response": "Here are all your tasks. (Mock: In real mode, this would show actual tasks from database)",
  "tool_calls": [
    {
      "tool": "list_tasks",
      "arguments": {"status": "all"}
    }
  ]
}
```

---

## 🎨 How Mock Service Works

### Intent Detection
The mock service analyzes your message and detects intent:

| Keywords | Intent | Tool Called |
|----------|--------|-------------|
| add, create, new task | Create Task | add_task |
| list, show, my tasks | List Tasks | list_tasks |
| complete, done, finish | Complete Task | update_task |
| delete, remove, cancel | Delete Task | delete_task |
| update, change, edit | Update Task | update_task |
| hello, hi, hey | Greeting | (none) |
| help, what can you do | Help | (none) |

### Response Generation
- Responses are contextual and natural
- Tool calls match the intent
- Task IDs are extracted from messages (e.g., "task 1" → task_id: 1)
- Fallback to general responses for unrecognized intents

---

## 🔧 Troubleshooting

### Issue: Still getting 500 errors

**Check 1: Verify mock mode is enabled**
```bash
cd backend
python -c "from app.config import settings; print(f'Mock mode: {settings.MOCK_OPENAI}')"
```
Expected: `Mock mode: True`

**Check 2: Restart backend**
```bash
cd backend
# Stop current server (Ctrl+C)
uvicorn app.main:app --reload --port 8001
```

**Check 3: Check backend logs**
Look for: `Using MockAgentService (MOCK_OPENAI=true)`

### Issue: Responses don't make sense

**This is expected!** The mock service:
- ✅ Simulates responses (not real AI)
- ✅ Uses simple keyword matching
- ✅ Provides generic responses
- ❌ Doesn't understand complex queries
- ❌ Doesn't maintain conversation context

For real AI responses, you need to:
1. Add billing to OpenAI account
2. Set `MOCK_OPENAI=false`
3. Restart backend

### Issue: Tool calls not working

**Check:** Are the MCP tools actually being invoked?

The mock service generates tool calls, but the actual tools (add_task, list_tasks, etc.) still run and interact with your database. This is intentional - you can test the full flow!

---

## 📊 Comparison: Mock vs Real

| Feature | Mock Service | Real OpenAI |
|---------|-------------|-------------|
| **Cost** | Free | ~$0.0003/message |
| **Speed** | Instant | 1-3 seconds |
| **Quality** | Basic | Excellent |
| **Context** | No | Yes |
| **Complex queries** | No | Yes |
| **Offline** | Yes | No |
| **API quota** | N/A | Required |

---

## 🎯 When to Use Each Mode

### Use Mock Mode When:
- ✅ Testing frontend UI/UX
- ✅ Developing chat interface
- ✅ API quota exceeded
- ✅ Working offline
- ✅ Running automated tests
- ✅ Demonstrating to stakeholders (no costs)

### Use Real OpenAI When:
- ✅ Testing actual AI responses
- ✅ Validating conversation flow
- ✅ Testing complex queries
- ✅ Production deployment
- ✅ User acceptance testing
- ✅ Need context awareness

---

## 🚀 Next Steps

### Immediate (You Can Do Now)
1. ✅ Start backend with mock mode
2. ✅ Test chat from frontend
3. ✅ Verify no 500 errors
4. ✅ Continue frontend development

### When Ready for Real AI
1. Add billing to OpenAI account
   - Visit: https://platform.openai.com/account/billing
   - Add payment method
   - Set usage limit: $5-10/month

2. Update configuration
   ```bash
   # In backend/.env
   MOCK_OPENAI=false
   ```

3. Restart backend
   ```bash
   cd backend
   uvicorn app.main:app --reload --port 8001
   ```

4. Test with real AI
   - Send chat messages
   - Verify intelligent responses
   - Check conversation context works

---

## 📝 Files Modified

**New Files:**
- ✅ `backend/app/services/mock_agent_service.py` - Mock service implementation
- ✅ `test_mock_service.py` - Test script
- ✅ `MOCK_SERVICE_GUIDE.md` - This guide

**Modified Files:**
- ✅ `backend/app/config.py` - Added MOCK_OPENAI setting
- ✅ `backend/app/routes/chat.py` - Conditional service selection
- ✅ `backend/.env` - Enabled MOCK_OPENAI=true

---

## 💡 Tips

1. **Keep mock mode enabled during development** - No API costs!
2. **Test with real API periodically** - Ensure integration still works
3. **Use mock mode for demos** - No risk of quota issues
4. **Switch to real API before production** - Users expect real AI

---

## 🆘 Need Help?

**Mock service not working?**
```bash
cd C:\Users\Ali Haider\hakathon2\phase2
python test_mock_service.py
```

**Want to see backend logs?**
```bash
cd backend
uvicorn app.main:app --reload --port 8001 --log-level debug
```

**Ready to use real OpenAI?**
1. Add billing: https://platform.openai.com/account/billing
2. Set `MOCK_OPENAI=false` in `.env`
3. Restart backend

---

**Last Updated:** 2026-02-07
**Status:** ✅ Mock mode enabled and working
