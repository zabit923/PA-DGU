import os
from typing import Optional

from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from starlette import status

from config import media_dir
from core.database.models import User
from core.utils import save_file

from .schemas import UserCreate, UserUpdate
from .utils import generate_passwd_hash


class UserService:
    async def get_user_by_id(self, user_id: int, session: AsyncSession):
        statement = select(User).where(User.id == user_id)
        result = await session.execute(statement)
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return user

    async def get_user_by_username(self, username: str, session: AsyncSession):
        statement = select(User).where(User.username == username)
        result = await session.execute(statement)
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return user

    async def get_user_by_email(self, email: str, session: AsyncSession):
        statement = select(User).where(User.email == email)
        result = await session.execute(statement)
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return user

    async def user_exists(self, username: str, session: AsyncSession):
        user = await self.get_user_by_username(username, session)
        return True if user else False

    async def create_user(
        self,
        user_data: UserCreate,
        session: AsyncSession,
        image_file: Optional[UploadFile],
    ):
        user_data_dict = user_data.model_dump()
        new_user = User(**user_data_dict)
        new_user.image = await save_file(image_file) if image_file else "user.png"
        new_user.password = generate_passwd_hash(user_data_dict["password"])
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user

    async def update_user(
        self,
        user: User,
        user_data: UserUpdate,
        session: AsyncSession,
        image_file: Optional[UploadFile],
    ):
        if image_file and user.image != "user.png":
            old_image_path = os.path.join(media_dir, user.image)
            if os.path.exists(old_image_path):
                os.remove(old_image_path)
            user.image = await save_file(image_file)
        user_data_dict = user_data.model_dump(exclude_unset=True)
        for key, value in user_data_dict.items():
            if value is None:
                continue
            setattr(user, key, value)
        await session.commit()
        await session.refresh(user)
        return user
