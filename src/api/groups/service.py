from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.database.models import Group, User

from .schemas import GroupCreate


class GroupService:
    async def get_group(self, group_id: int, session: AsyncSession) -> Group:
        statement = select(Group).where(Group.id == group_id)
        result = await session.execute(statement)
        group = result.scalars().first()
        return group

    async def create_group(
        self, group_data: GroupCreate, user: User, session: AsyncSession
    ) -> Group:
        group_data_dict = group_data.model_dump()
        new_group = Group(**group_data_dict, curator=user, members=[user])
        session.add(new_group)
        await session.commit()
        return new_group

    async def update_user(
        self, group: Group, group_data: dict, session: AsyncSession
    ) -> Group:
        for k, v in group_data.items():
            setattr(group, k, v)

        await session.commit()
        return group
