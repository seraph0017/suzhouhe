"""
WebSocket Manager for real-time communication
"""

import json
import asyncio
from typing import Dict, Set, Any
from fastapi import WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """WebSocket connection manager"""

    def __init__(self):
        # Active connections: {user_id: {connection_id: websocket}}
        self.active_connections: Dict[int, Dict[str, WebSocket]] = {}
        # Room subscriptions: {room: {user_id: set}}
        self.rooms: Dict[str, Set[int]] = {}

    async def connect(self, websocket: WebSocket, user_id: int, connection_id: str) -> str:
        """Accept and register a new connection"""
        await websocket.accept()

        # Register connection
        if user_id not in self.active_connections:
            self.active_connections[user_id] = {}
        self.active_connections[user_id][connection_id] = websocket

        logger.info(f"New WebSocket connection: user_id={user_id}, connection_id={connection_id}")
        return connection_id

    def disconnect(self, user_id: int, connection_id: str):
        """Remove a connection"""
        if user_id in self.active_connections:
            if connection_id in self.active_connections[user_id]:
                del self.active_connections[user_id][connection_id]
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

        # Remove from rooms
        for room in list(self.rooms.keys()):
            if user_id in self.rooms[room]:
                self.rooms[room].discard(user_id)
                if not self.rooms[room]:
                    del self.rooms[room]

        logger.info(f"WebSocket disconnected: user_id={user_id}, connection_id={connection_id}")

    async def send_personal(self, user_id: int, message: dict):
        """Send message to a specific user (all their connections)"""
        if user_id not in self.active_connections:
            return

        message_str = json.dumps(message)
        disconnected = []

        for connection_id, websocket in self.active_connections[user_id].items():
            try:
                if websocket.client_state == WebSocketState.CONNECTED:
                    await websocket.send_text(message_str)
                else:
                    disconnected.append(connection_id)
            except Exception as e:
                logger.error(f"Error sending message to user {user_id}: {e}")
                disconnected.append(connection_id)

        # Clean up disconnected clients
        for connection_id in disconnected:
            self.disconnect(user_id, connection_id)

    async def send_to_room(self, room: str, message: dict):
        """Send message to all users in a room"""
        if room not in self.rooms:
            return

        message_str = json.dumps(message)
        for user_id in self.rooms[room]:
            await self.send_personal(user_id, message)

    async def broadcast(self, message: dict):
        """Broadcast message to all connected users"""
        message_str = json.dumps(message)
        for user_id in list(self.active_connections.keys()):
            await self.send_personal(user_id, message)

    def join_room(self, user_id: int, room: str):
        """Join a room"""
        if room not in self.rooms:
            self.rooms[room] = set()
        self.rooms[room].add(user_id)
        logger.info(f"User {user_id} joined room {room}")

    def leave_room(self, user_id: int, room: str):
        """Leave a room"""
        if room in self.rooms and user_id in self.rooms[room]:
            self.rooms[room].discard(user_id)
            if not self.rooms[room]:
                del self.rooms[room]
            logger.info(f"User {user_id} left room {room}")


# Global connection manager
manager = ConnectionManager()


class WebSocketMessage:
    """WebSocket message types and utilities"""

    # Message types
    CONNECTION_INIT = "CONNECTION_INIT"
    CONNECTION_ACK = "CONNECTION_ACK"
    CONNECTION_ERROR = "CONNECTION_ERROR"

    PROGRESS_UPDATE = "PROGRESS_UPDATE"
    TASK_COMPLETE = "TASK_COMPLETE"
    TASK_ERROR = "TASK_ERROR"

    NOTIFICATION = "NOTIFICATION"

    PING = "PING"
    PONG = "PONG"

    @staticmethod
    def create_message(msg_type: str, data: dict = None, message: str = None) -> dict:
        """Create a WebSocket message"""
        msg = {
            "type": msg_type,
            "timestamp": asyncio.get_event_loop().time(),
        }
        if data:
            msg["data"] = data
        if message:
            msg["message"] = message
        return msg

    @staticmethod
    def progress_update(job_id: int, progress: int, status: str, message: str = None) -> dict:
        """Create progress update message"""
        return WebSocketMessage.create_message(
            WebSocketMessage.PROGRESS_UPDATE,
            {
                "job_id": job_id,
                "progress": progress,
                "status": status,
            },
            message
        )

    @staticmethod
    def task_complete(job_id: int, result: dict = None) -> dict:
        """Create task complete message"""
        return WebSocketMessage.create_message(
            WebSocketMessage.TASK_COMPLETE,
            {
                "job_id": job_id,
                "result": result,
            }
        )

    @staticmethod
    def task_error(job_id: int, error: str) -> dict:
        """Create task error message"""
        return WebSocketMessage.create_message(
            WebSocketMessage.TASK_ERROR,
            {
                "job_id": job_id,
                "error": error,
            }
        )

    @staticmethod
    def notification(title: str, content: str, level: str = "info") -> dict:
        """Create notification message"""
        return WebSocketMessage.create_message(
            WebSocketMessage.NOTIFICATION,
            {
                "title": title,
                "content": content,
                "level": level,
            }
        )

    @staticmethod
    def connection_ack(connection_id: str, user_id: int) -> dict:
        """Create connection acknowledgment message"""
        return WebSocketMessage.create_message(
            WebSocketMessage.CONNECTION_ACK,
            {
                "connection_id": connection_id,
                "user_id": user_id,
            }
        )

    @staticmethod
    def pong() -> dict:
        """Create PONG response"""
        return WebSocketMessage.create_message(WebSocketMessage.PONG)
