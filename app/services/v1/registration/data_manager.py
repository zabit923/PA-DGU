from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UserCreationError, UserExistsError
from app.core.security.password import PasswordHasher
from app.models import User
from app.schemas import RegistrationRequestSchema
from app.services.v1.users.data_manager import UserDataManager


class RegisterDataManager(UserDataManager):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def validate_user_uniqueness(self, email: str) -> None:
        conditions = [User.email == email]

        statement = select(User).where(or_(*conditions))
        existing_user = await self.get_one(statement)

        if existing_user:
            raise UserExistsError("email", email)

    async def create_user_from_registration(
        self, user_data: RegistrationRequestSchema
    ) -> User:
        try:
            user_model = User(
                username=user_data.username,
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                email=user_data.email,
                password=PasswordHasher.hash_password(user_data.password),
                is_verified=False,
                is_superuser=False,
                is_teacher=False,
            )

            created_user = await self.add_one(user_model)

            self.logger.info(
                "Пользователь создан в базе данных: ID=%s", created_user.id
            )
            return created_user

        except Exception as e:
            self.logger.error("Ошибка создания пользователя в БД: %s", e, exc_info=True)
            raise UserCreationError("Не удалось создать пользователя") from e
