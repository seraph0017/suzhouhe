"""
WebSocket API router
"""

import uuid
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.utils.security import decode_token
from app.services.websocket import manager, WebSocketMessage
from app.utils.audit_logger import log_audit_action

router = APIRouter()


@router.websocket("/ws/notifications")
async def websocket_notifications(
    websocket: WebSocket,
    db: Session = Depends(get_db),
):
    """
    WebSocket endpoint for real-time notifications and progress updates

    Connection handshake:
    1. Client connects with token in query params
    2. Server validates token and accepts connection
    3. Client sends CONNECTION_INIT with connection_id
    4. Server responds with CONNECTION_ACK
    5. Heartbeat: Client sends PING every 30s, Server responds with PONG
    """
    # Validate token from query params
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4001, reason="Missing token")
        return

    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        await websocket.close(code=4002, reason="Invalid token")
        return

    user_id = payload.get("sub")
    if not user_id:
        await websocket.close(code=4003, reason="Invalid token payload")
        return

    # Verify user exists and is active
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        await websocket.close(code=4004, reason="User not found or inactive")
        return

    # Accept connection
    connection_id = str(uuid.uuid4())
    await manager.connect(websocket, user_id, connection_id)

    # Send connection acknowledgment
    await websocket.send_json(WebSocketMessage.connection_ack(connection_id, user_id))

    # Auto-join user's project rooms
    for project in user.projects_led:
        manager.join_room(user_id, f"project:{project.id}")
    for membership in user.project_memberships:
        manager.join_room(user_id, f"project:{membership.project_id}")

    # Log audit action
    log_audit_action(
        db=db,
        user_id=user_id,
        action="WEBSOCKET_CONNECT",
        entity_type="WEBSOCKET",
        ip_address=websocket.client.host if websocket.client else None,
    )

    try:
        while True:
            # Wait for messages (PING or custom events)
            try:
                data = await websocket.receive_json()
                msg_type = data.get("type")

                if msg_type == "PING":
                    # Respond with PONG
                    await websocket.send_json(WebSocketMessage.pong())

                elif msg_type == "JOIN_ROOM":
                    # Join a specific room
                    room = data.get("room")
                    if room:
                        manager.join_room(user_id, room)

                elif msg_type == "LEAVE_ROOM":
                    # Leave a specific room
                    room = data.get("room")
                    if room:
                        manager.leave_room(user_id, room)

            except WebSocketDisconnect:
                break
            except Exception as e:
                # Log error but keep connection alive
                print(f"WebSocket error: {e}")

    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(user_id, connection_id)
        log_audit_action(
            db=db,
            user_id=user_id,
            action="WEBSOCKET_DISCONNECT",
            entity_type="WEBSOCKET",
        )


@router.get("/connections")
async def list_connections(
    current_user: User = Depends(lambda: None),  # Placeholder for auth
):
    """List active WebSocket connections (for debugging)"""
    return {
        "total_users": len(manager.active_connections),
        "total_rooms": len(manager.rooms),
        "connections": {
            user_id: list(connections.keys())
            for user_id, connections in manager.active_connections.items()
        }
    }
