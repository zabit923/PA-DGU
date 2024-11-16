from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from core.database.db import get_async_session
from core.database.models import User

from .dependencies import get_current_user
from .schemas import Token, UserCreate, UserLogin, UserRead, UserUpdate
from .service import UserService
from .utils import create_access_token, verify_password

router = APIRouter(prefix="/users")
user_service = UserService()


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserRead)
async def register_user(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_async_session),
):
    user_exist = await user_service.user_exists(user_data.username, session)
    if user_exist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User already exist."
        )
    new_user = await user_service.create_user(user_data, session)
    return new_user


@router.post("/login", status_code=status.HTTP_201_CREATED, response_model=Token)
async def login_user(
    login_data: UserLogin,
    session: AsyncSession = Depends(get_async_session),
):
    user = await user_service.get_user_by_username(login_data.username, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user."
        )
    password_valid = verify_password(
        password=login_data.password, password_hash=user.password
    )
    if password_valid:
        access_token = create_access_token(
            username=user.username, user_id=user.id, expires_delta=timedelta(hours=24)
        )
        refresh_token = create_access_token(
            username=user.username, user_id=user.id, expires_delta=timedelta(days=2)
        )
        return {"access_token": access_token, "refresh_token": refresh_token}
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials."
    )


@router.post(
    "/users/upload-image", status_code=status.HTTP_200_OK, response_model=UserRead
)
async def upload_user_image(
    image: UploadFile,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    updated_user = await user_service.update_user_image(user, image, session)
    return updated_user


@router.patch("/update-user", status_code=status.HTTP_200_OK, response_model=UserRead)
async def update_user(
    user_data: UserUpdate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    updated_user = await user_service.update_user_image(user, user_data, session)
    return updated_user


@router.get("/get-me", status_code=status.HTTP_200_OK, response_model=UserRead)
async def get_current_user(user: User = Depends(get_current_user)):
    return user
