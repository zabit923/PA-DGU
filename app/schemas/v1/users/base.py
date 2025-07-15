from typing import Optional

from pydantic import EmailStr, Field

from app.schemas.v1.base import CommonBaseSchema, UserBaseSchema


class UserSchema(UserBaseSchema):
    username: str = Field(description="Имя пользователя")
    first_name: Optional[str] = Field(default=None, description="Имя")
    last_name: Optional[str] = Field(default=None, description="Фамилия")
    email: EmailStr = Field(description="Email адрес")
    image: Optional[str] = Field(default=None, description="URL аватара")

    is_superuser: bool = Field(default=False, description="Статус суперпользователя")
    is_teacher: bool = Field(default=False, description="Статус преподавателя")
    is_online: bool = Field(default=False, description="Статус онлайн")
    is_verified: bool = Field(default=True, description="Статус верификации")
    ignore_messages: bool = Field(default=False, description="Игнорировать сообщения")


class UserCredentialsSchema(CommonBaseSchema):
    id: int = Field(description="Уникальный идентификатор пользователя")
    username: Optional[str] = Field(None, description="Имя пользователя")
    email: EmailStr = Field(description="Email адрес пользователя")
    password: str = Field(description="Хешированный пароль")
    is_verified: bool = Field(default=False, description="Статус верификации")
