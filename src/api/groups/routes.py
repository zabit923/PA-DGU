from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.groups.schemas import GroupCreate, GroupRead
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
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied."
        )
    new_group = await group_service.create_group(group_data, user.id, session)
    return new_group
