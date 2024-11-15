from fastapi import APIRouter

from api.users.service import UserService

router = APIRouter(prefix="/groups")
user_service = UserService()


# @router.post("/create_group", status_code=status.HTTP_201_CREATED, response_model=)
