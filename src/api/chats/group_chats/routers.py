from typing import List

from fastapi import APIRouter, Depends, HTTPException, WebSocketException, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.websockets import WebSocket, WebSocketDisconnect

from api.chats.dependencies import authorize_websocket
from api.groups.service import GroupService
from api.notifications.service import NotificationService
from api.users.routers import get_current_user
from core.database import get_async_session
from core.database.models import User

from .managers import GroupConnectionManager
from .schemas import GroupMessageCreate, GroupMessageRead, GroupMessageUpdate
from .service import GroupMessageService

router = APIRouter(prefix="/groups")

manager = GroupConnectionManager()

group_service = GroupService()
message_service = GroupMessageService()
notification_service = NotificationService()


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
                message_data = await websocket.receive_json()
                if "action" in message_data and message_data["action"] == "typing":
                    is_typing = message_data.get("is_typing", False)
                    await manager.notify_typing_status(
                        group_id, user.username, is_typing
                    )
                    continue
                message_data = GroupMessageCreate(**message_data)
                message = await message_service.create_message(
                    message_data, user, group_id, session
                )
                await notification_service.create_group_message_notification(
                    message, session
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


@router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_message(
    message_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    message = await message_service.get_message_by_id(message_id, session)
    if message.sender != user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete this message.",
        )
    await message_service.delete_message(message, session)
    await manager.notify_deletion(message.group_id, message_id)
    return {"detail": "Message deleted successfully."}


@router.patch(
    "/{message_id}",
    status_code=status.HTTP_200_OK,
    response_model=GroupMessageRead,
)
async def update_message(
    message_id: int,
    message_data: GroupMessageUpdate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    message = await message_service.get_message_by_id(message_id, session)
    if message.sender != user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete this message.",
        )
    updated_message = await message_service.update_message(
        message, message_data, session
    )
    await manager.notify_update(message.group_id, message_id)
    return updated_message
