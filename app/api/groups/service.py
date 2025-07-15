from typing import Sequence

from config import settings
from core.database import get_async_session
from core.database.models import Group, User
from core.database.repositories import GroupRepository
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from .schemas import GroupCreate, GroupUpdate, UserKickList


class GroupService:
    def __init__(self, repository: GroupRepository):
        self.repository = repository

    async def get_group(self, group_id: int) -> Group:
        group = await self.repository.get_by_id(group_id)
        if not group:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return group

    async def get_my_groups(self, user: User) -> Sequence[Group]:
        groups = await self.repository.get_my_groups(user)
        return groups

    async def get_my_created_groups(self, user: User) -> Sequence[Group]:
        if not user.is_teacher:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="You are not teacher."
            )
        groups = await self.repository.get_by_curator(user)
        return groups

    async def create_group(self, group_data: GroupCreate, user: User) -> Group:
        if not user.is_teacher:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="You are not teacher."
            )
        group = await self.repository.create(group_data, user)
        return group

    async def update_group(
        self, group_id: int, group_data: GroupUpdate, user: User
    ) -> Group:
        if not user.is_teacher:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="You are not teacher."
            )
        group = await self.repository.get_by_id(group_id)
        group_data_dict = group_data.model_dump(exclude_unset=True)
        for key, value in group_data_dict.items():
            if value is None:
                continue
            setattr(group, key, value)
        await self.repository.update(group)
        return group

    async def get_all_groups(self) -> Sequence[Group]:
        return await self.repository.get_all()

    async def delete_group(self, group_id: int, user: User) -> None:
        group = await self.repository.get_by_id(group_id)
        if not group:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        if group.methodist != user:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        await self.repository.delete(group)

    async def generate_invite_link(self, group_id: int, user: User) -> str:
        group = await self.repository.get_by_id(group_id)
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Group not found."
            )
        if group.methodist != user:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        await self.repository.generate_invite_link(group)
        return f"http://{settings.run.host}:{settings.run.port}/api/v1/groups/join/{group.invite_token}"

    async def join_group_by_invite(self, invite_token: str, user: User) -> Group:
        group = await self.repository.get_by_invite_token(invite_token)
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Invalid invite link."
            )
        if user in group.members:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a member.",
            )
        await self.repository.join_group(user, group)
        return group

    async def leave_group(self, group_id: int, user: User) -> None:
        group = await self.repository.get_by_id(group_id)
        if group.methodist == user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="The curator cannot leave the group.",
            )
        if user not in group.members:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this group.",
            )
        await self.repository.delete_from_group(group, user)

    async def kick_users_from_group(
        self, group_id: int, data: UserKickList, user: User
    ):
        group = await self.repository.get_by_id(group_id)
        if group.methodist != user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the curator can kick users from the group.",
            )
        if user.id in data.users_list:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="You can't kick yourself."
            )

        for user_id in data.users_list:
            member = next((m for m in group.members if m.id == user_id), None)
            if member:
                await self.repository.delete_from_group(group, member)

    async def contrained_user_in_group(
        self,
        user: User,
        group_id: int,
    ) -> True | False:
        group = await self.repository.get_by_id(group_id)
        return True if user in group.members else False


def group_service_factory(
    session: AsyncSession = Depends(get_async_session),
) -> GroupService:
    return GroupService(GroupRepository(session))
