from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.database.models import User

from .schemas import UserCreate
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

    async def create_user(self, user_data: UserCreate, session: AsyncSession):
        user_data_dict = user_data.model_dump()
        new_user = User(**user_data_dict)
        new_user.password = generate_passwd_hash(user_data_dict["password"])
        session.add(new_user)
        await session.commit()
        return new_user

    async def update_user(self, user: User, user_data: dict, session: AsyncSession):
        for k, v in user_data.items():
            setattr(user, k, v)

        await session.commit()
        return user
