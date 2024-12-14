from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from api.chats.group_chats.schemas import GroupMessageCreate
from core.database.models import GroupMessage, User


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
        await session.refresh(new_message)
        return new_message

    async def get_messages(self, group, offset: int, limit: int, session: AsyncSession):
        stmt = (
            select(GroupMessage)
            .where(GroupMessage.group_id == group.id)
            .order_by(GroupMessage.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return result.scalars().all()
