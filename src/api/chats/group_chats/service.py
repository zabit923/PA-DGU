from typing import Sequence

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from starlette import status

from api.chats.group_chats.schemas import GroupMessageCreate, GroupMessageUpdate
from core.database.models import Group, GroupMessage, User


class GroupMessageService:
    @staticmethod
    async def create_message(
        message_data: GroupMessageCreate,
        user: User,
        group_id: int,
        session: AsyncSession,
    ) -> GroupMessage:
        message_data_dict = message_data.model_dump()
        new_message = GroupMessage(**message_data_dict, sender=user, group_id=group_id)
        session.add(new_message)
        await session.commit()
        await session.refresh(new_message)
        return new_message

    @staticmethod
    async def get_messages(group, offset: int, limit: int, session: AsyncSession):
        stmt = (
            select(GroupMessage)
            .where(GroupMessage.group_id == group.id)
            .order_by(GroupMessage.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_message_by_id(
        message_id: int,
        session: AsyncSession,
    ):
        stmt = select(GroupMessage).where(GroupMessage.id == message_id)
        result = await session.execute(stmt)
        message = result.scalar_one_or_none()
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Message not found."
            )
        return message

    @staticmethod
    async def delete_message(message: GroupMessage, session: AsyncSession) -> None:
        if message:
            await session.delete(message)
            await session.commit()
        else:
            raise HTTPException(status_code=404, detail="Message not found.")

    @staticmethod
    async def update_message(
        message: GroupMessage,
        message_data: GroupMessageUpdate,
        session: AsyncSession,
    ) -> GroupMessage:
        message.text = message_data.text
        await session.commit()
        await session.refresh(message)
        return message

    @staticmethod
    async def get_group_users_by_message(
        message: GroupMessage,
        session: AsyncSession,
    ) -> Sequence[User]:
        statement = (
            select(User)
            .join(User.member_groups)
            .join(Group.group_messages)
            .where(GroupMessage.id == message.id)
        )
        result = await session.execute(statement)
        users = result.scalars().all()
        return users
