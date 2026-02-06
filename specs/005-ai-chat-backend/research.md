# Research & Discovery: AI Chat Backend

**Feature**: 005-ai-chat-backend
**Date**: 2026-02-06
**Phase**: 0 - Research & Discovery

## Overview

This document captures research findings for implementing a stateless AI chat backend with OpenAI Agents SDK integration and MCP tool delegation. The research focuses on architectural patterns, SDK integration approaches, and best practices for production-grade AI systems.

## Research Questions

1. How to integrate OpenAI Agents SDK with FastAPI?
2. How to use MCP SDK for tool invocation?
3. How to manage stateless conversation context?
4. How to handle agent failures gracefully?
5. How to manage token limits for conversation history?
6. How to structure agent prompts for task management?

## Research Findings

### 1. OpenAI Agents SDK Integration with FastAPI

**Decision**: Use OpenAI Agents SDK (openai-agents) with async/await pattern in FastAPI endpoints

**Rationale**:
- OpenAI Agents SDK provides high-level abstractions for agent orchestration
- Supports tool calling (function calling) natively
- Integrates well with FastAPI's async architecture
- Handles conversation context management
- Provides built-in error handling and retry logic

**Integration Pattern**:
```python
from openai import AsyncOpenAI
from openai.types.beta import Assistant, Thread

# Initialize client
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

# Create assistant with tools
assistant = await client.beta.assistants.create(
    name="Todo Task Manager",
    instructions="You help users manage their todo tasks...",
    tools=[...],  # MCP tools registered here
    model="gpt-4-turbo-preview"
)

# Run conversation
thread = await client.beta.threads.create()
message = await client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content=user_message
)
run = await client.beta.threads.runs.create_and_poll(
    thread_id=thread.id,
    assistant_id=assistant.id
)
```

**Alternatives Considered**:
- **LangChain**: More complex, heavier dependencies, overkill for our use case
- **Direct OpenAI API**: Lower-level, requires manual conversation management
- **Custom agent framework**: Reinventing the wheel, higher maintenance burden

**Rejected Because**: OpenAI Agents SDK provides the right level of abstraction for our needs without unnecessary complexity.

### 2. MCP SDK Usage for Tool Invocation

**Decision**: Use MCP SDK (mcp-python) to register tools and handle invocations

**Rationale**:
- MCP (Model Context Protocol) provides standardized tool interface
- Supports both synchronous and asynchronous tool execution
- Built-in schema validation for tool parameters
- Integrates with OpenAI function calling
- Enables tool auditability and logging

**Integration Pattern**:
```python
from mcp import MCPServer, Tool

# Define MCP tools
@Tool(
    name="create_task",
    description="Create a new task for the user",
    parameters={
        "title": {"type": "string", "description": "Task title"},
        "description": {"type": "string", "description": "Task description"}
    }
)
async def create_task(title: str, description: str, user_id: str):
    # Validate user_id from JWT
    # Call task service to create task
    # Return structured response
    pass

# Register tools with OpenAI assistant
tools = [
    {"type": "function", "function": create_task.to_openai_function()}
]
```

**Alternatives Considered**:
- **Direct function calling**: No standardization, harder to audit
- **REST API calls from agent**: Breaks tool abstraction, harder to test
- **Custom tool protocol**: Reinventing MCP, not worth the effort

**Rejected Because**: MCP SDK provides standardized tool interface with built-in validation and auditability.

### 3. Stateless Conversation Management

**Decision**: Store conversation history in database, reconstruct context on each request

**Rationale**:
- Enables horizontal scaling (no sticky sessions)
- Survives server restarts (constitutional requirement)
- Simplifies deployment and maintenance
- Aligns with serverless architecture patterns

**Implementation Strategy**:
```python
# On each request:
1. Load conversation from DB (if conversation_id provided)
2. Load all messages for conversation (ordered by created_at)
3. Build agent context from message history
4. Truncate if exceeds token limit (keep recent messages)
5. Run agent with reconstructed context
6. Persist new messages to DB
7. Return response
```

**Token Limit Management**:
- GPT-4 Turbo: 128k tokens context window
- Reserve 4k tokens for response
- Use ~100k tokens for conversation history
- Estimate: ~500 tokens per message (average)
- Max messages in context: ~200 messages
- Strategy: Keep last 50 messages, summarize older context if needed

**Alternatives Considered**:
- **In-memory session state**: Violates stateless principle, doesn't scale
- **Redis cache**: Adds complexity, still requires DB persistence
- **Conversation summarization**: Complex, may lose important context

**Rejected Because**: Database-backed stateless approach is simplest and meets all constitutional requirements.

### 4. Agent Failure Handling

**Decision**: Implement graceful degradation with user-friendly error messages

**Rationale**:
- Agent failures should not crash the system
- Users should receive helpful feedback
- Errors should be logged for debugging
- System should remain available even if OpenAI API is down

**Error Handling Strategy**:
```python
try:
    # Run agent
    response = await agent_service.run(conversation_id, message)
except OpenAIAPIError as e:
    # OpenAI API failure (rate limit, timeout, service unavailable)
    logger.error(f"OpenAI API error: {e}")
    return "I'm having trouble processing your request right now. Please try again in a moment."
except ToolInvocationError as e:
    # MCP tool failure
    logger.error(f"Tool invocation error: {e}")
    return "I encountered an issue managing your tasks. Please try again."
except Exception as e:
    # Unexpected error
    logger.error(f"Unexpected error: {e}")
    return "Something went wrong. Please try again later."
```

**Retry Strategy**:
- OpenAI API: 3 retries with exponential backoff
- MCP tools: 2 retries with linear backoff
- Database: 3 retries with exponential backoff

**Alternatives Considered**:
- **Fail fast**: Poor user experience, no recovery
- **Circuit breaker**: Overkill for MVP, adds complexity
- **Fallback to rule-based**: Complex to maintain, inconsistent UX

**Rejected Because**: Simple retry with graceful degradation provides best balance of reliability and simplicity.

### 5. Conversation History Truncation

**Decision**: Keep last 50 messages in agent context, with intelligent truncation

**Rationale**:
- Balances context preservation with token limits
- Most conversations don't exceed 50 messages
- Recent messages are most relevant for intent understanding
- Older context can be summarized if needed (future enhancement)

**Truncation Strategy**:
```python
def build_agent_context(messages: List[Message], max_tokens: int = 100000):
    # Start with most recent messages
    context_messages = []
    total_tokens = 0

    for message in reversed(messages):
        estimated_tokens = len(message.content) // 4  # Rough estimate
        if total_tokens + estimated_tokens > max_tokens:
            break
        context_messages.insert(0, message)
        total_tokens += estimated_tokens

    # Always include system message
    system_message = "You are a helpful assistant for managing todo tasks..."
    return [system_message] + context_messages
```

**Alternatives Considered**:
- **Load all messages**: May exceed token limits, slow queries
- **Fixed window (e.g., last 10)**: May lose important context
- **Summarization**: Complex, may lose nuance, requires additional API calls

**Rejected Because**: Last 50 messages with token-based truncation provides good balance.

### 6. Agent Prompt Engineering

**Decision**: Use structured system prompt with clear instructions and examples

**Rationale**:
- Clear instructions improve agent accuracy
- Examples demonstrate expected behavior
- Structured format ensures consistency
- Tool descriptions guide agent decision-making

**System Prompt Template**:
```
You are a helpful assistant for managing todo tasks. You help users create, view, update, and delete their tasks using natural language.

CAPABILITIES:
- Create tasks: "Add buy groceries to my list"
- List tasks: "Show me my tasks"
- Update tasks: "Mark buy groceries as done"
- Delete tasks: "Remove buy groceries"

TOOLS AVAILABLE:
- create_task(title, description): Create a new task
- list_tasks(): Get all user's tasks
- update_task(task_id, updates): Update task details
- delete_task(task_id): Delete a task
- get_task(task_id): Get task details

BEHAVIOR GUIDELINES:
1. Always confirm destructive actions (delete, bulk operations)
2. Provide natural, conversational responses
3. If user intent is unclear, ask clarifying questions
4. Handle errors gracefully with helpful messages
5. Be concise but friendly

EXAMPLES:
User: "Add buy groceries to my list"
Assistant: [calls create_task] "I've added 'buy groceries' to your task list."

User: "Show me my tasks"
Assistant: [calls list_tasks] "You have 3 tasks: 1. Buy groceries (pending), 2. Call dentist (pending), 3. Finish report (completed)"

User: "Delete buy groceries"
Assistant: "Are you sure you want to delete 'buy groceries'? Reply 'yes' to confirm."
```

**Alternatives Considered**:
- **Minimal prompt**: Less guidance, lower accuracy
- **Few-shot learning**: More examples, higher token usage
- **Fine-tuned model**: Expensive, complex, overkill for MVP

**Rejected Because**: Structured system prompt with guidelines provides best balance of accuracy and token efficiency.

## Technology Decisions

### OpenAI Model Selection

**Decision**: Use GPT-4 Turbo (gpt-4-turbo-preview)

**Rationale**:
- 128k token context window (supports long conversations)
- Better reasoning capabilities than GPT-3.5
- Native function calling support
- Acceptable latency (<5 seconds typical)
- Cost-effective for production use

**Alternatives**: GPT-3.5 Turbo (cheaper but less capable), GPT-4 (smaller context window)

### MCP SDK Version

**Decision**: Use mcp-python 0.1.0+ (latest stable)

**Rationale**:
- Official MCP implementation
- Active development and support
- Python 3.11+ compatibility
- Async/await support

### Database Schema

**Decision**: Add Conversation and Message tables with foreign keys to User

**Rationale**:
- Normalized schema (3NF)
- Efficient queries with proper indexing
- Supports conversation resume
- Aligns with existing schema patterns

## Performance Considerations

### Expected Latency Breakdown

- Database query (load conversation): ~50ms
- Agent reasoning (OpenAI API): ~3-5 seconds
- Tool invocation (MCP): ~100-500ms per tool
- Database write (persist message): ~50ms
- **Total**: ~4-6 seconds typical, <10 seconds worst case

### Optimization Strategies

1. **Database Indexing**: Index on user_id, conversation_id, created_at
2. **Connection Pooling**: Reuse database connections
3. **Async I/O**: Use async/await for all I/O operations
4. **Caching**: Cache assistant configuration (not conversation state)
5. **Batch Operations**: Batch message persistence when possible

## Security Considerations

### JWT Validation

- Verify JWT signature on every request
- Extract user_id from JWT claims
- Never trust client-supplied user_id
- Validate token expiration

### Input Sanitization

- Validate message length (<10,000 characters)
- Sanitize user input for SQL injection
- Validate conversation_id format (integer)
- Rate limit requests (60 per minute per user)

### Tool Authorization

- Pass user_id from JWT to all tool invocations
- Tools validate user_id matches resource owner
- Log all tool invocations for audit trail
- Never expose tool implementation details to users

## Risks & Mitigations

### Risk 1: OpenAI API Rate Limits
**Mitigation**: Implement exponential backoff, queue requests, provide clear error messages

### Risk 2: High Latency
**Mitigation**: Set timeout limits, provide loading indicators, optimize database queries

### Risk 3: Token Limit Exceeded
**Mitigation**: Implement intelligent truncation, monitor conversation lengths, alert on approaching limits

### Risk 4: Tool Invocation Failures
**Mitigation**: Retry logic, graceful degradation, clear error messages to users

## Next Steps

1. Implement data models (Conversation, Message)
2. Create API contracts (OpenAPI spec for POST /api/chat)
3. Write quickstart guide for setup
4. Proceed to Phase 1: Design & Contracts
