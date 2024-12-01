from typing import List

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.groups.schemas import GroupCreate, GroupRead, GroupUpdate
from api.groups.service import GroupService
from api.users.dependencies import get_current_user
from core.database import get_async_session
from core.database.models import Group, User

router = APIRouter(prefix="/groups")
group_service = GroupService()


@router.post(
    "/create-group", status_code=status.HTTP_201_CREATED, response_model=GroupRead
)
async def create_group(
    group_data: GroupCreate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    if not user.is_teacher:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You are not teacher."
        )
    new_group = await group_service.create_group(group_data, user, session)
    return new_group


@router.patch(
    "/update-group/{group_id}", status_code=status.HTTP_200_OK, response_model=GroupRead
)
async def update_group(
    group_id: int,
    group_data: GroupUpdate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    if not user.is_teacher:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You are not teacher."
        )
    new_group = await group_service.update_group(group_id, group_data, session)
    return new_group


@router.get(
    "/get-all-groups", status_code=status.HTTP_200_OK, response_model=List[GroupRead]
)
async def get_all_groups(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    if not user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    statement = select(Group)
    result = await session.execute(statement)
    groups = result.scalars().all()
    return groups


@router.get(
    "/get-my-created-groups",
    status_code=status.HTTP_200_OK,
    response_model=List[GroupRead],
)
async def get_my_created_groups(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    if not user.is_teacher:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You are not teacher."
        )
    groups = await group_service.get_my_groups(user, session)
    return groups


@router.get(
    "/get-my-groups", status_code=status.HTTP_200_OK, response_model=List[GroupRead]
)
async def get_my_groups(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    statement = select(Group).where(Group.members.contains(user))
    result = await session.execute(statement)
    groups = result.scalars().all()
    return groups
