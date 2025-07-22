from typing import List, Optional

from sqlalchemy import or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UserNotFoundError
from app.core.security.password import PasswordHasher
from app.models import (
    Exam,
    Group,
    GroupMessage,
    Lecture,
    PrivateMessage,
    PrivateRoom,
    User,
)
from app.schemas import (
    PaginationParams,
    PasswordFormSchema,
    PasswordUpdateResponseSchema,
    UserSchema,
    UserUpdateSchema,
)
from app.services.v1.base import BaseEntityManager


class UserDataManager(BaseEntityManager[UserSchema]):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, schema=UserSchema, model=User)

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

    async def get_users(
        self,
        pagination: PaginationParams,
        search: str = None,
    ) -> tuple[List[UserSchema], int]:
        statement = select(self.model).distinct()
        if search:
            statement = statement.filter(
                or_(
                    self.model.username.ilike(f"%{search}%"),
                    self.model.email.ilike(f"%{search}%"),
                )
            )
        return await self.get_paginated_items(statement, pagination)

    async def get_by_lecture(self, lecture: Lecture) -> List[UserSchema]:
        statement = (
            select(self.model)
            .join(self.model.member_groups)
            .join(Group.lectures)
            .where(Lecture.id == lecture.id)
            .where(self.model.is_teacher.is_(False))
            .distinct()
        )
        return await self.get_all(statement)

    async def get_by_exam(self, exam: Exam) -> List[UserSchema]:
        statement = (
            select(self.model)
            .join(self.model.member_groups)
            .join(Group.exams)
            .where(Exam.id == exam.id)
            .distinct()
        )
        return await self.get_all(statement)

    async def get_by_group(self, group: Group) -> UserSchema:
        statement = select(self.model).where(
            self.model.member_groups.any(Group.id == group.id)
        )
        return await self.get_one(statement)

    async def get_users_by_private_message(
        self, message: PrivateMessage
    ) -> List[UserSchema]:
        statement = (
            select(self.model)
            .join(self.model.rooms)
            .join(PrivateRoom.messages)
            .where(PrivateMessage.id == message.id)
        )
        return await self.get_all(statement)

    async def get_users_by_group_message(
        self, message: GroupMessage
    ) -> List[UserSchema]:
        statement = (
            select(self.model)
            .join(self.model.member_groups)
            .join(Group.group_messages)
            .where(GroupMessage.id == message.id)
        )
        return await self.get_all(statement)

    async def update_user(self, user: User, data: UserUpdateSchema) -> UserSchema:
        user_data_dict = data.model_dump(exclude_unset=True, exclude_none=True)
        for key, value in user_data_dict.items():
            setattr(user, key, value)
        return await self.update_one(user)

    async def update_image(self, user: User, image_url: str) -> None:
        try:
            await self.update_items(user.id, {"image": image_url})
        except (ValueError, SQLAlchemyError):
            self.logger.error("Не удалось обновить изображение %s", user.id)
            raise RuntimeError(f"Не удалось обновить изображение {user.id}")

    async def update_password(
        self, current_user: User, password_data: PasswordFormSchema
    ) -> PasswordUpdateResponseSchema:
        user_model = await self.get_model_by_field("id", current_user.id)
        if not user_model:
            raise UserNotFoundError(
                field="id",
                value=current_user.id,
            )
        new_password = PasswordHasher.hash_password(password_data.new_password)
        await self.update_items(current_user.id, {"password": new_password})
        return PasswordUpdateResponseSchema()
