from typing import List

from models import User
from schemas import (
    GroupCreateSchema,
    GroupDataSchema,
    GroupUpdateSchema,
    LectureCreateSchema,
    PaginationParams,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Group
from app.services.v1.base import BaseEntityManager


class GroupDataManager(BaseEntityManager[GroupDataSchema]):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, schema=GroupDataSchema, model=Group)

    async def get_group_by_id(self, group_id: int) -> Group:
        statement = select(self.model).where(self.model.id == group_id)
        return await self.get_one(statement)

    async def create_group(self, data: GroupCreateSchema, user: User) -> Group:
        user = await self.session.merge(user)
        group_model = Group(
            course=data.course,
            facult=data.facult,
            subgroup=data.subgroup,
            methodist=user,
            members=[user],
        )
        return await self.add_one(group_model)

    async def update_group(self, group: Group, data: GroupUpdateSchema) -> Group:
        group_data_dict = data.model_dump(exclude_unset=True, exclude_none=True)
        for key, value in group_data_dict.items():
            setattr(group, key, value)
        return await self.update_one(group)

    async def get_all_groups(
        self,
        pagination: PaginationParams,
    ) -> tuple[List[Group], int]:
        statement = select(self.model).distinct()
        return await self.get_paginated_items(statement, pagination)

    async def get_my_groups(self, user: User) -> List[Group]:
        group_ids = [group.id for group in user.member_groups]
        statement = select(Group).where(Group.id.in_(group_ids))
        return await self.get_all(statement)

    async def get_by_ids(self, group_ids: List[int]) -> List[Group]:
        statement = select(Group).filter(Group.id.in_(group_ids))
        return await self.get_all(statement)

    async def get_by_invite_token(self, invite_token: str) -> Group:
        statement = select(Group).where(Group.invite_token == invite_token)
        return await self.get_one(statement)

    async def join_group(self, user: User, group: Group) -> None:
        group.members.append(user)
        await self.session.commit()
        await self.session.refresh(group)

    async def delete_from_group(self, group: Group, user: User) -> None:
        group.members = [member for member in group.members if member.id != user.id]
        await self.session.commit()

    async def generate_invite_link(self, group: Group) -> None:
        group.generate_invite_token()
        await self.session.commit()
        await self.session.refresh(group)

    async def groups_in_lecture_data(
        self, lecture_data: LectureCreateSchema
    ) -> List[Group]:
        statement = select(Group).where(Group.id.in_(lecture_data.groups))
        result = await self.session.execute(statement)
        return result.scalars().all()
