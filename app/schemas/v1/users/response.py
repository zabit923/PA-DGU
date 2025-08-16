from typing import Optional

from pydantic import EmailStr

from app.schemas.v1.base import BaseResponseSchema, BaseSchema
from app.schemas.v1.pagination import Page


class UserShortSchema(BaseSchema):
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: EmailStr
    image: Optional[str] = None

    is_superuser: bool = False
    is_teacher: bool = False
    is_online: bool = False
    is_verified: bool = False


class UserListResponseSchema(BaseResponseSchema):
    message: str = "Список пользователей успешно получен"
    data: Page[UserShortSchema]


class PasswordUpdateResponseSchema(BaseResponseSchema):
    message: str = "Пароль успешно изменен"
