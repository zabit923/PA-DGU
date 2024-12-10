import logging

from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from starlette.websockets import WebSocket, WebSocketDisconnect

from core.database import get_async_session
from core.database.models import Group

from .managers import PersonalConnectionManager
from .schemas import MessageSchema
from .utils import authorize_websocket

logger = logging.Logger(__name__)

router = APIRouter(prefix="/chats")
manager = PersonalConnectionManager()


@router.websocket("/groups/{group_id}")
async def websocket_endpoint(
    group_id: int,
    websocket: WebSocket,
    session: AsyncSession = Depends(get_async_session),
):
    user = await authorize_websocket(websocket)
    statement = select(Group).where(Group.id == group_id)
    result = await session.execute(statement)
    group = result.scalars().first()
    if not group:
        await websocket.close(code=4001)
        return logger.info("Group not found.")
    if not user:
        await websocket.close(code=4001)
        return logger.info("User not found.")

    await manager.connect(group_id, websocket)
    await manager.broadcast(group_id, "{user.username} joined the chat.")
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
    finally:
        if websocket.client_state == "CONNECTED":
            await websocket.close(code=4001)
