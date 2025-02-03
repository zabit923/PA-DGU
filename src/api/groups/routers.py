from typing import List

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import Response

from api.groups.schemas import GroupCreate, GroupRead, GroupUpdate, UserKickList
from api.groups.service import GroupService
from api.users.dependencies import get_current_user
from core.database import get_async_session
from core.database.models import Group, User

router = APIRouter(prefix="/groups")
group_service = GroupService()


@router.post("", status_code=status.HTTP_201_CREATED, response_model=GroupRead)
async def create_group(
    group_data: GroupCreate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    new_group = await group_service.create_group(group_data, user, session)
    return new_group


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


@router.get(
    "/get-my-created-groups",
    status_code=status.HTTP_200_OK,
    response_model=List[GroupRead],
)
async def get_my_created_groups(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    groups = await group_service.get_my_created_groups(user, session)
    return groups


@router.get("/{group_id}", status_code=status.HTTP_200_OK, response_model=GroupRead)
async def get_group(
    group_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    group = await group_service.get_group(group_id, session)
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if user not in group.members:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return group


@router.patch("/{group_id}", status_code=status.HTTP_200_OK, response_model=GroupRead)
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


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group(
    group_id: int,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(get_current_user),
):
    await group_service.delete_group(group_id, user, session)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("", status_code=status.HTTP_200_OK, response_model=List[GroupRead])
async def get_all_groups(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    if not user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    groups = await group_service.get_all_groups(session)
    return groups


@router.post("/invite/{group_id}", status_code=status.HTTP_200_OK)
async def invite_to_group(
    group_id: int,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(get_current_user),
):
    group = await group_service.get_group(group_id, session)
    if not group or group.curator != user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    invite_url = await group_service.generate_invite_link(group_id, session)
    return invite_url


@router.get(
    "/join/{invite_token}", status_code=status.HTTP_200_OK, response_model=GroupRead
)
async def join_group(
    invite_token: str,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(get_current_user),
):
    group = await group_service.join_group_by_invite(invite_token, user, session)
    return group


@router.get("/group-leave/{group_id}", status_code=status.HTTP_200_OK)
async def group_leave(
    group_id: int,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(get_current_user),
):
    await group_service.leave_group(group_id, user, session)
    return {"message": "Success."}


@router.post("/kick-user/{group_id}", status_code=status.HTTP_200_OK)
async def kick_user(
    group_id: int,
    data: UserKickList,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(get_current_user),
):
    await group_service.kick_users_from_group(group_id, data, user, session)
    return {"message": "Successfully removed user(s) from the group."}
