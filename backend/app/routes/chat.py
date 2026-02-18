"""
Chat API routes for AI-powered task management.

This module provides the POST /api/chat endpoint for natural language
task management via AI agent (Spec 005).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
import logging

from app.database.connection import get_db
from app.middleware.auth import get_current_user
from app.models.message import MessageRole
from typing import Dict
from app.schemas.chat import ChatRequest, ChatResponse, ToolCall
from app.services.conversation_service import ConversationService
from app.services.agent_service import AgentService
from app.services.mock_agent_service import MockAgentService
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post(
    "",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Send a chat message to the AI assistant",
    description="""
    Send a message to the AI assistant for natural language task management.

    The assistant can:
    - Create tasks from natural language descriptions
    - List and search tasks
    - Update task details and completion status
    - Delete tasks

    **Authentication**: Requires valid JWT token in Authorization header.

    **Conversation Management**:
    - Pass `conversation_id: null` to start a new conversation
    - Pass existing `conversation_id` to continue a conversation
    - The response includes `conversation_id` for subsequent messages

    **Stateless Architecture**:
    - All conversation context is loaded from database per request
    - No server-side session state is maintained
    - Conversations can be resumed after server restarts

    **Tool Transparency**:
    - The response includes `tool_calls` array showing which tools were invoked
    - This provides transparency into agent actions
    """,
    responses={
        200: {
            "description": "Successful response from AI assistant",
            "content": {
                "application/json": {
                    "example": {
                        "conversation_id": 1,
                        "response": "I've added 'buy groceries' to your task list.",
                        "tool_calls": [
                            {
                                "tool": "create_task",
                                "arguments": {
                                    "title": "buy groceries",
                                    "description": "Purchase groceries from the store"
                                }
                            }
                        ]
                    }
                }
            }
        },
        400: {
            "description": "Bad request - invalid input",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Message too long (max 10,000 characters)"
                    }
                }
            }
        },
        401: {
            "description": "Unauthorized - missing or invalid JWT token",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Not authenticated"
                    }
                }
            }
        },
        403: {
            "description": "Forbidden - conversation belongs to another user",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Conversation not found or access denied"
                    }
                }
            }
        },
        500: {
            "description": "Internal server error - agent or tool failure",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "An error occurred processing your request. Please try again."
                    }
                }
            }
        }
    }
)
async def chat(
    request: ChatRequest,
    current_user: Dict[str, str] = Depends(get_current_user),
    session: Session = Depends(get_db)
) -> ChatResponse:
    """
    Process a chat message and return AI assistant response.

    Args:
        request: Chat request with conversation_id and message
        current_user: Authenticated user from JWT token
        session: Database session

    Returns:
        ChatResponse with conversation_id, response, and tool_calls

    Raises:
        HTTPException 400: Invalid input (message too long, etc.)
        HTTPException 403: Conversation access denied
        HTTPException 500: Agent or tool execution failure
    """
    try:
        # Initialize services
        conversation_service = ConversationService(session)

        # Use mock service if enabled, otherwise use real OpenAI service
        if settings.MOCK_OPENAI:
            agent_service = MockAgentService()
            logger.info(
                "Using MockAgentService (MOCK_OPENAI=true)",
                extra={"user_id": current_user["user_id"]}
            )
        else:
            agent_service = AgentService()
            logger.info(
                "Using real AgentService with OpenAI API",
                extra={"user_id": current_user["user_id"]}
            )

        # Get or create conversation
        if request.conversation_id is None:
            # Create new conversation
            logger.info(
                f"Creating new conversation for user {current_user['user_id']}",
                extra={"user_id": current_user["user_id"]}
            )
            conversation = conversation_service.create_conversation(
                user_id=current_user["user_id"]
            )
        else:
            # Load existing conversation
            logger.info(
                f"Loading conversation {request.conversation_id} for user {current_user['user_id']}",
                extra={
                    "user_id": current_user["user_id"],
                    "conversation_id": request.conversation_id
                }
            )
            conversation = conversation_service.get_conversation(
                conversation_id=request.conversation_id,
                user_id=current_user["user_id"]
            )

            if not conversation:
                logger.warning(
                    f"Conversation {request.conversation_id} not found or access denied",
                    extra={
                        "user_id": current_user["user_id"],
                        "conversation_id": request.conversation_id
                    }
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Conversation not found or access denied"
                )

        # Persist user message
        logger.info(
            f"Adding user message to conversation {conversation.id}",
            extra={
                "user_id": current_user["user_id"],
                "conversation_id": conversation.id,
                "message_length": len(request.message)
            }
        )
        conversation_service.add_message(
            conversation_id=conversation.id,
            user_id=current_user["user_id"],
            role=MessageRole.USER,
            content=request.message
        )

        # Load conversation history for agent context
        conversation_history = conversation_service.load_messages(
            conversation_id=conversation.id,
            limit=50  # Load last 50 messages for context
        )

        # Run agent to process message
        logger.info(
            f"Running agent for conversation {conversation.id}",
            extra={
                "user_id": current_user["user_id"],
                "conversation_id": conversation.id,
                "history_length": len(conversation_history)
            }
        )
        assistant_response, tool_calls = await agent_service.run_agent(
            user_message=request.message,
            conversation_history=conversation_history[:-1],  # Exclude the message we just added
            user_id=current_user["user_id"]
        )

        # Persist assistant response
        logger.info(
            f"Adding assistant response to conversation {conversation.id}",
            extra={
                "user_id": current_user["user_id"],
                "conversation_id": conversation.id,
                "tool_calls_count": len(tool_calls)
            }
        )
        conversation_service.add_message(
            conversation_id=conversation.id,
            user_id=current_user["user_id"],
            role=MessageRole.ASSISTANT,
            content=assistant_response
        )

        # Return response
        return ChatResponse(
            conversation_id=conversation.id,
            response=assistant_response,
            tool_calls=[
                ToolCall(tool=tc["tool"], arguments=tc["arguments"])
                for tc in tool_calls
            ]
        )

    except HTTPException:
        # Re-raise HTTP exceptions (403, etc.)
        raise

    except ValueError as e:
        # Validation errors
        logger.error(
            f"Validation error: {str(e)}",
            extra={"user_id": current_user["user_id"], "error": str(e)}
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except Exception as e:
        # Catch-all for unexpected errors
        logger.error(
            f"Chat endpoint error: {str(e)}",
            extra={"user_id": current_user["user_id"], "error": str(e)},
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred processing your request. Please try again."
        )
