import logging
from typing import List

from fastapi import APIRouter, Depends, status

from api.groups.service import GroupService, group_service_factory
from api.users.routers import get_current_user
from core.database.models import User
from core.managers.group_websocket_manager import (
    GroupConnectionManager,
    get_group_websocket_manager,
)

from .schemas import GroupMessageRead, GroupMessageUpdate
from .service import GroupChatService, group_chat_service_factory

router = APIRouter(prefix="/groups")
logger = logging.getLogger(__name__)


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
    manager: GroupConnectionManager = Depends(get_group_websocket_manager),
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
    manager: GroupConnectionManager = Depends(get_group_websocket_manager),
):
    message = await chat_service.get_message_by_id(message_id)
    updated_message = await chat_service.update_message(message, message_data, user)
    await manager.notify_update(message.group_id, message_id)
    return updated_message
