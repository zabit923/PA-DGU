from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, UploadFile
from pydantic import EmailStr
from starlette import status
from sqlalchemy.exc import IntegrityError

from config import BASE_URL
from core.tasks import send_activation_email

from .dependencies import get_current_user
from .schemas import (
    Token,
    UserCreate,
    UserLogin,
    UserRead,
    UserShort,
    UserUpdate,
    PasswordResetConfirmResponseSchema,
    PasswordResetConfirmSchema,
    ForgotPasswordSchema,
    PasswordResetResponseSchema
)
from .service import UserService, user_service_factory

router = APIRouter(prefix="/users")


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserShort)
async def register_user(
    username: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: EmailStr = Form(...),
    password: str = Form(...),
    is_teacher: bool = Form(...),
    image: Optional[UploadFile] = File(None),
    user_service: UserService = Depends(user_service_factory),
):
    try:
        user_data = UserCreate(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            is_teacher=is_teacher,
        )
        new_user = await user_service.create_user(user_data, image)
        activation_link = f"{BASE_URL}/users/activate/{new_user.id}"
        send_activation_email.delay(
            email=email, username=username, activation_link=activation_link
        )
        return new_user
    
    except IntegrityError as e:
        raise HTTPException(
            status_code=400,
            detail="Пользователь с такими данными уже существует"            
        )


@router.get(
    "/activate/{user_id}", status_code=status.HTTP_200_OK, response_model=UserRead
)
async def activate_user(
    user_id: int, user_service: UserService = Depends(user_service_factory)
):
    return await user_service.activate_user(user_id)


@router.post("/login", status_code=status.HTTP_201_CREATED, response_model=Token)
async def login_user(
    login_data: UserLogin, user_service: UserService = Depends(user_service_factory)
):
    tokens = await user_service.authenticate_user(login_data)
    return {
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
    }


@router.patch("", status_code=status.HTTP_200_OK, response_model=UserRead)
async def update_user(
    username: str = Form(None),
    first_name: str = Form(None),
    last_name: str = Form(None),
    email: EmailStr = Form(None),
    is_teacher: bool = Form(None),
    image: Optional[UploadFile] = File(None),
    user=Depends(get_current_user),
    user_service: UserService = Depends(user_service_factory),
):
    user_data = UserUpdate(
        username=username,
        first_name=first_name,
        last_name=last_name,
        email=email,
        is_teacher=is_teacher,
    )
    return await user_service.update_user(user, user_data, image)


@router.get("/get-me", status_code=status.HTTP_200_OK, response_model=UserRead)
async def get_me(user=Depends(get_current_user)):
    return user


@router.get("", status_code=status.HTTP_200_OK, response_model=List[UserRead])
async def get_all_users(
    user=Depends(get_current_user),
    user_service: UserService = Depends(user_service_factory),
):
    return await user_service.get_all_users(user)


@router.get(
    "/change-online-status", status_code=status.HTTP_200_OK, response_model=UserRead
)
async def change_user_status(
    user=Depends(get_current_user),
    user_service: UserService = Depends(user_service_factory),
):
    return await user_service.change_online_status(user)


@router.get(
    "/change-ignore-status", status_code=status.HTTP_200_OK, response_model=UserRead
)
async def set_user_ignore(
    user=Depends(get_current_user),
    user_service: UserService = Depends(user_service_factory),
):
    return await user_service.change_ignore_status(user)


@router.get("/{user_id}", status_code=status.HTTP_200_OK, response_model=UserRead)
async def get_user(
    user_id: int, user_service: UserService = Depends(user_service_factory)
):
    return await user_service.get_user_by_id(user_id)


@router.post(
    path="/forgot-password",
    response_model=PasswordResetResponseSchema,
    summary="Запрос восстановления пароля",
)
async def forgot_password(
    request: ForgotPasswordSchema,
    user_service: UserService = Depends(user_service_factory),
) -> PasswordResetResponseSchema:
    return await user_service.send_password_reset_email(
        request.email
    )


@router.post(
    path="/reset-password/{reset_token}",
    response_model=PasswordResetConfirmResponseSchema,
    summary="Подтверждение сброса пароля",
)
async def reset_password(
    reset_token: str,
    reset_data: PasswordResetConfirmSchema,
    user_service: UserService = Depends(user_service_factory),
) -> PasswordResetConfirmResponseSchema:
    return await user_service.reset_password(reset_data, reset_token)
