import logging
from typing import List

from fastapi import APIRouter
from fastapi.params import Depends
from starlette import status

from api.users.dependencies import get_current_user
from core.database.models import User
from core.managers.private_websocket_manager import (
    PrivateConnectionManager,
    get_private_websocket_manager,
)

from .schemas import PrivateMessageRead, PrivateMessageUpdate, RoomRead
from .service import PrivateChatService, private_chat_service_factory

router = APIRouter(prefix="/private-chats")
logger = logging.getLogger(__name__)


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
    manager: PrivateConnectionManager = Depends(get_private_websocket_manager),
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
    manager: PrivateConnectionManager = Depends(get_private_websocket_manager),
):
    message = await chat_service.get_message_by_id(message_id)
    updated_message = await chat_service.update_message(message, message_data, user)
    await manager.notify_update(message.room_id, message_id)
    return updated_message
