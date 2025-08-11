import re

from pydantic import EmailStr, Field, field_validator

from app.schemas.v1.base import BaseRequestSchema


class AuthSchema(BaseRequestSchema):
    username: str = Field(
        description="Имя пользователя, email или телефон в формате +7 (XXX) XXX-XX-XX",
        examples=["user@example.com", "john_doe", "+7 999 123-45-67"],
    )
    password: str = Field(
        description="Пароль (минимум 8 символов, заглавная и строчная буква, цифра, спецсимвол",
    )

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        if "@" in v:
            return v

        if v.startswith("+7"):
            phone_pattern = r"^\+7 \(\d{3}\) \d{3}-\d{2}-\d{2}$"
            if not re.match(phone_pattern, v):
                raise ValueError(
                    "Неверный формат телефона. Используйте: +7 (XXX) XXX-XX-XX"
                )
            return v

        if len(v) < 3:
            raise ValueError("Username должен содержать минимум 3 символа")

        return v


class ForgotPasswordSchema(BaseRequestSchema):
    email: EmailStr = Field(description="Email адрес для восстановления пароля")


class PasswordResetConfirmSchema(BaseRequestSchema):
    token: str = Field(description="Токен восстановления пароля")
    new_password: str = Field(description="Новый пароль", min_length=8, max_length=128)
    confirm_password: str = Field(
        description="Подтверждение нового пароля", min_length=8, max_length=128
    )

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v, values):
        if "new_password" in values and v != values["new_password"]:
            raise ValueError("Пароли не совпадают")
        return v
