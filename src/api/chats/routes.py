import logging

from fastapi import APIRouter
from starlette.websockets import WebSocket, WebSocketDisconnect

logger = logging.Logger(__name__)

router = APIRouter(prefix="/chats")


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        logger.info("Client disconnected")
