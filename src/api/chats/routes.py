import logging

from fastapi import APIRouter
from starlette.websockets import WebSocket, WebSocketDisconnect

from .managers import ConnectionManager
from .schemas import MessageSchema
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
                raw_data = await websocket.receive_json()
                try:
                    data = MessageSchema(**raw_data)
                except ValueError as e:
                    await websocket.send_text(f"Invalid message format: {e}")
                    continue
                if data.recipient:
                    await manager.send_personal_message(
                        f"{user.username}: {data.message}", data.recipient
                    )
                else:
                    await manager.broadcast(f"{user.username}: {data.message}")
        except WebSocketDisconnect:
            manager.disconnect(user.username)
            await manager.broadcast(f"{user.username} left the chat.")
    await websocket.close(code=4001)
