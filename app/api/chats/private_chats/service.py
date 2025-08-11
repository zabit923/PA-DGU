from typing import List, Sequence

from api.chats.private_chats.schemas import PrivateMessageCreate, PrivateMessageUpdate
from core.database import get_async_session
from core.database.models import PrivateMessage, PrivateRoom, User
from core.database.repositories import (
    PrivateMessageRepository,
    RoomRepository,
    UserRepository,
)
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status


class PrivateChatService:
    def __init__(
        self,
        room_repository: RoomRepository,
        private_message_repository: PrivateMessageRepository,
        user_repository: UserRepository,
    ):
        self.room_repository = room_repository
        self.private_message_repository = private_message_repository
        self.user_repository = user_repository

    async def get_or_create_room(self, user_id1: int, user_id2: int) -> PrivateRoom:
        room = await self.room_repository.get_by_user_ids(user_id1, user_id2)
        if not room:
            room = await self.room_repository.create(user_id1, user_id2)
        return room

    async def create_message(
        self,
        sender: User,
        room_id: int,
        message_data: PrivateMessageCreate,
    ) -> PrivateMessage:
        message_data_dict = message_data.model_dump()
        new_message = await self.private_message_repository.create(
            message_data_dict, room_id, sender
        )
        return new_message

    async def get_messages(
        self, user_id: int, room: PrivateRoom, offset: int, limit: int
    ) -> Sequence[PrivateMessage]:
        messages = await self.private_message_repository.get_by_room(
            room, offset, limit
        )
        message_ids = [m.id for m in messages]
        await self.private_message_repository.set_messages_is_read_bulk(
            user_id, message_ids
        )
        return messages

    async def set_incoming_messages_is_read_bulk(
        self, user_id: int, message_ids: List[int]
    ) -> None:
        await self.private_message_repository.set_messages_is_read_bulk(
            user_id, message_ids
        )
        return

    async def get_message_by_id(self, message_id: int) -> PrivateMessage:
        message = await self.private_message_repository.get_by_id(message_id)
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Message not found."
            )
        return message

    async def get_my_rooms(self, user: User) -> Sequence[PrivateRoom]:
        rooms = await self.room_repository.get_my_rooms(user)
        rooms_with_last_message = []
        for room in rooms:
            last_message = await self.private_message_repository.get_last_message(room)
            rooms_with_last_message.append(
                {
                    "id": room.id,
                    "members": room.members,
                    "last_message": last_message,
                    "created_at": room.created_at,
                }
            )
        return rooms_with_last_message

    async def delete_message(self, message_id: int, user: User) -> None:
        message = await self.private_message_repository.get_by_id(message_id)
        if message:
            if message.sender != user:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You are not authorized to delete this message.",
                )
            await self.private_message_repository.delete(message)
        else:
            raise HTTPException(status_code=404, detail="Message not found.")

    async def update_message(
        self, message: PrivateMessage, message_data: PrivateMessageUpdate, user: User
    ) -> PrivateMessage:
        if not message:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        if message.sender != user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to update this message.",
            )
        message.text = message_data.text
        await self.private_message_repository.update(message)
        return message

    async def get_users_by_message(
        self,
        message: PrivateMessage,
    ) -> Sequence[User]:
        users = await self.user_repository.get_users_by_private_message(message)
        return users

    async def update_online_status(self, user: User) -> None:
        if user.is_online is False:
            user.is_online = True
            await self.user_repository.update(user)
        else:
            user.is_online = False
            await self.user_repository.update(user)


def private_chat_service_factory(
    session: AsyncSession = Depends(get_async_session),
) -> PrivateChatService:
    return PrivateChatService(
        RoomRepository(session),
        PrivateMessageRepository(session),
        UserRepository(session),
    )
