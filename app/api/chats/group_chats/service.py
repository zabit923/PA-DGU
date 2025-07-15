from typing import List, Sequence

from api.chats.group_chats.schemas import GroupMessageCreate, GroupMessageUpdate
from core.database import get_async_session
from core.database.models import Group, GroupMessage, GroupMessageCheck, User
from core.database.repositories import (
    GroupMessageRepository,
    GroupRepository,
    UserRepository,
)
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status


class GroupChatService:
    def __init__(
        self,
        group_message_repository: GroupMessageRepository,
        user_repository: UserRepository,
        group_repository: GroupRepository,
    ):
        self.group_message_repository = group_message_repository
        self.user_repository = user_repository
        self.group_repository = group_repository

    async def create_message(
        self, message_data: GroupMessageCreate, user: User, group_id: int
    ) -> GroupMessage:
        message_data_dict = message_data.model_dump()
        new_message = await self.group_message_repository.create(
            message_data_dict, user, group_id
        )
        return new_message

    async def get_messages(
        self, group: Group, user: User, offset: int, limit: int
    ) -> Sequence[GroupMessage]:
        if not group:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        if user.id not in [member.id for member in group.members]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User not member of this group.",
            )
        messages = await self.group_message_repository.get_messages_by_group(
            group, offset, limit
        )
        message_ids = [m.id for m in messages if m.sender != user]
        if message_ids:
            await self.group_message_repository.set_group_message_as_read(
                user.id, message_ids
            )
        return messages

    async def get_message_checks(
        self, message: GroupMessage, user: User
    ) -> Sequence[GroupMessageCheck]:
        if message.sender != user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not sender of this message",
            )
        checks = await self.group_message_repository.get_checks(message)
        return checks

    async def set_group_message_as_read_bulk(
        self, user_id: int, message_ids: List[int]
    ) -> None:
        await self.group_message_repository.set_group_message_as_read(
            user_id, message_ids
        )
        return

    async def set_incoming_messages_as_read(
        self, user_id: int, message_ids: List[int]
    ) -> None:
        await self.group_message_repository.set_group_message_as_read(
            user_id, message_ids
        )
        return

    async def get_message_by_id(self, message_id: int) -> GroupMessage:
        message = await self.group_message_repository.get_by_id(message_id)
        if not message:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return message

    async def delete_message(self, message_id: int, user: User) -> None:
        message = await self.group_message_repository.get_by_id(message_id)
        if message:
            if message.sender != user:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You are not authorized to delete this message.",
                )
            await self.group_message_repository.delete(message)
        else:
            raise HTTPException(status_code=404, detail="Message not found.")

    async def update_message(
        self, message: GroupMessage, message_data: GroupMessageUpdate, user: User
    ) -> GroupMessage:
        if not message:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        if message.sender != user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to update this message.",
            )
        message.text = message_data.text
        await self.group_message_repository.update(message)
        return message

    async def get_group_users_by_message(self, message: GroupMessage) -> Sequence[User]:
        users = await self.user_repository.get_users_by_group_message(message)
        return users

    async def update_online_status(self, user: User) -> None:
        if user.is_online is False:
            user.is_online = True
            await self.user_repository.update(user)
        else:
            user.is_online = False
            await self.user_repository.update(user)


def group_chat_service_factory(
    session: AsyncSession = Depends(get_async_session),
) -> GroupChatService:
    return GroupChatService(
        GroupMessageRepository(session),
        UserRepository(session),
        GroupRepository(session),
    )
