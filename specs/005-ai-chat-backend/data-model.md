# Data Model: AI Chat Backend

**Feature**: 005-ai-chat-backend
**Date**: 2026-02-06
**Phase**: 1 - Design & Contracts

## Overview

This document defines the data models for conversation persistence in the AI Chat Backend. The models support stateless conversation management by storing all conversation history in the database, enabling conversation resume after server restarts.

## Entity Relationship Diagram

```
User (existing)
  |
  | 1:N
  |
Conversation
  |
  | 1:N
  |
Message
```

## Models

### Conversation

**Purpose**: Represents a persistent chat session between a user and the AI assistant.

**Table Name**: `conversations`

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | PRIMARY KEY, AUTO_INCREMENT | Unique conversation identifier |
| user_id | UUID | FOREIGN KEY (users.id), NOT NULL, INDEX | Owner of the conversation |
| created_at | DateTime | NOT NULL, DEFAULT NOW() | When conversation was created |
| updated_at | DateTime | NOT NULL, DEFAULT NOW(), ON UPDATE NOW() | When conversation was last updated |

**Relationships**:
- **Belongs to**: User (many-to-one)
- **Has many**: Messages (one-to-many)

**Indexes**:
- PRIMARY KEY on `id`
- INDEX on `user_id` (for efficient user conversation queries)
- INDEX on `updated_at` (for sorting by recent activity)

**Validation Rules**:
- `user_id` must reference existing user
- `created_at` cannot be modified after creation
- `updated_at` automatically updated on any message addition

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List
import uuid

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    user: Optional["User"] = Relationship(back_populates="conversations")
    messages: List["Message"] = Relationship(back_populates="conversation", cascade_delete=True)

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "created_at": "2026-02-06T10:00:00Z",
                "updated_at": "2026-02-06T10:05:00Z"
            }
        }
```

**Lifecycle**:
1. **Creation**: Created when user sends first message without conversation_id
2. **Update**: `updated_at` timestamp updated on every new message
3. **Deletion**: Cascade delete all associated messages (optional, not in MVP)
4. **Archival**: Conversations persist indefinitely (archival strategy out of scope for Phase III)

---

### Message

**Purpose**: Represents a single message in a conversation (from user or assistant).

**Table Name**: `messages`

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | PRIMARY KEY, AUTO_INCREMENT | Unique message identifier |
| conversation_id | Integer | FOREIGN KEY (conversations.id), NOT NULL, INDEX | Conversation this message belongs to |
| user_id | UUID | FOREIGN KEY (users.id), NOT NULL, INDEX | Owner of the conversation (denormalized for security) |
| role | Enum | NOT NULL, CHECK IN ('user', 'assistant') | Message sender role |
| content | Text | NOT NULL | Message content (max 10,000 characters) |
| created_at | DateTime | NOT NULL, DEFAULT NOW() | When message was created |

**Relationships**:
- **Belongs to**: Conversation (many-to-one)
- **Belongs to**: User (many-to-one)

**Indexes**:
- PRIMARY KEY on `id`
- INDEX on `conversation_id` (for efficient conversation history queries)
- INDEX on `user_id` (for security filtering)
- INDEX on `created_at` (for ordering messages chronologically)
- COMPOSITE INDEX on `(conversation_id, created_at)` (for efficient conversation history loading)

**Validation Rules**:
- `conversation_id` must reference existing conversation
- `user_id` must match conversation owner (enforced at application level)
- `role` must be either 'user' or 'assistant'
- `content` length must be <= 10,000 characters
- `created_at` cannot be modified after creation (immutable)

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional
from enum import Enum
import uuid

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", nullable=False, index=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False, index=True)
    role: MessageRole = Field(nullable=False)
    content: str = Field(nullable=False, max_length=10000)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False, index=True)

    # Relationships
    conversation: Optional["Conversation"] = Relationship(back_populates="messages")
    user: Optional["User"] = Relationship(back_populates="messages")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "conversation_id": 1,
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "role": "user",
                "content": "Add buy groceries to my list",
                "created_at": "2026-02-06T10:00:00Z"
            }
        }
```

**Lifecycle**:
1. **Creation**: Created when user sends message or agent responds
2. **Immutability**: Messages are immutable after creation (no updates or deletes)
3. **Ordering**: Messages ordered by `created_at` for conversation history
4. **Retention**: Messages persist indefinitely with conversation

---

## Existing Model Updates

### User (existing model)

**New Relationships**:
```python
# Add to existing User model
conversations: List["Conversation"] = Relationship(back_populates="user")
messages: List["Message"] = Relationship(back_populates="user")
```

**No schema changes required** - only relationship definitions added.

---

## Database Migration

**Migration File**: `alembic/versions/xxx_add_conversation_message_tables.py`

**Operations**:
1. Create `conversations` table
2. Create `messages` table
3. Add foreign key constraints
4. Create indexes
5. Add relationship back-references to User model (code-only, no schema change)

**Rollback Strategy**:
1. Drop `messages` table (cascade)
2. Drop `conversations` table
3. Remove relationship definitions from User model

**Migration Script** (Alembic):
```python
"""Add conversation and message tables for AI chat backend

Revision ID: xxx
Revises: yyy
Create Date: 2026-02-06 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'xxx'
down_revision = 'yyy'
branch_labels = None
depends_on = None

def upgrade():
    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_conversations_user_id', 'conversations', ['user_id'])
    op.create_index('ix_conversations_updated_at', 'conversations', ['updated_at'])

    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.Enum('user', 'assistant', name='messagerole'), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_messages_conversation_id', 'messages', ['conversation_id'])
    op.create_index('ix_messages_user_id', 'messages', ['user_id'])
    op.create_index('ix_messages_created_at', 'messages', ['created_at'])
    op.create_index('ix_messages_conversation_created', 'messages', ['conversation_id', 'created_at'])

def downgrade():
    op.drop_table('messages')
    op.drop_table('conversations')
```

---

## Query Patterns

### Load Conversation with Messages

**Use Case**: Reconstruct conversation context for agent

**Query**:
```python
from sqlmodel import select

# Load conversation with all messages
conversation = session.exec(
    select(Conversation)
    .where(Conversation.id == conversation_id)
    .where(Conversation.user_id == user_id)  # Security filter
).first()

if conversation:
    messages = session.exec(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
    ).all()
```

**Performance**: ~50ms with proper indexing (composite index on conversation_id, created_at)

### Create New Conversation

**Use Case**: User starts new chat session

**Query**:
```python
conversation = Conversation(user_id=user_id)
session.add(conversation)
session.commit()
session.refresh(conversation)
```

**Performance**: ~50ms

### Add Message to Conversation

**Use Case**: Persist user message or assistant response

**Query**:
```python
message = Message(
    conversation_id=conversation_id,
    user_id=user_id,
    role=MessageRole.USER,
    content=content
)
session.add(message)

# Update conversation timestamp
conversation.updated_at = datetime.utcnow()
session.add(conversation)

session.commit()
```

**Performance**: ~50ms (single transaction)

### List User Conversations

**Use Case**: Show conversation history to user (future feature)

**Query**:
```python
conversations = session.exec(
    select(Conversation)
    .where(Conversation.user_id == user_id)
    .order_by(Conversation.updated_at.desc())
    .limit(50)
).all()
```

**Performance**: ~30ms with index on (user_id, updated_at)

---

## Data Integrity

### Constraints

1. **Foreign Key Constraints**: Ensure referential integrity
   - `conversations.user_id` → `users.id` (CASCADE DELETE)
   - `messages.conversation_id` → `conversations.id` (CASCADE DELETE)
   - `messages.user_id` → `users.id` (CASCADE DELETE)

2. **Check Constraints**:
   - `messages.role` IN ('user', 'assistant')
   - `messages.content` length <= 10,000 characters

3. **Not Null Constraints**: All fields except `id` are NOT NULL

### Security Filters

**Critical**: Always filter by `user_id` from JWT when querying conversations or messages

```python
# CORRECT: Filter by authenticated user_id
conversation = session.exec(
    select(Conversation)
    .where(Conversation.id == conversation_id)
    .where(Conversation.user_id == user_id_from_jwt)  # Security filter
).first()

# WRONG: No user_id filter (security vulnerability)
conversation = session.exec(
    select(Conversation)
    .where(Conversation.id == conversation_id)
).first()
```

---

## Performance Considerations

### Indexing Strategy

1. **Primary Keys**: Auto-indexed
2. **Foreign Keys**: Indexed for join performance
3. **Composite Index**: `(conversation_id, created_at)` for efficient message loading
4. **Timestamp Indexes**: For sorting and filtering by date

### Expected Data Volume

- **Conversations**: ~1,000 per user (over lifetime)
- **Messages**: ~50 per conversation (average)
- **Total Messages**: ~50,000 per user (over lifetime)
- **Database Size**: ~100MB per 1,000 users (estimated)

### Optimization Strategies

1. **Pagination**: Limit message loading to last 50 messages
2. **Lazy Loading**: Load messages only when needed
3. **Connection Pooling**: Reuse database connections
4. **Query Optimization**: Use composite indexes for common queries

---

## Testing Strategy

### Unit Tests

1. **Model Creation**: Test Conversation and Message creation
2. **Relationships**: Test User-Conversation-Message relationships
3. **Validation**: Test field constraints and validation rules
4. **Queries**: Test query patterns for correctness

### Integration Tests

1. **Migration**: Test database migration up/down
2. **Conversation Flow**: Test create conversation → add messages → load history
3. **Security**: Test user_id filtering prevents cross-user access
4. **Performance**: Test query performance with realistic data volumes

---

## Next Steps

1. Create API contracts (OpenAPI spec for POST /api/chat)
2. Write quickstart guide for database setup
3. Implement models in backend/app/models/
4. Create migration script in alembic/versions/
5. Proceed to Phase 2: Tasks generation
