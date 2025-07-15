from typing import Optional

from pydantic import EmailStr, Field, field_validator

from app.core.security.password import BasePasswordValidator
from app.schemas.v1.base import BaseRequestSchema, CommonBaseSchema


class UserUpdateSchema(CommonBaseSchema):
    username: Optional[str] = Field(None, description="Имя пользователя")
    first_name: Optional[str] = Field(None, description="Имя")
    last_name: Optional[str] = Field(None, description="Фамилия")
    email: Optional[EmailStr] = Field(None, description="Email адрес")


class PasswordFormSchema(BaseRequestSchema):
    new_password: str = Field(
        ...,
        description="Новый пароль (минимум 8 символов, заглавная и строчная буква, цифра, спецсимвол)",
        alias="new_password",
    )
    confirm_password: str = Field(..., description="Подтверждение нового пароля")

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v, info):
        validator = BasePasswordValidator()
        return validator.validate_password_strength(v)

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v, info):
        data = info.data
        if "new_password" in data and v != data["new_password"]:
            raise ValueError("Пароли не совпадают")
        return v
