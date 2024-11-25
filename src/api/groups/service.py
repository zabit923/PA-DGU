from typing import Optional

from fastapi import HTTPException
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
        existing_group = await self.group_exists(
            organization.id,
            group_data_dict["facult"],
            group_data_dict["course"],
            group_data_dict["subgroup"],
            session,
        )
        if existing_group:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Group with the same organization, facult, course, and subgroup already exists.",
            )
        new_group = Group(
            **group_data_dict, organization=organization, curator=user, members=[user]
        )
        session.add(new_group)
        await session.commit()
        return new_group

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

        group.facult = group_data_dict.get("facult", group.facult)
        group.course = group_data_dict.get("course", group.course)
        group.subgroup = group_data_dict.get("subgroup", group.subgroup)

        existing_group = await self.group_exists(
            organization_id=group.organization_id,
            facult=group.facult,
            course=group.course,
            subgroup=group.subgroup,
            session=session,
            exclude_group_id=group.id,
        )
        if existing_group:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Group with the same organization, facult, course, and subgroup already exists.",
            )

        await session.commit()
        await session.refresh(group)
        return group

    async def group_exists(
        self,
        organization_id: int,
        facult: str,
        course: int,
        subgroup: int,
        session: AsyncSession,
        exclude_group_id: Optional[int] = None,
    ) -> bool:
        statement = select(Group).where(
            Group.organization_id == organization_id,
            Group.facult == facult,
            Group.course == course,
            Group.subgroup == subgroup,
        )
        if exclude_group_id:
            statement = statement.where(Group.id != exclude_group_id)

        result = await session.execute(statement)
        return result.scalars().first() is not None

    async def get_organization(self, org_id, session: AsyncSession) -> Organization:
        statement = select(Organization).where(Organization.id == org_id)
        result = await session.execute(statement)
        organization = result.scalars().first()
        return organization
