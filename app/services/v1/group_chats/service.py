from typing import List, Tuple

from core.exceptions import ForbiddenError
from fastapi import HTTPException
from services.v1.users.data_manager import UserDataManager
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.models import Group, GroupMessage, GroupMessageCheck, User
from app.schemas import (
    GroupMessageCreateSchema,
    GroupMessageResponseSchema,
    GroupMessageUpdate,
    PaginationParams,
)
from app.services.v1.base import BaseService
from app.services.v1.group_chats.data_manager import GroupMessageDataManager


class GroupMessageService(BaseService):
    def __init__(
        self,
        session: AsyncSession,
    ):
        super().__init__(session)
        self.data_manager = GroupMessageDataManager(session)
        self.user_data_manager = UserDataManager(session)

    async def create_message(
        self, message_data: GroupMessageCreateSchema, user: User, group_id: int
    ) -> GroupMessage:
        new_message = await self.data_manager.create(message_data, user, group_id)
        return new_message

    async def get_messages(
        self,
        group: Group,
        user: User,
        pagination: PaginationParams,
    ) -> Tuple[List[GroupMessageResponseSchema], int]:
        if not group:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        if user.id not in [member.id for member in group.members]:
            raise ForbiddenError("Вы не состоите в этой группе")
        messages, total = await self.data_manager.get_messages_by_group(
            group, pagination
        )
        message_ids = [m.id for m in messages if m.sender != user]
        if message_ids:
            await self.data_manager.set_group_message_as_read(user.id, message_ids)
        return [
            GroupMessageResponseSchema.model_validate(message) for message in messages
        ], total

    async def get_message_checks(
        self, message: GroupMessage, user: User
    ) -> List[GroupMessageCheck]:
        if message.sender != user:
            raise ForbiddenError(
                "Вы не можете просматривать проверки сообщений, которые не отправили вы."
            )
        checks = await self.data_manager.get_checks(message)
        return checks

    async def set_group_message_as_read_bulk(
        self, user_id: int, message_ids: List[int]
    ) -> None:
        await self.data_manager.set_group_message_as_read(user_id, message_ids)
        return

    async def set_incoming_messages_as_read(
        self, user_id: int, message_ids: List[int]
    ) -> None:
        await self.data_manager.set_group_message_as_read(user_id, message_ids)
        return

    async def get_message_by_id(self, message_id: int) -> GroupMessage:
        message = await self.data_manager.get_by_id(message_id)
        if not message:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return message

    async def delete_message(self, message_id: int, user: User) -> None:
        message = await self.data_manager.get_by_id(message_id)
        if message:
            if message.sender != user:
                raise ForbiddenError("Вы не можете удалить это сообщение.")
            await self.data_manager.delete(message)
        else:
            raise HTTPException(status_code=404, detail="Сообщение не найдено.")

    async def update_message(
        self, message: GroupMessage, message_data: GroupMessageUpdate, user: User
    ) -> GroupMessage:
        if not message:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        if message.sender != user:
            raise ForbiddenError("Вы не можете редактировать это сообщение.")
        message.text = message_data.text
        await self.data_manager.update(message)
        return message

    async def get_group_users_by_message(self, message: GroupMessage) -> List[User]:
        users = await self.user_data_manager.get_users_by_group_message(message)
        return users

    async def update_online_status(self, user: User) -> None:
        if user.is_online is False:
            user.is_online = True
            await self.user_data_manager.update(user)
        else:
            user.is_online = False
            await self.user_data_manager.update(user)
