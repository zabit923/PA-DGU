from typing import List

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from starlette import status

from core.database.models import Group, Organization, User

from .schemas import GroupCreate, GroupUpdate


class GroupService:
    async def get_group(self, group_id: int, session: AsyncSession) -> Group:
        statement = select(Group).where(Group.id == group_id)
        result = await session.execute(statement)
        group = result.scalars().first()
        return group

    async def get_my_groups(self, user: User, session: AsyncSession) -> List[Group]:
        statement = select(Group).where(Group.curator == user)
        result = await session.execute(statement)
        groups = result.scalars().all()
        return groups

    async def create_group(
        self, group_data: GroupCreate, user: User, session: AsyncSession
    ) -> Group:
        group_data_dict = group_data.model_dump()
        org_id = group_data_dict.pop("organization")
        organization = await self.get_organization(org_id, session)
        if not organization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Organization with id {org_id} not found.",
            )
        new_group = Group(
            **group_data_dict, organization=organization, curator=user, members=[user]
        )
        session.add(new_group)
        try:
            await session.commit()
            return new_group
        except IntegrityError:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Group with the same organization, facult, course, and subgroup already exists.",
            )

    async def update_group(
        self, group_id: int, group_data: GroupUpdate, session: AsyncSession
    ) -> Group:
        group = await self.get_group(group_id, session)
        group_data_dict = group_data.model_dump(exclude_unset=True)

        if "organization" in group_data_dict:
            org_id = group_data_dict.pop("organization")
            organization = await self.get_organization(org_id, session)
            if not organization:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Organization with id {org_id} not found.",
                )
            group.organization = organization

        for key, value in group_data_dict.items():
            if value is None:
                continue
            setattr(group, key, value)

        try:
            await session.commit()
            await session.refresh(group)
            return group
        except IntegrityError:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Group with the same organization, facult, course, and subgroup already exists.",
            )

    async def get_organization(self, org_id, session: AsyncSession) -> Organization:
        statement = select(Organization).where(Organization.id == org_id)
        result = await session.execute(statement)
        organization = result.scalars().first()
        return organization
