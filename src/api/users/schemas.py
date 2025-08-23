from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator, Field
from pydantic_core.core_schema import ValidationInfo

import config
from config import settings


class Token(BaseModel):
    access_token: str
    refresh_token: str


class UserCreate(BaseModel):
    username: str
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    is_teacher: bool


class UserLogin(BaseModel):
    username: str
    password: str


class UserRead(BaseModel):
    id: int
    username: str
    first_name: str
    last_name: str
    email: EmailStr
    is_teacher: bool
    is_online: bool
    is_active: bool
    is_superuser: bool
    image: Optional[str]
    created_at: datetime
    created_groups: Optional[List["GroupShort"]] = []
    member_groups: Optional[List["GroupShort"]] = []

    model_config = ConfigDict(from_attributes=True)

    @field_validator("image", mode="before")
    def create_image_url(cls, value: Optional[object]) -> Optional[str]:
        if config.DEBUG:
            return (
                f"http://{settings.run.host}:{settings.run.port}/static/media/{value}"
            )
        return f"{settings.url}/static/media/{value}"


class UserShort(BaseModel):
    id: int
    username: str
    first_name: str
    last_name: str
    email: EmailStr
    is_teacher: bool
    is_online: bool
    is_superuser: bool
    image: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_validator("image", mode="before")
    def create_image_url(cls, value: Optional[object]) -> Optional[str]:
        if config.DEBUG:
            return (
                f"http://{settings.run.host}:{settings.run.port}/static/media/{value}"
            )
        return f"{settings.url}/static/media/{value}"


class UserUpdate(BaseModel):
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_teacher: Optional[bool] = None


class PasswordResetDataSchema(BaseModel):
    email: EmailStr = Field(
        description="Email адрес для восстановления пароля", example="user@example.com"
    )
    expires_in: int = Field(
        description="Время действия ссылки восстановления в секундах", example=1800
    )


class PasswordResetConfirmDataSchema(BaseModel):
    password_changed_at: datetime = Field(
        description="Время изменения пароля в формате UTC",
        example="2024-01-15T10:35:00Z",
    )


class ForgotPasswordSchema(BaseModel):
    email: EmailStr = Field(description="Email адрес для восстановления пароля")


class PasswordResetConfirmSchema(BaseModel):
    new_password: str = Field(description="Новый пароль", min_length=8, max_length=128)
    confirm_password: str = Field(
        description="Подтверждение нового пароля", min_length=8, max_length=128
    )

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v: str, info: ValidationInfo) -> str:
        new_password = info.data.get("new_password")
        if new_password is not None and v != new_password:
            raise ValueError("Пароли не совпадают")
        return v


class PasswordResetResponseSchema(BaseModel):
    data: PasswordResetDataSchema


class PasswordResetConfirmResponseSchema(BaseModel):
    data: PasswordResetConfirmDataSchema


from api.groups.schemas import GroupShort

UserRead.model_rebuild()
UserCreate.model_rebuild()
