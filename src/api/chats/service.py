from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from api.chats.schemas import GroupMessageCreate, GroupMessageRead
from core.database.models import Group, GroupMessage, User


class GroupMessageService:
    async def create_message(
        self,
        message_data: GroupMessageCreate,
        user: User,
        group_id: int,
        session: AsyncSession,
    ) -> GroupMessage:
        message_data_dict = message_data.model_dump()
        new_message = GroupMessage(**message_data_dict, sender=user, group_id=group_id)
        session.add(new_message)
        await session.commit()
        return new_message

    async def get_all_messages(
        self,
        group: Group,
        session: AsyncSession,
    ) -> List[GroupMessageRead]:
        statement = select(GroupMessage).where(GroupMessage.group_id == group.id)
        result = await session.execute(statement)
        messages = result.scalars().all()
        return messages
