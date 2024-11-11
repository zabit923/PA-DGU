from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from starlette.responses import JSONResponse

from core.auth.users import UserManager, auth_backend, fastapi_users, get_user_manager

from .schemas import UserCreate, UserLogin, UserRead

router = APIRouter(
    prefix="/api/v1",
)


@router.post("/login")
async def login(
    login_data: UserLogin,
    user_manager: UserManager = Depends(get_user_manager),
):
    user = await user_manager.authenticate(
        credentials={"username": login_data.username, "password": login_data.password}
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    response = await auth_backend.get_login_response(user, user_manager)
    return JSONResponse(content=response)


router.include_router(
    router=fastapi_users.get_register_router(
        UserRead,
        UserCreate,
    ),
)

router.include_router(
    router=fastapi_users.get_verify_router(UserRead),
)


router.include_router(
    router=fastapi_users.get_reset_password_router(),
)
