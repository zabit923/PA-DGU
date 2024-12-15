from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.chats.private_chats.schemas import PrivateMessageCreate
from core.database.models import PrivateMessage, PrivateRoom, User
from core.database.models.chats import room_members


class PersonalMessageService:
    async def get_or_create_room(
        self, user1_id: int, user2_id: int, session: AsyncSession
    ) -> PrivateRoom:
        stmt = (
            select(PrivateRoom)
            .join(room_members, PrivateRoom.id == room_members.c.room_id)
            .where(room_members.c.user_id.in_([user1_id, user2_id]))
            .group_by(PrivateRoom.id)
        )
        result = await session.execute(stmt)
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
        sender_id: int,
        room_id: int,
        message_data: PrivateMessageCreate,
        session: AsyncSession,
    ) -> PrivateMessage:
        message_data_dict = message_data.model_dump()
        new_message = PrivateMessage(
            **message_data_dict, room_id=room_id, sender_id=sender_id
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
