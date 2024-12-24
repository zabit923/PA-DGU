from typing import List

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from starlette import status

from api.chats.group_chats.schemas import GroupMessageCreate, GroupMessageUpdate
from core.database.models import Group, GroupMessage, User
from core.tasks import send_new_group_message_email


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

        user_list = await self.get_group_users_by_message(new_message, session)
        filtered_user_list = [
            u for u in user_list if u != user and not u.ignore_messages
        ]

        simplified_user_list = [
            {"email": user.email, "username": user.username}
            for user in filtered_user_list
        ]
        send_new_group_message_email.delay(
            group_id, simplified_user_list, message_data.text, user.username
        )

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

    async def get_message_by_id(
        self,
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

    async def delete_message(
        self, message: GroupMessage, session: AsyncSession
    ) -> None:
        if message:
            await session.delete(message)
            await session.commit()
        else:
            raise HTTPException(status_code=404, detail="Message not found.")

    async def update_message(
        self,
        message: GroupMessage,
        message_data: GroupMessageUpdate,
        session: AsyncSession,
    ) -> GroupMessage:
        message.text = message_data.text
        await session.commit()
        await session.refresh(message)
        return message

    async def get_group_users_by_message(
        self,
        message: GroupMessage,
        session: AsyncSession,
    ) -> List[User]:
        statement = (
            select(User)
            .join(User.member_groups)
            .join(Group.group_messages)
            .where(GroupMessage.id == message.id)
        )
        result = await session.execute(statement)
        users = result.scalars().all()
        return users
