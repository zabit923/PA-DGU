from sqlalchemy import Sequence, desc, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.models import PrivateMessage, PrivateRoom, User


class PrivateMessageRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_room(
        self, room: PrivateRoom, offset: int, limit: int
    ) -> Sequence[PrivateMessage]:
        statement = (
            select(PrivateMessage)
            .where(PrivateMessage.room_id == room.id)
            .order_by(PrivateMessage.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def get_last_message(self, room: PrivateRoom) -> PrivateMessage:
        statement = (
            select(PrivateMessage)
            .where(PrivateMessage.room_id == room.id)
            .order_by(desc(PrivateMessage.created_at))
            .limit(1)
        )
        last_message_result = await self.session.execute(statement)
        return last_message_result.scalar_one_or_none()

    async def get_by_id(self, message_id: int) -> PrivateMessage:
        statement = select(PrivateMessage).where(PrivateMessage.id == message_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def set_messages_is_read_bulk(self, user_id: int, message_ids: list) -> None:
        if not message_ids:
            return
        statement = (
            update(PrivateMessage)
            .where(
                PrivateMessage.id.in_(message_ids),
                PrivateMessage.sender_id != user_id,
                PrivateMessage.is_readed == False,
            )
            .values(is_readed=True)
        )
        await self.session.execute(statement)
        await self.session.commit()

    async def create(
        self, message_data_dict: dict, room_id: int, sender: User
    ) -> PrivateMessage:
        new_message = PrivateMessage(
            **message_data_dict, room_id=room_id, sender_id=sender.id
        )
        self.session.add(new_message)
        await self.session.commit()
        return new_message

    async def delete(self, message: PrivateMessage) -> None:
        await self.session.delete(message)
        await self.session.commit()

    async def update(self, message: PrivateMessage) -> None:
        await self.session.commit()
        await self.session.refresh(message)
