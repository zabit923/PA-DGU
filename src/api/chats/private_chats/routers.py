import logging
from json import JSONDecodeError
from typing import List

from fastapi import APIRouter, WebSocket
from fastapi.params import Depends
from fastapi_limiter.depends import WebSocketRateLimiter
from starlette import status
from starlette.websockets import WebSocketDisconnect

from api.chats.dependencies import authorize_websocket
from api.chats.exceptions import WebsocketTooManyRequests
from api.chats.rate_limiter import websocket_callback
from api.notifications.service import NotificationService, notification_service_factory
from api.users.dependencies import get_current_user
from core.database.models import User
from core.managers.private_websocket_manager import PrivateConnectionManager

from .schemas import (
    PrivateMessageCreate,
    PrivateMessageRead,
    PrivateMessageUpdate,
    RoomRead,
)
from .service import PrivateChatService, private_chat_service_factory

router = APIRouter(prefix="/private-chats")

logger = logging.getLogger(__name__)
manager = PrivateConnectionManager()


@router.websocket("/{receiver_id}")
async def private_chat_websocket(
    receiver_id: int,
    websocket: WebSocket,
    user: User = Depends(authorize_websocket),
    chat_service: PrivateChatService = Depends(private_chat_service_factory),
    notification_service: NotificationService = Depends(notification_service_factory),
):
    room = await chat_service.get_or_create_room(user_id1=user.id, user_id2=receiver_id)
    await manager.connect(room.id, user.username, websocket)
    ratelimit = WebSocketRateLimiter(times=50, seconds=10, callback=websocket_callback)
    try:
        while True:
            try:
                message_data = await websocket.receive_json()
                await ratelimit(websocket)
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
            except WebsocketTooManyRequests:
                logger.exception(f"User: {user} sent too many ws requests")
                await manager.send_error("You have sent too many requests", websocket)
    except WebSocketDisconnect:
        logging.info("Websocket is disconnected")
        manager.disconnect(room.id, user.username)


@router.get(
    "/get-my-rooms", status_code=status.HTTP_200_OK, response_model=List[RoomRead]
)
async def get_my_rooms(
    user: User = Depends(get_current_user),
    chat_service: PrivateChatService = Depends(private_chat_service_factory),
) -> List[RoomRead]:
    rooms = await chat_service.get_my_rooms(user)
    return rooms


@router.get(
    "/{receiver_id}",
    status_code=status.HTTP_200_OK,
    response_model=List[PrivateMessageRead],
)
async def get_messages(
    receiver_id: int,
    offset: int = 0,
    limit: int = 50,
    user: User = Depends(get_current_user),
    chat_service: PrivateChatService = Depends(private_chat_service_factory),
) -> List[PrivateMessageRead]:
    room = await chat_service.get_or_create_room(user_id1=user.id, user_id2=receiver_id)
    messages = await chat_service.get_messages(room, offset, limit)
    return messages


@router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_message(
    message_id: int,
    user: User = Depends(get_current_user),
    chat_service: PrivateChatService = Depends(private_chat_service_factory),
):
    message = await chat_service.get_message_by_id(message_id)
    await chat_service.delete_message(message_id, user)
    await manager.notify_deletion(message.room_id, message_id)
    return {"detail": "Message deleted successfully."}


@router.patch(
    "/{message_id}",
    status_code=status.HTTP_200_OK,
    response_model=PrivateMessageRead,
)
async def update_message(
    message_id: int,
    message_data: PrivateMessageUpdate,
    user: User = Depends(get_current_user),
    chat_service: PrivateChatService = Depends(private_chat_service_factory),
):
    message = await chat_service.get_message_by_id(message_id)
    updated_message = await chat_service.update_message(message, message_data, user)
    await manager.notify_update(message.room_id, message_id)
    return updated_message
