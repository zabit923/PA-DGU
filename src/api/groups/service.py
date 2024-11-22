from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from starlette import status

from core.database.models import Group, Organization, User

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
            group_data_dict.get("subgroup"),
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

    async def update_user(
        self, group: Group, group_data: dict, session: AsyncSession
    ) -> Group:
        for k, v in group_data.items():
            setattr(group, k, v)

        await session.commit()
        return group

    async def group_exists(
        self,
        organization_id: int,
        facult: str,
        course: int,
        subgroup: int,
        session: AsyncSession,
    ) -> bool:
        statement = select(Group).where(
            Group.organization_id == organization_id,
            Group.facult == facult,
            Group.course == course,
            Group.subgroup == subgroup,
        )
        result = await session.execute(statement)
        return result.scalars().first() is not None

    async def get_organization(self, org_id, session: AsyncSession) -> Organization:
        statement = select(Organization).where(Organization.id == org_id)
        result = await session.execute(statement)
        organization = result.scalars().first()
        return organization
