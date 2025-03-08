from fastapi import HTTPException
from fastapi.params import Depends
from starlette import status
from starlette.requests import Request

from api.users.service import UserService, user_service_factory


async def get_current_user(
    request: Request, user_service: UserService = Depends(user_service_factory)
):
    if request.user.is_authenticated:
        user = await user_service.get_user_by_id(request.user.id)
        return user
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
