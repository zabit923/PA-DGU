from api.groups.schemas import GroupCreate
from api.materials.schemas import LectureCreate
from core.database.models import Group, User
from sqlalchemy import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


class GroupRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, group_id: int) -> Group:
        statement = select(Group).where(Group.id == group_id)
        result = await self.session.execute(statement)
        return result.scalars().first()

    async def get_all(self) -> Sequence[Group]:
        statement = select(Group)
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def get_my_groups(self, user: User) -> Sequence[Group]:
        group_ids = [group.id for group in user.member_groups]
        statement = select(Group).where(Group.id.in_(group_ids))
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def get_by_curator(self, user: User) -> Sequence[Group]:
        statement = select(Group).where(Group.methodist == user)
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def get_by_ids(self, group_ids: list[int]) -> Sequence[Group]:
        statement = select(Group).filter(Group.id.in_(group_ids))
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def get_by_invite_token(self, invite_token: str) -> Group:
        statement = select(Group).where(Group.invite_token == invite_token)
        result = await self.session.execute(statement)
        return result.scalars().first()

    async def join_group(self, user: User, group: Group) -> None:
        group.members.append(user)
        await self.session.commit()
        await self.session.refresh(group)

    async def delete_from_group(self, group: Group, user: User) -> None:
        group.members.remove(user)
        await self.session.commit()
        await self.session.refresh(group)

    async def generate_invite_link(self, group: Group) -> None:
        group.generate_invite_token()
        await self.session.commit()
        await self.session.refresh(group)

    async def groups_in_lecture_data(
        self, lecture_data: LectureCreate
    ) -> Sequence[Group]:
        statement = select(Group).where(Group.id.in_(lecture_data.groups))
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def create(self, group_data: GroupCreate, user: User) -> Group:
        group_data_dict = group_data.model_dump()
        new_group = Group(**group_data_dict, methodist=user, members=[user])
        self.session.add(new_group)
        await self.session.commit()
        return new_group

    async def update(self, group: GroupCreate) -> None:
        await self.session.commit()
        await self.session.refresh(group)

    async def delete(self, group: Group) -> None:
        await self.session.delete(group)
        await self.session.commit()
