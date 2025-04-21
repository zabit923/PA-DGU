from sqlalchemy import Sequence, distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.models import PrivateRoom, User
from core.database.models.chats import room_members


class RoomRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_my_rooms(self, user: User) -> Sequence[PrivateRoom]:
        statement = (
            select(PrivateRoom)
            .join(room_members, PrivateRoom.id == room_members.c.room_id)
            .where(user.id == room_members.c.user_id)
        )
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def get_by_user_ids(self, user_id1: int, user_id2: int) -> PrivateRoom:
        subquery = (
            select(room_members.c.room_id)
            .group_by(room_members.c.room_id)
            .having(
                func.count(distinct(room_members.c.user_id)) == 2,
            )
            .where(room_members.c.user_id.in_([user_id1, user_id2]))
        )

        statement = select(PrivateRoom).where(PrivateRoom.id.in_(subquery))

        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def create(self, user_id1: int, user_id2: int) -> PrivateRoom:
        room = PrivateRoom()
        self.session.add(room)
        await self.session.flush()
        await self.session.execute(
            room_members.insert().values(
                [
                    {"room_id": room.id, "user_id": user_id}
                    for user_id in [user_id1, user_id2]
                ]
            )
        )
        await self.session.commit()
        return room
