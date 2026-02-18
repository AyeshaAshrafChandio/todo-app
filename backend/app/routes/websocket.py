"""
WebSocket API routes for real-time task updates.

This module implements the WebSocket endpoint for real-time communication:
- GET /api/ws: WebSocket connection endpoint with JWT authentication

The WebSocket connection accepts JWT tokens for authentication and broadcasts
task events (created, updated, completed, deleted, shared) to connected clients.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends, status
from sqlmodel import Session, select
import jwt
import logging
from typing import Optional

from app.config import settings
from app.database.connection import get_db
from app.services.websocket_manager import websocket_manager
from app.models.team_member import TeamMember

logger = logging.getLogger(__name__)

# Create router with /api prefix
router = APIRouter(
    prefix="/api",
    tags=["WebSocket"],
)


async def authenticate_websocket(token: str, db: Session) -> Optional[str]:
    """
    Authenticate WebSocket connection using JWT token.

    Args:
        token: JWT token from query parameter or first message
        db: Database session for user verification

    Returns:
        str: User ID if authentication successful, None otherwise
    """
    try:
        # Decode JWT token
        payload = jwt.decode(
            token,
            settings.BETTER_AUTH_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )

        # Extract user_id from token
        user_id = payload.get("sub")
        if not user_id:
            logger.warning("JWT token missing 'sub' claim")
            return None

        logger.info(f"WebSocket authenticated: user_id={user_id}")
        return user_id

    except jwt.ExpiredSignatureError:
        logger.warning("WebSocket authentication failed: token expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"WebSocket authentication failed: invalid token - {e}")
        return None
    except Exception as e:
        logger.error(f"WebSocket authentication error: {e}")
        return None


async def get_user_teams(db: Session, user_id: str) -> list[str]:
    """
    Get list of team IDs that user belongs to.

    Args:
        db: Database session
        user_id: User identifier

    Returns:
        list[str]: List of team IDs
    """
    try:
        statement = select(TeamMember.team_id).where(TeamMember.user_id == user_id)
        team_ids = db.exec(statement).all()
        return list(team_ids)
    except Exception as e:
        logger.error(f"Error fetching user teams: {e}")
        return []


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(None, description="JWT authentication token"),
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for real-time task updates.

    This endpoint establishes a WebSocket connection for real-time communication.
    Clients must authenticate using a JWT token provided as a query parameter.

    **Authentication:**
    - JWT token must be provided in query parameter: ws://host/api/ws?token=<jwt>
    - Token is validated using BETTER_AUTH_SECRET
    - Connection is rejected if token is invalid or expired

    **Connection Flow:**
    1. Client connects with JWT token
    2. Server validates token and extracts user_id
    3. Server sends connection_ack message
    4. Server broadcasts task events to client
    5. Client can send ping messages to keep connection alive

    **Event Types:**
    - connection_ack: Sent when connection is established
    - task_created: Sent when a task is created
    - task_updated: Sent when a task is updated
    - task_completed: Sent when a task is marked complete
    - task_reopened: Sent when a task is reopened
    - task_deleted: Sent when a task is deleted
    - task_shared: Sent when a task is shared with user
    - error: Sent when an error occurs

    **Message Format:**
    ```json
    {
        "event_type": "task_created",
        "timestamp": "2024-01-01T12:00:00",
        "data": {
            "task_id": 123,
            "user_id": "user123",
            "team_id": "team456"
        }
    }
    ```

    Args:
        websocket: WebSocket connection instance
        token: JWT authentication token from query parameter
        db: Database session dependency

    Example:
        ```javascript
        const ws = new WebSocket('ws://localhost:8000/api/ws?token=<jwt>');
        ws.onmessage = (event) => {
            const message = JSON.parse(event.data);
            console.log('Received:', message.event_type);
        };
        ```
    """
    user_id = None

    try:
        # Authenticate using token from query parameter
        if not token:
            logger.warning("WebSocket connection rejected: no token provided")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        user_id = await authenticate_websocket(token, db)
        if not user_id:
            logger.warning("WebSocket connection rejected: authentication failed")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        # Get user's team memberships for team broadcasts
        team_ids = await get_user_teams(db, user_id)

        # Register connection with WebSocket manager
        await websocket_manager.connect(websocket, user_id, team_ids)

        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Wait for messages from client
                data = await websocket.receive_text()

                # Handle ping messages to keep connection alive
                if data == "ping":
                    await websocket.send_text("pong")
                    continue

                # Handle other message types if needed
                logger.debug(f"Received message from user {user_id}: {data}")

            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected: user_id={user_id}")
                break
            except Exception as e:
                logger.error(f"Error handling WebSocket message: {e}")
                # Send error message to client
                await websocket.send_json({
                    "event_type": "error",
                    "timestamp": "",
                    "data": {
                        "message": "Error processing message"
                    }
                })

    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
    finally:
        # Clean up connection
        if user_id:
            websocket_manager.disconnect(websocket, user_id)
            logger.info(f"WebSocket connection closed: user_id={user_id}")
