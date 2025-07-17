from typing import Optional

from pydantic import EmailStr

from app.schemas.v1.base import BaseResponseSchema, BaseSchema
from app.schemas.v1.pagination import Page

# from app.schemas.groups import GroupShort


class UserReadSchema(BaseSchema):
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: EmailStr
    image: Optional[str]

    is_superuser: bool = False
    is_teacher: bool = False
    is_online: bool = False
    is_verified: bool = False
    ignore_messages: bool = False

    # created_groups: Optional[List["GroupShort"]]
    # member_groups: Optional[List["GroupShort"]]


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


class UserUpdateResponseSchema(BaseResponseSchema):
    message: str = "Данные пользователя успешно обновлены"
    data: UserReadSchema


class UserListResponseSchema(BaseResponseSchema):
    message: str = "Список пользователей успешно получен"
    data: Page[UserShortSchema]


class PasswordUpdateResponseSchema(BaseResponseSchema):
    message: str = "Пароль успешно изменен"


UserReadSchema.model_rebuild()
