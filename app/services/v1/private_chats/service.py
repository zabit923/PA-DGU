from typing import List, Tuple

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.services.v1.users.data_manager import UserDataManager
from app.services.v1.base import BaseService
from app.services.v1.private_chats.data_manager import PrivateMessageDataManager
from app.services.v1.rooms.data_manager import RoomDataManager
from app.models import PrivateRoom, User, PrivateMessage
from app.schemas import (
    PrivateMessageCreateSchema,
    PaginationParams,
    PrivateMessageResponseSchema,
    RoomResponseSchema,
    UserShortSchema,
    PrivateMessageUpdateSchema
)
from app.core.exceptions import ForbiddenError


class PrivateMessageService(BaseService):
    def __init__(
        self,
        session: AsyncSession,
    ):
        super().__init__(session)
        self.message_data_manager = PrivateMessageDataManager(session)
        self.room_data_manager = RoomDataManager(session)
        self.user_data_manager = UserDataManager(session)

    async def get_or_create_room(self, user_id1: int, user_id2: int, user: User) -> PrivateRoom:
        if user_id2 == user.id:
            raise ForbiddenError(detail="Необходим id собеседника.")
        room = await self.room_data_manager.get_by_user_ids(user_id1, user_id2)
        if not room:
            room = await self.room_data_manager.create(user_id1, user_id2)
        return room

    async def create_message(
        self,
        sender: User,
        room_id: int,
        message_data: PrivateMessageCreateSchema,
    ) -> PrivateMessage:
        message_data_dict = message_data.model_dump()
        new_message = await self.message_data_manager.create(
            message_data_dict, room_id, sender
        )
        return new_message

    async def get_messages(
        self,
        user: User,
        user_id: int,
        room: PrivateRoom,
        pagination: PaginationParams,
    ) -> Tuple[List[PrivateMessageResponseSchema], int]:
        if user.id not in [member.id for member in room.members]:
            raise ForbiddenError(detail="Вы не участник этой беседы.")
        messages, total = await self.message_data_manager.get_by_room(
            room, pagination
        )
        message_ids = [m.id for m in messages]
        await self.message_data_manager.set_messages_is_read_bulk(
            user_id, message_ids
        )
        return [
            PrivateMessageResponseSchema.model_validate(message) for message in messages
        ], total

    async def set_incoming_messages_is_read_bulk(
        self,
        user_id: int,
        message_ids: List[int]
    ) -> None:
        await self.message_data_manager.set_messages_is_read_bulk(
            user_id, message_ids
        )
        return

    async def get_message_by_id(self, message_id: int) -> PrivateMessage:
        message = await self.message_data_manager.get_by_id(message_id)
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Сообщение не найдено."
            )
        return message

    async def get_my_rooms(self, user: User) -> List[PrivateRoom]:
        rooms = await self.room_data_manager.get_my_rooms(user)
        rooms_with_last_message = []
        for room in rooms:
            last_message = await self.message_data_manager.get_last_message(room)
            members_schemas = [
                UserShortSchema.model_validate(m) for m in room.members
            ]
            rooms_with_last_message.append(
                RoomResponseSchema(
                    id=room.id,
                    created_at=room.created_at,
                    updated_at=room.updated_at,
                    members=members_schemas,
                    last_message=last_message,
                )
            )
        return rooms_with_last_message

    async def delete_message(self, message_id: int, user: User) -> None:
        message = await self.message_data_manager.get_by_id(message_id)
        if message:
            if message.sender.id != user.id:
                raise ForbiddenError(detail="Вы не можете удалить чужое сообщение.")
            await self.message_data_manager.delete(message)
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Сообщение не найдено"
            )

    async def update_message(
        self,
        message: PrivateMessage,
        message_data: PrivateMessageUpdateSchema,
        user: User
    ) -> PrivateMessage:
        if not message:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        if message.sender.id != user.id:
            raise ForbiddenError(detail="Вы не можете изменять чужое сообщение.")
        message.text = message_data.text
        await self.message_data_manager.update(message)
        return message

    async def get_users_by_message(
        self,
        message: PrivateMessage,
    ) -> List[User]:
        users = await self.user_data_manager.get_users_by_private_message(message)
        return users

    async def update_online_status(self, user: User) -> None:
        if user.is_online is False:
            user.is_online = True
            await self.user_data_manager.update(user)
        else:
            user.is_online = False
            await self.user_data_manager.update(user)
