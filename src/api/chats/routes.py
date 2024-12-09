import logging

from fastapi import APIRouter
from starlette.websockets import WebSocket, WebSocketDisconnect

from .managers import ConnectionManager
from .utils import authorize_websocket

logger = logging.Logger(__name__)

router = APIRouter(prefix="/chats")
manager = ConnectionManager()


@router.websocket("/test")
async def websocket_endpoint(websocket: WebSocket):
    user = await authorize_websocket(websocket)
    if user:
        await manager.connect(websocket, user.username)
        await manager.broadcast(f"{user.username} joined the chat.")
        try:
            while True:
                data = await websocket.receive_json()
                recipient = data.get("recipient")
                message = data.get("message")
                if recipient:
                    await manager.send_personal_message(
                        f"{user.username}: {message}", recipient
                    )
                else:
                    await manager.broadcast(f"{user.username}: {message}")
        except WebSocketDisconnect:
            manager.disconnect(user.username)
            await manager.broadcast(f"{user.username} left the chat.")
