from json import JSONDecodeError

from fastapi import Depends, WebSocketException
from starlette import status
from starlette.websockets import WebSocket, WebSocketDisconnect

from api.chats.dependencies import authorize_websocket
from api.chats.group_chats.routers import logger, router
from api.chats.group_chats.schemas import GroupMessageCreate, GroupMessageRead
from api.chats.group_chats.service import GroupChatService, group_chat_service_factory
from api.groups.service import GroupService, group_service_factory
from api.notifications.service import NotificationService, notification_service_factory
from core.database.models import User
from core.managers.group_websocket_manager import (
    GroupConnectionManager,
    get_group_websocket_manager,
)


@router.websocket("/{group_id}")
async def group_chat_websocket(
    group_id: int,
    websocket: WebSocket,
    user: User = Depends(authorize_websocket),
    chat_service: GroupChatService = Depends(group_chat_service_factory),
    group_service: GroupService = Depends(group_service_factory),
    notification_service: NotificationService = Depends(notification_service_factory),
    manager: GroupConnectionManager = Depends(get_group_websocket_manager),
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
        logger.info("Websocket is disconnected")
        manager.disconnect(group_id, user.username)
