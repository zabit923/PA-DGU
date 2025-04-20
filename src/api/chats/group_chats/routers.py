import logging
from json import JSONDecodeError
from typing import List

from fastapi import APIRouter, Depends, WebSocketException, status
from starlette.websockets import WebSocket, WebSocketDisconnect

from api.chats.dependencies import authorize_websocket
from api.groups.service import GroupService, group_service_factory
from api.notifications.service import NotificationService, notification_service_factory
from api.users.routers import get_current_user
from core.database.models import User
from core.managers.group_websocket_manager import GroupConnectionManager

from .schemas import GroupMessageCreate, GroupMessageRead, GroupMessageUpdate
from .service import GroupChatService, group_chat_service_factory

router = APIRouter(prefix="/groups")

logger = logging.getLogger(__name__)
manager = GroupConnectionManager()


@router.websocket("/{group_id}")
async def group_chat_websocket(
    group_id: int,
    websocket: WebSocket,
    user: User = Depends(authorize_websocket),
    chat_service: GroupChatService = Depends(group_chat_service_factory),
    group_service: GroupService = Depends(group_service_factory),
    notification_service: NotificationService = Depends(notification_service_factory),
):
    group = await group_service.get_group(group_id)
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
    await chat_service.update_online_status(user)
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
                message = await chat_service.create_message(
                    message_data, user, group_id
                )
                await notification_service.create_group_message_notification(
                    message, chat_service
                )
                message = GroupMessageRead.model_validate(message).model_dump(
                    mode="json"
                )
                await manager.broadcast(group_id, message, user.username)
            except (JSONDecodeError, AttributeError) as e:
                logger.exception(f"Websocket error, detail: {e}")
                await manager.send_error("Wrong message format", websocket)
                continue
            except ValueError as e:
                logger.exception(f"Websocket error, detail: {e}")
                await manager.send_error(
                    "Could not validate incoming message", websocket
                )
    except WebSocketDisconnect:
        await chat_service.update_online_status(user)
        logging.info("Websocket is disconnected")
        manager.disconnect(group_id, user.username)


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
    chat_service: GroupChatService = Depends(group_chat_service_factory),
    group_service: GroupService = Depends(group_service_factory),
) -> List[GroupMessageRead]:
    group = await group_service.get_group(group_id)
    messages = await chat_service.get_messages(group, user, offset, limit)
    return messages


@router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_message(
    message_id: int,
    user: User = Depends(get_current_user),
    chat_service: GroupChatService = Depends(group_chat_service_factory),
):
    message = await chat_service.get_message_by_id(message_id)
    await chat_service.delete_message(message, user)
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
    chat_service: GroupChatService = Depends(group_chat_service_factory),
):
    message = await chat_service.get_message_by_id(message_id)
    updated_message = await chat_service.update_message(message, message_data, user)
    await manager.notify_update(message.group_id, message_id)
    return updated_message
