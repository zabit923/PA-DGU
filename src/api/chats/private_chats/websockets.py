from json import JSONDecodeError

from fastapi import Depends
from starlette.websockets import WebSocket, WebSocketDisconnect

from api.chats.dependencies import authorize_websocket
from api.chats.private_chats.routers import logger, router
from api.chats.private_chats.schemas import PrivateMessageCreate, PrivateMessageRead
from api.chats.private_chats.service import (
    PrivateChatService,
    private_chat_service_factory,
)
from api.notifications.service import NotificationService, notification_service_factory
from core.database.models import User
from core.managers.private_websocket_manager import (
    PrivateConnectionManager,
    get_private_websocket_manager,
)


@router.websocket("/{receiver_id}")
async def private_chat_websocket(
    receiver_id: int,
    websocket: WebSocket,
    user: User = Depends(authorize_websocket),
    chat_service: PrivateChatService = Depends(private_chat_service_factory),
    notification_service: NotificationService = Depends(notification_service_factory),
    manager: PrivateConnectionManager = Depends(get_private_websocket_manager),
):
    room = await chat_service.get_or_create_room(user_id1=user.id, user_id2=receiver_id)
    await manager.connect(room.id, user.username, websocket)
    await chat_service.update_online_status(user)
    try:
        while True:
            try:
                message_data = await websocket.receive_json()
                if "action" in message_data and message_data["action"] == "typing":
                    is_typing = message_data.get("is_typing", False)
                    await manager.notify_typing_status(
                        room.id, user.username, is_typing
                    )
                    continue
                message_data = PrivateMessageCreate(**message_data)
                message = await chat_service.create_message(user, room.id, message_data)
                await notification_service.create_private_message_notification(
                    message, chat_service
                )
                message = PrivateMessageRead.model_validate(message).model_dump(
                    mode="json"
                )
                await manager.send_message(room.id, message, exclude=user.username)

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
        manager.disconnect(room.id, user.username)
