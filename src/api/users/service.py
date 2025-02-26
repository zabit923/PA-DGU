import os
from datetime import timedelta
from typing import List, Optional

from fastapi import Depends, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from config import media_dir
from core.database import get_async_session
from core.database.models import User
from core.database.repositories import UserRepository
from core.utils import save_file

from .schemas import UserCreate, UserLogin, UserUpdate
from .utils import create_access_token, generate_passwd_hash, verify_password


class UserService:
    def __init__(self, repository):
        self.repository = repository

    async def get_user_by_id(self, user_id: int) -> User:
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return user

    async def get_user_by_username(self, username: str) -> User:
        user = await self.repository.get_by_username(username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return user

    async def get_user_by_email(self, email: str) -> User:
        user = await self.repository.get_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return user

    async def get_all_users(self, user: User) -> List[User]:
        if not user.is_superuser:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        users = await self.repository.get_all()
        return users

    async def user_exists(self, username: str) -> bool:
        user = await self.repository.get_by_username(username)
        return user is not None

    async def create_user(
        self, user_data: UserCreate, image_file: Optional[UploadFile]
    ) -> User:
        user_data_dict = user_data.model_dump()
        new_user = User(**user_data_dict)
        new_user.image = await save_file(image_file) if image_file else "user.png"
        new_user.password = generate_passwd_hash(user_data_dict["password"])

        await self.repository.add(new_user)
        return new_user

    async def authenticate_user(self, login_data: UserLogin):
        user = await self.get_user_by_username(login_data.username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate user.",
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
                username=user.username,
                user_id=user.id,
                expires_delta=timedelta(hours=24),
            )
            refresh_token = create_access_token(
                username=user.username,
                user_id=user.id,
                expires_delta=timedelta(days=2),
                refresh=True,
            )
            return {"access_token": access_token, "refresh_token": refresh_token}
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials."
        )

    async def update_user(
        self, user: User, user_data: UserUpdate, image_file: Optional[UploadFile]
    ) -> User:
        if image_file:
            await self._update_user_image(user, image_file)
        user_data_dict = user_data.model_dump(exclude_unset=True, exclude_none=True)
        for key, value in user_data_dict.items():
            setattr(user, key, value)
        await self.repository.update(user)
        return user

    @staticmethod
    async def _update_user_image(user: User, image_file: UploadFile) -> None:
        if user.image and user.image != "user.png":
            old_image_path = os.path.join(media_dir, user.image)
            if os.path.exists(old_image_path):
                os.remove(old_image_path)
        user.image = await save_file(image_file)

    async def activate_user(self, user_id: int) -> User:
        user = await self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
            )
        if user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already active.",
            )
        await self.repository.update(user)
        return user

    async def change_online_status(self, user: User) -> User:
        if user.is_online:
            user.is_online = False
        else:
            user.is_online = True
        await self.repository.update(user)
        return user

    async def change_ignore_status(self, user: User) -> User:
        if user.ignore_messages:
            user.ignore_messages = False
        else:
            user.ignore_messages = True
        await self.repository.update(user)
        return user


def user_service(session: AsyncSession = Depends(get_async_session)):
    return UserService(UserRepository(session))
