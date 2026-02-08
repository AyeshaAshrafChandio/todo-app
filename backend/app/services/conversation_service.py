"""
ConversationService for managing chat conversations and messages.

This service provides CRUD operations for conversations and messages,
supporting the stateless AI Chat Backend architecture (Spec 005).
"""

from datetime import datetime
from typing import Optional, List
from sqlmodel import Session, select
from app.models.conversation import Conversation
from app.models.message import Message, MessageRole


class ConversationService:
    """
    Service for managing conversations and messages.

    This service handles:
    - Creating new conversations
    - Loading existing conversations with message history
    - Adding messages to conversations
    - Updating conversation timestamps
    """

    def __init__(self, session: Session):
        """
        Initialize the conversation service.

        Args:
            session: SQLModel database session
        """
        self.session = session

    def create_conversation(self, user_id: str) -> Conversation:
        """
        Create a new conversation for a user.

        Args:
            user_id: UUID of the user creating the conversation

        Returns:
            Newly created Conversation object

        Example:
            ```python
            conversation = service.create_conversation(user_id="550e8400-...")
            print(f"Created conversation {conversation.id}")
            ```
        """
        conversation = Conversation(user_id=user_id)
        self.session.add(conversation)
        self.session.commit()
        self.session.refresh(conversation)
        return conversation

    def get_conversation(
        self,
        conversation_id: int,
        user_id: str
    ) -> Optional[Conversation]:
        """
        Get a conversation by ID, ensuring it belongs to the user.

        Args:
            conversation_id: ID of the conversation to retrieve
            user_id: UUID of the user (for security filtering)

        Returns:
            Conversation object if found and belongs to user, None otherwise

        Security:
            Always filters by user_id to prevent cross-user access

        Example:
            ```python
            conversation = service.get_conversation(
                conversation_id=1,
                user_id="550e8400-..."
            )
            if conversation:
                print(f"Found conversation with {len(conversation.messages)} messages")
            ```
        """
        statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
        return self.session.exec(statement).first()

    def load_messages(
        self,
        conversation_id: int,
        limit: Optional[int] = None
    ) -> List[Message]:
        """
        Load messages for a conversation, ordered chronologically.

        Args:
            conversation_id: ID of the conversation
            limit: Optional limit on number of messages to load (most recent)

        Returns:
            List of Message objects ordered by created_at ascending

        Performance:
            Uses composite index on (conversation_id, created_at) for efficiency

        Example:
            ```python
            # Load last 50 messages
            messages = service.load_messages(conversation_id=1, limit=50)
            for msg in messages:
                print(f"{msg.role}: {msg.content}")
            ```
        """
        statement = select(Message).where(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.asc())

        if limit:
            # Get total count first
            count_statement = select(Message).where(
                Message.conversation_id == conversation_id
            )
            total_messages = len(self.session.exec(count_statement).all())

            # If we have more messages than limit, skip oldest ones
            if total_messages > limit:
                offset = total_messages - limit
                statement = statement.offset(offset)

            statement = statement.limit(limit)

        return list(self.session.exec(statement).all())

    def add_message(
        self,
        conversation_id: int,
        user_id: str,
        role: MessageRole,
        content: str
    ) -> Message:
        """
        Add a message to a conversation and update conversation timestamp.

        Args:
            conversation_id: ID of the conversation
            user_id: UUID of the user (conversation owner)
            role: Message sender role (USER or ASSISTANT)
            content: Message content text

        Returns:
            Newly created Message object

        Side Effects:
            Updates conversation.updated_at timestamp

        Example:
            ```python
            # Add user message
            message = service.add_message(
                conversation_id=1,
                user_id="550e8400-...",
                role=MessageRole.USER,
                content="Add buy groceries to my list"
            )
            ```
        """
        # Create message
        message = Message(
            conversation_id=conversation_id,
            user_id=user_id,
            role=role,
            content=content
        )
        self.session.add(message)

        # Update conversation timestamp
        conversation = self.session.get(Conversation, conversation_id)
        if conversation:
            conversation.updated_at = datetime.utcnow()
            self.session.add(conversation)

        self.session.commit()
        self.session.refresh(message)
        return message

    def get_user_conversations(
        self,
        user_id: str,
        limit: int = 50
    ) -> List[Conversation]:
        """
        Get all conversations for a user, ordered by most recent activity.

        Args:
            user_id: UUID of the user
            limit: Maximum number of conversations to return (default 50)

        Returns:
            List of Conversation objects ordered by updated_at descending

        Example:
            ```python
            conversations = service.get_user_conversations(user_id="550e8400-...")
            for conv in conversations:
                print(f"Conversation {conv.id}: {conv.updated_at}")
            ```
        """
        statement = select(Conversation).where(
            Conversation.user_id == user_id
        ).order_by(Conversation.updated_at.desc()).limit(limit)

        return list(self.session.exec(statement).all())
