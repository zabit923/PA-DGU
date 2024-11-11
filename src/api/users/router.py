from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from core.database.db import get_async_session
from core.database.models import User
from core.utils.protect import protected_endpoint

from .dependencies import authenticate_user, bcrypt_context, create_token_access
from .schemas import Token, UserCreate, UserLogin, UserRead

router = APIRouter(
    prefix="/users",
)


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserRead)
async def register_user(
    create_user_schema: UserCreate,
    session: AsyncSession = Depends(get_async_session),
):
    new_user = User(
        username=create_user_schema.username,
        first_name=create_user_schema.first_name,
        last_name=create_user_schema.last_name,
        email=create_user_schema.email,
        is_teacher=create_user_schema.is_teacher,
        hashed_password=bcrypt_context.hash(create_user_schema.password),
    )

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user


@router.post("/login", status_code=status.HTTP_201_CREATED, response_model=Token)
async def login_user(
    login_schema: UserLogin,
    session: AsyncSession = Depends(get_async_session),
):
    user = await authenticate_user(
        login_schema.username, login_schema.password, session
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Could bot validate user."
        )
    token = await create_token_access(user.username, user.id, timedelta(hours=24))

    return {"access_token": token, "token_type": "bearer"}


@router.get("/get_me", status_code=status.HTTP_200_OK, response_model=UserRead)
async def get_me(current_user: User = Depends(protected_endpoint)):
    return current_user


@router.get("/test", status_code=status.HTTP_200_OK)
async def get_protected_route(_=Depends(protected_endpoint)):
    return {"message": "success"}
