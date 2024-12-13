import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, WebSocketException, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.websockets import WebSocket, WebSocketDisconnect

from api.chats.dependencies import authorize_websocket
from api.groups.service import GroupService
from api.users.routes import get_current_user
from core.database import get_async_session
from core.database.models import User

from .managers import GroupConnectionManager
from .schemas import GroupMessageCreate, GroupMessageRead
from .service import GroupMessageService

logger = logging.Logger(__name__)
router = APIRouter(prefix="/groups")

manager = GroupConnectionManager()
group_service = GroupService()
message_service = GroupMessageService()


@router.websocket("/{group_id}")
async def group_chat_websocket(
    group_id: int,
    websocket: WebSocket,
    user: User = Depends(authorize_websocket),
    session: AsyncSession = Depends(get_async_session),
):
    group = await group_service.get_group(group_id, session)
    if not group:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION, reason="Group not found."
        )
    if user not in group.members:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="User not member of this group.",
        )
    await manager.connect(group_id, user.username, websocket)
    try:
        while True:
            try:
                message_data = GroupMessageCreate(**await websocket.receive_json())
                message = await message_service.create_message(
                    message_data, user, group_id, session
                )
                message = GroupMessageRead.model_validate(message).model_dump(
                    mode="json"
                )
                await manager.broadcast(group_id, message, user.username)
            except ValueError as e:
                await websocket.send_text(f"Invalid message format: {e}")
                continue
    except WebSocketDisconnect:
        manager.disconnect(group_id, user.username)
    finally:
        if websocket.client_state == "CONNECTED":
            await websocket.close(code=status.WS_1000_NORMAL_CLOSURE)


@router.get(
    "/{group_id}",
    status_code=status.HTTP_200_OK,
    response_model=List[GroupMessageRead],
)
async def get_messages(
    group_id: int,
    offset: int = 0,
    limit: int = 50,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> List[GroupMessageRead]:
    group = await group_service.get_group(group_id, session)
    if user not in group.members:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not member of this group.",
        )
    messages = await message_service.get_messages(group, offset, limit, session)
    return messages
