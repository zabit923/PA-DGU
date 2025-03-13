from sqlalchemy import Sequence, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.models import Group, GroupMessage, User


class GroupMessageRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, message_id: int) -> GroupMessage:
        statement = select(GroupMessage).where(GroupMessage.id == message_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_messages_by_group(
        self, group: Group, offset: int, limit: int
    ) -> Sequence[GroupMessage]:
        statement = (
            select(GroupMessage)
            .where(GroupMessage.group_id == group.id)
            .order_by(GroupMessage.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def create(
        self, message_data_dict: dict, sender: User, group_id: int
    ) -> GroupMessage:
        new_message = GroupMessage(
            **message_data_dict, sender=sender, group_id=group_id
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
