from typing import List

from app.schemas import GroupMessageCreateSchema, GroupMessageDataSchema, PaginationParams
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Group, GroupMessage, GroupMessageCheck, User
from app.services.v1.base import BaseEntityManager


class GroupMessageDataManager(BaseEntityManager[GroupMessageDataSchema]):
    def __init__(self, session: AsyncSession):
        super().__init__(
            session=session, schema=GroupMessageDataSchema, model=GroupMessage
        )

    async def get_by_id(self, message_id: int) -> GroupMessage:
        statement = select(GroupMessage).where(GroupMessage.id == message_id)
        return await self.get_one(statement)

    async def get_messages_by_group(
        self,
        group: Group,
        pagination: PaginationParams,
    ) -> tuple[List[GroupMessage], int]:
        statement = (
            select(GroupMessage)
            .where(GroupMessage.group_id == group.id)
            .order_by(GroupMessage.created_at.desc())
        )
        return await self.get_paginated_items(statement, pagination)

    async def set_group_message_as_read(
        self,
        user_id: int,
        message_ids: List[int],
    ) -> None:
        existing_checks = await self.session.execute(
            select(GroupMessageCheck.message_id)
            .where(GroupMessageCheck.user_id == user_id)
            .where(GroupMessageCheck.message_id.in_(message_ids))
        )
        existing_message_ids = {row[0] for row in existing_checks.fetchall()}
        new_checks = [
            GroupMessageCheck(user_id=user_id, message_id=message_id)
            for message_id in message_ids
            if message_id not in existing_message_ids
        ]
        if new_checks:
            self.session.add_all(new_checks)
            try:
                await self.session.commit()
            except IntegrityError:
                await self.session.rollback()

    async def get_checks(self, message: GroupMessage) -> List[GroupMessageCheck]:
        statement = select(GroupMessageCheck).where(
            GroupMessageCheck.message_id == message.id
        )
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def create(
        self, message_data: GroupMessageCreateSchema, sender: User, group_id: int
    ) -> GroupMessage:
        new_message = GroupMessage(
            text=message_data.text, sender_id=sender.id, group_id=group_id
        )
        self.session.add(new_message)
        await self.session.commit()
        return new_message

    async def delete(self, message: GroupMessage) -> None:
        await self.session.delete(message)
        await self.session.commit()

    async def update(self, message: GroupMessage) -> None:
        await self.session.commit()
        await self.session.refresh(message)
