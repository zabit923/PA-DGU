import os
from typing import Optional

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.database.models import User

from .schemas import UserCreate, UserUpdate
from .utils import generate_passwd_hash


class UserService:
    async def get_user_by_id(self, id: int, session: AsyncSession):
        statement = select(User).where(User.id == id)
        result = await session.execute(statement)
        user = result.scalars().first()
        return user

    async def get_user_by_username(self, username: str, session: AsyncSession):
        statement = select(User).where(User.username == username)
        result = await session.execute(statement)
        user = result.scalars().first()
        return user

    async def get_user_by_email(self, email: str, session: AsyncSession):
        statement = select(User).where(User.email == email)
        result = await session.execute(statement)
        user = result.scalars().first()
        return user

    async def user_exists(self, username: str, session: AsyncSession):
        user = await self.get_user_by_username(username, session)
        return True if user is not None else False

    async def create_user(
        self,
        user_data: UserCreate,
        session: AsyncSession,
        image_file: Optional[UploadFile] = None,
    ):
        user_data_dict = user_data.model_dump()
        new_user = User(**user_data_dict)
        new_user.password = generate_passwd_hash(user_data_dict["password"])
        session.add(new_user)
        await session.commit()

        if image_file:
            await self.update_user_image(new_user, image_file, session)

        return new_user

    async def update_user(
        self, user: User, user_data: UserUpdate, session: AsyncSession
    ):
        user_data_dict = user_data.model_dump()
        for k, v in user_data_dict.items():
            setattr(user, k, v)

        await session.commit()
        return user

    async def update_user_image(
        self, user: User, image_file: UploadFile, session: AsyncSession
    ):
        file_extension = image_file.filename.split(".")[-1]
        new_file_name = f"user_{user.id}.{file_extension}"
        file_path = os.path.join("../media", new_file_name)

        with open(file_path, "wb") as f:
            f.write(await image_file.read())

        user.image = new_file_name
        await session.commit()
        await session.refresh(user)

        return user
