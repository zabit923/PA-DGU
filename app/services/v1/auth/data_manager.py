from typing import Optional

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.schemas import UserCredentialsSchema
from app.services.v1.users.data_manager import UserDataManager


class AuthDataManager(UserDataManager):
    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.schema = UserCredentialsSchema

    async def get_user_by_identifier(self, identifier: str) -> Optional[User]:
        statement = select(User).where(
            or_(
                User.email == identifier,
                User.username == identifier,
            )
        )

        user = await self.get_one(statement)

        if user:
            self.logger.info(
                "Пользователь найден",
                extra={"identifier": identifier, "user_id": user.id},
            )
        else:
            self.logger.info("Пользователь не найден", extra={"identifier": identifier})

        return user
