from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.groups.schemas import GroupCreate, GroupRead, GroupUpdate
from api.groups.service import GroupService
from api.users.dependencies import get_current_user
from core.database import get_async_session
from core.database.models import User

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
