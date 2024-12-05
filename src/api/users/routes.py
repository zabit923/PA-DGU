from datetime import timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from config import settings
from core.database.db import get_async_session
from core.database.models import User
from tasks import send_activation_email

from .dependencies import get_current_user
from .schemas import Token, UserCreate, UserLogin, UserRead, UserShort, UserUpdate
from .service import UserService
from .utils import create_access_token, verify_password

router = APIRouter(prefix="/users")
user_service = UserService()


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserShort)
async def register_user(
    username: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: EmailStr = Form(...),
    password: str = Form(...),
    is_teacher: bool = Form(...),
    image: Optional[UploadFile] = File(None),
    session: AsyncSession = Depends(get_async_session),
):
    user_data = UserCreate(
        username=username,
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=password,
        is_teacher=is_teacher,
    )
    user_exist = await user_service.user_exists(user_data.username, session)
    if user_exist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User already exist."
        )
    new_user = await user_service.create_user(user_data, session, image)

    activation_link = f"http://{settings.run.host}:{settings.run.port}/api/v1/users/activate/{new_user.id}"
    send_activation_email.delay(
        email=email, username=username, activation_link=activation_link
    )
    return new_user


@router.get("/activate/{user_id}", status_code=status.HTTP_200_OK)
async def activate_user(
    user_id: int, session: AsyncSession = Depends(get_async_session)
):
    user = await user_service.get_user_by_id(user_id, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )
    if user.is_active:
        return {"message": "User is already active."}
    user.is_active = True
    await session.commit()
    return {"message": "User successfully activated."}


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
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User is not activated."
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


@router.patch("/update-user", status_code=status.HTTP_200_OK, response_model=UserRead)
async def update_user(
    username: str = Form(None),
    first_name: str = Form(None),
    last_name: str = Form(None),
    email: EmailStr = Form(None),
    is_teacher: bool = Form(None),
    image: Optional[UploadFile] = File(None),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    user_data = UserUpdate(
        username=username,
        first_name=first_name,
        last_name=last_name,
        email=email,
        is_teacher=is_teacher,
    )
    updated_user = await user_service.update_user(user, user_data, session, image)
    return updated_user


@router.get("/get-me", status_code=status.HTTP_200_OK, response_model=UserRead)
async def get_current_user(user: User = Depends(get_current_user)):
    return user


@router.get(
    "/get-all-users", status_code=status.HTTP_200_OK, response_model=List[UserRead]
)
async def get_all_users(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    if not user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    statement = select(User)
    result = await session.execute(statement)
    users = result.scalars().all()
    return users
