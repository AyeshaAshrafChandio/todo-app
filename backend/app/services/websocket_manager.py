"""
WebSocket Manager Service for Real-Time Updates.

This module manages WebSocket connections, tracks active clients,
and broadcasts events to connected users for real-time task updates.
"""

from typing import Dict, List, Set
from datetime import datetime
from fastapi import WebSocket
import json
import logging

logger = logging.getLogger(__name__)


class WebSocketManager:
    """
    Manages WebSocket connections and event broadcasting.

    This class maintains a registry of active WebSocket connections
    organized by user_id, and provides methods to broadcast events
    to specific users or teams.

    Attributes:
        active_connections: Dict mapping user_id to list of WebSocket connections
        user_teams: Dict mapping user_id to set of team_ids for team broadcasts
    """

    def __init__(self):
        """Initialize the WebSocket manager with empty connection registry."""
        # Map user_id -> list of WebSocket connections
        self.active_connections: Dict[str, List[WebSocket]] = {}

        # Map user_id -> set of team_ids (for team broadcasts)
        self.user_teams: Dict[str, Set[str]] = {}

        logger.info("WebSocket manager initialized")

    async def connect(self, websocket: WebSocket, user_id: str, team_ids: List[str] = None):
        """
        Register a new WebSocket connection for a user.

        Args:
            websocket: WebSocket connection instance
            user_id: User identifier
            team_ids: Optional list of team IDs the user belongs to
        """
        await websocket.accept()

        # Add connection to user's connection list
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)

        # Store user's team memberships for team broadcasts
        if team_ids:
            self.user_teams[user_id] = set(team_ids)

        logger.info(f"WebSocket connected: user_id={user_id}, total_connections={len(self.active_connections[user_id])}")

        # Send connection acknowledgment
        await self.send_to_user(user_id, {
            "event_type": "connection_ack",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "user_id": user_id,
                "message": "WebSocket connection established"
            }
        })

    def disconnect(self, websocket: WebSocket, user_id: str):
        """
        Remove a WebSocket connection for a user.

        Args:
            websocket: WebSocket connection instance to remove
            user_id: User identifier
        """
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
                logger.info(f"WebSocket disconnected: user_id={user_id}, remaining_connections={len(self.active_connections[user_id])}")

            # Clean up empty connection lists
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
                if user_id in self.user_teams:
                    del self.user_teams[user_id]
                logger.info(f"User {user_id} has no active connections")

    async def send_to_user(self, user_id: str, message: dict):
        """
        Send a message to all connections for a specific user.

        Args:
            user_id: User identifier
            message: Message dictionary to send (will be JSON serialized)
        """
        if user_id not in self.active_connections:
            logger.debug(f"No active connections for user {user_id}")
            return

        # Send to all connections for this user
        disconnected = []
        for websocket in self.active_connections[user_id]:
            try:
                await websocket.send_json(message)
                logger.debug(f"Sent message to user {user_id}: {message['event_type']}")
            except Exception as e:
                logger.error(f"Error sending to user {user_id}: {e}")
                disconnected.append(websocket)

        # Clean up disconnected connections
        for websocket in disconnected:
            self.disconnect(websocket, user_id)

    async def send_to_team(self, team_id: str, message: dict, exclude_user_id: str = None):
        """
        Send a message to all users in a team.

        Args:
            team_id: Team identifier
            message: Message dictionary to send
            exclude_user_id: Optional user_id to exclude from broadcast
        """
        # Find all users in this team
        team_users = [
            user_id for user_id, teams in self.user_teams.items()
            if team_id in teams and user_id != exclude_user_id
        ]

        logger.debug(f"Broadcasting to team {team_id}: {len(team_users)} users")

        # Send to each user in the team
        for user_id in team_users:
            await self.send_to_user(user_id, message)

    async def broadcast_task_created(self, task_id: int, user_id: str, team_id: str = None):
        """
        Broadcast task_created event to relevant users.

        Args:
            task_id: Created task ID
            user_id: Task creator user ID
            team_id: Optional team ID if task is team-owned
        """
        message = {
            "event_type": "task_created",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "task_id": task_id,
                "user_id": user_id,
                "team_id": team_id
            }
        }

        # Send to task creator
        await self.send_to_user(user_id, message)

        # If team task, broadcast to team members
        if team_id:
            await self.send_to_team(team_id, message, exclude_user_id=user_id)

    async def broadcast_task_updated(self, task_id: int, user_id: str, team_id: str = None):
        """
        Broadcast task_updated event to relevant users.

        Args:
            task_id: Updated task ID
            user_id: User who updated the task
            team_id: Optional team ID if task is team-owned
        """
        message = {
            "event_type": "task_updated",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "task_id": task_id,
                "user_id": user_id,
                "team_id": team_id
            }
        }

        # Send to user who updated
        await self.send_to_user(user_id, message)

        # If team task, broadcast to team members
        if team_id:
            await self.send_to_team(team_id, message, exclude_user_id=user_id)

    async def broadcast_task_completed(self, task_id: int, user_id: str, team_id: str = None):
        """
        Broadcast task_completed event to relevant users.

        Args:
            task_id: Completed task ID
            user_id: User who completed the task
            team_id: Optional team ID if task is team-owned
        """
        message = {
            "event_type": "task_completed",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "task_id": task_id,
                "user_id": user_id,
                "team_id": team_id
            }
        }

        # Send to user who completed
        await self.send_to_user(user_id, message)

        # If team task, broadcast to team members
        if team_id:
            await self.send_to_team(team_id, message, exclude_user_id=user_id)

    async def broadcast_task_reopened(self, task_id: int, user_id: str, team_id: str = None):
        """
        Broadcast task_reopened event to relevant users.

        Args:
            task_id: Reopened task ID
            user_id: User who reopened the task
            team_id: Optional team ID if task is team-owned
        """
        message = {
            "event_type": "task_reopened",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "task_id": task_id,
                "user_id": user_id,
                "team_id": team_id
            }
        }

        # Send to user who reopened
        await self.send_to_user(user_id, message)

        # If team task, broadcast to team members
        if team_id:
            await self.send_to_team(team_id, message, exclude_user_id=user_id)

    async def broadcast_task_deleted(self, task_id: int, user_id: str, team_id: str = None):
        """
        Broadcast task_deleted event to relevant users.

        Args:
            task_id: Deleted task ID
            user_id: User who deleted the task
            team_id: Optional team ID if task was team-owned
        """
        message = {
            "event_type": "task_deleted",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "task_id": task_id,
                "user_id": user_id,
                "team_id": team_id
            }
        }

        # Send to user who deleted
        await self.send_to_user(user_id, message)

        # If team task, broadcast to team members
        if team_id:
            await self.send_to_team(team_id, message, exclude_user_id=user_id)

    async def broadcast_task_shared(self, task_id: int, shared_with_user_id: str, shared_by_user_id: str):
        """
        Broadcast task_shared event to the user who received the share.

        Args:
            task_id: Shared task ID
            shared_with_user_id: User who received the share
            shared_by_user_id: User who shared the task
        """
        message = {
            "event_type": "task_shared",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "task_id": task_id,
                "shared_with_user_id": shared_with_user_id,
                "shared_by_user_id": shared_by_user_id
            }
        }

        # Send to user who received the share
        await self.send_to_user(shared_with_user_id, message)

    def get_connection_count(self) -> int:
        """
        Get total number of active WebSocket connections.

        Returns:
            int: Total number of active connections
        """
        return sum(len(connections) for connections in self.active_connections.values())

    def get_user_count(self) -> int:
        """
        Get number of users with active connections.

        Returns:
            int: Number of unique users connected
        """
        return len(self.active_connections)


# Global WebSocket manager instance
websocket_manager = WebSocketManager()
