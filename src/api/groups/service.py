from typing import List

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from starlette import status

from config import settings
from core.database.models import Group, User

from .schemas import GroupCreate, GroupUpdate, UserKickList


class GroupService:
    async def get_group(self, group_id: int, session: AsyncSession) -> Group:
        statement = select(Group).where(Group.id == group_id)
        result = await session.execute(statement)
        group = result.scalars().first()
        return group

    async def get_my_created_groups(
        self, user: User, session: AsyncSession
    ) -> List[Group]:
        if not user.is_teacher:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="You are not teacher."
            )
        statement = select(Group).where(Group.curator == user)
        result = await session.execute(statement)
        groups = result.scalars().all()
        return groups

    async def create_group(
        self, group_data: GroupCreate, user: User, session: AsyncSession
    ) -> Group:
        if not user.is_teacher:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="You are not teacher."
            )
        group_data_dict = group_data.model_dump()
        new_group = Group(**group_data_dict, curator=user, members=[user])
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

    async def get_all_groups(self, session: AsyncSession) -> List[Group]:
        statement = select(Group)
        result = await session.execute(statement)
        groups = result.scalars().all()
        return groups

    async def delete_group(
        self, group_id: int, user: User, session: AsyncSession
    ) -> None:
        group = await self.get_group(group_id, session)
        if not group:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        if group.curator != user:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        await session.delete(group)
        await session.commit()

    async def generate_invite_link(self, group_id: int, session: AsyncSession) -> str:
        group = await self.get_group(group_id, session)
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Group not found."
            )

        group.generate_invite_token()
        await session.commit()
        return f"http://{settings.run.host}:{settings.run.port}/api/v1/groups/join/{group.invite_token}"

    async def join_group_by_invite(
        self, invite_token: str, user: User, session: AsyncSession
    ) -> Group:
        statement = select(Group).where(Group.invite_token == invite_token)
        result = await session.execute(statement)
        group = result.scalars().first()

        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Invalid invite link."
            )

        if user in group.members:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a member.",
            )

        group.members.append(user)
        await session.commit()
        return group

    async def leave_group(
        self, group_id: int, user: User, session: AsyncSession
    ) -> None:
        group = await self.get_group(group_id, session)

        if group.curator == user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="The curator cannot leave the group.",
            )

        if user not in group.members:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this group.",
            )

        group.members.remove(user)
        await session.commit()

    async def kick_users_from_group(
        self, group_id: int, data: UserKickList, user: User, session: AsyncSession
    ):
        group = await self.get_group(group_id, session)

        if group.curator != user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the curator can kick users from the group.",
            )

        statement = select(User).where(User.id.in_(data.users_list))
        result = await session.execute(statement)
        users_to_remove = result.scalars().all()

        if not users_to_remove:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No users found to remove.",
            )

        for user_to_remove in users_to_remove:
            if user_to_remove in group.members:
                group.members.remove(user_to_remove)

        await session.commit()
