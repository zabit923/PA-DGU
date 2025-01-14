from typing import List

from fastapi import HTTPException
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.chats.private_chats.schemas import PrivateMessageCreate, PrivateMessageUpdate
from api.users.service import UserService
from core.database.models import PrivateMessage, PrivateRoom, User
from core.database.models.chats import room_members

user_service = UserService()


class PersonalMessageService:
    async def get_or_create_room(
        self, user1_id: int, user2_id: int, session: AsyncSession
    ) -> PrivateRoom:
        statement = (
            select(PrivateRoom)
            .join(room_members, PrivateRoom.id == room_members.c.room_id)
            .where(room_members.c.user_id.in_([user1_id, user2_id]))
            .group_by(PrivateRoom.id)
        )
        result = await session.execute(statement)
        room = result.scalar_one_or_none()

        if not room:
            room = PrivateRoom()
            session.add(room)
            await session.flush()
            await session.execute(
                room_members.insert().values(
                    [
                        {"room_id": room.id, "user_id": user_id}
                        for user_id in [user1_id, user2_id]
                    ]
                )
            )
            await session.commit()
        return room

    async def create_message(
        self,
        sender: User,
        room_id: int,
        message_data: PrivateMessageCreate,
        session: AsyncSession,
    ) -> PrivateMessage:
        message_data_dict = message_data.model_dump()
        new_message = PrivateMessage(
            **message_data_dict, room_id=room_id, sender_id=sender.id
        )
        session.add(new_message)
        await session.commit()
        await session.refresh(new_message)
        return new_message

    async def get_messages(self, room, offset: int, limit: int, session: AsyncSession):
        statement = (
            select(PrivateMessage)
            .where(PrivateMessage.room_id == room.id)
            .order_by(PrivateMessage.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await session.execute(statement)
        return result.scalars().all()

    async def get_message_by_id(
        self,
        message_id: int,
        session: AsyncSession,
    ):
        stmt = select(PrivateMessage).where(PrivateMessage.id == message_id)
        result = await session.execute(stmt)
        message = result.scalar_one_or_none()
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Message not found."
            )
        return message

    async def get_my_rooms(self, user: User, session: AsyncSession):
        statement = (
            select(PrivateRoom)
            .join(room_members, PrivateRoom.id == room_members.c.room_id)
            .where(user.id == room_members.c.user_id)
        )
        result = await session.execute(statement)
        rooms = result.scalars().all()

        rooms_with_last_message = []
        for room in rooms:
            last_message_stmt = (
                select(PrivateMessage)
                .where(PrivateMessage.room_id == room.id)
                .order_by(desc(PrivateMessage.created_at))
                .limit(1)
            )
            last_message_result = await session.execute(last_message_stmt)
            last_message = last_message_result.scalar_one_or_none()

            rooms_with_last_message.append(
                {
                    "id": room.id,
                    "members": room.members,
                    "last_message": last_message,
                    "created_at": room.created_at,
                }
            )
        return rooms_with_last_message

    async def delete_message(self, message_id: int, session: AsyncSession) -> None:
        message = await self.get_message_by_id(message_id, session)
        if message:
            await session.delete(message)
            await session.commit()
        else:
            raise HTTPException(status_code=404, detail="Message not found.")

    async def update_message(
        self,
        message: PrivateMessage,
        message_data: PrivateMessageUpdate,
        session: AsyncSession,
    ) -> PrivateMessage:
        message.text = message_data.text
        await session.commit()
        await session.refresh(message)
        return message

    async def get_user_by_message(
        self,
        message: PrivateMessage,
        session: AsyncSession,
    ) -> List[User]:
        statement = (
            select(User)
            .join(User.rooms)
            .join(PrivateRoom.messages)
            .where(PrivateMessage.id == message.id)
        )
        result = await session.execute(statement)
        users = result.scalars().all()
        return users
