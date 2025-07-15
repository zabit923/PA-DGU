from datetime import datetime

from pydantic import EmailStr, Field

from app.schemas.v1.base import BaseCommonResponseSchema


class TokenDataSchema(BaseCommonResponseSchema):
    access_token: str = Field(
        description="JWT токен доступа для авторизации запросов",
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    )
    refresh_token: str = Field(
        description="Токен для обновления access_token",
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    )
    token_type: str = Field(
        default="Bearer", description="Тип токена для заголовка Authorization"
    )
    expires_in: int = Field(
        description="Время жизни access_token в секундах", example=1800
    )


class LogoutDataSchema(BaseCommonResponseSchema):
    logged_out_at: datetime = Field(
        description="Время выхода из системы в формате UTC",
        example="2024-01-15T10:30:00Z",
    )


class PasswordResetDataSchema(BaseCommonResponseSchema):
    email: EmailStr = Field(
        description="Email адрес для восстановления пароля", example="user@example.com"
    )
    expires_in: int = Field(
        description="Время действия ссылки восстановления в секундах", example=1800
    )


class PasswordResetConfirmDataSchema(BaseCommonResponseSchema):
    password_changed_at: datetime = Field(
        description="Время изменения пароля в формате UTC",
        example="2024-01-15T10:35:00Z",
    )
