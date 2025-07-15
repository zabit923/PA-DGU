from datetime import datetime
from typing import Optional

from pydantic import EmailStr, Field

from app.schemas.v1.base import BaseCommonResponseSchema


class RegistrationDataSchema(BaseCommonResponseSchema):
    id: int

    username: Optional[str] = Field(
        None,
        description="Имя пользователя для входа в систему",
        examples=["john_doe", "user123", "admin"],
    )
    first_name: str = Field(
        min_length=1,
        max_length=50,
        description="Имя пользователя. Должно содержать от 1 до 50 символов",
        examples=["John", "Alice"],
    )
    last_name: str = Field(
        min_length=1,
        max_length=50,
        description="Фамилия пользователя. Должна содержать от 1 до 50 символов",
        examples=["Doe", "Smith"],
    )
    email: EmailStr = Field(
        description="Email адрес пользователя",
        examples=["user@example.com", "john.doe@company.org"],
    )
    is_verified: bool = Field(
        default=False, description="Статус верификации email или телефона"
    )
    is_teacher: bool = Field(
        default=False,
        description="Является ли пользователь учителем (true) или учеником (false)",
    )
    created_at: datetime = Field(
        description="Дата и время создания аккаунта", examples=["2024-01-15T10:30:00Z"]
    )
    access_token: Optional[str] = Field(
        default=None,
        description="Ограниченный JWT токен доступа (до верификации email). "
        "Будет None если используются cookies (use_cookies=true)",
        examples=["eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...", None],
    )
    refresh_token: Optional[str] = Field(
        default=None,
        description="JWT токен для обновления access токена. "
        "Будет None если используются cookies (use_cookies=true)",
        examples=["eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...", None],
    )
    token_type: str = Field(default="bearer", description="Тип токена (всегда bearer)")
    requires_verification: bool = Field(
        default=True, description="Требуется ли верификация email для полного доступа"
    )


class VerificationDataSchema(BaseCommonResponseSchema):
    id: int
    email: EmailStr = Field(
        description="Верифицированный email адрес", example="john@example.com"
    )
    verified_at: datetime = Field(
        description="Время подтверждения email в формате UTC",
        example="2024-01-15T10:35:00Z",
    )
    access_token: Optional[str] = Field(
        default=None,
        description="Новый полный JWT токен доступа (без ограничений). "
        "Будет None если используются cookies (use_cookies=true)",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...", None],
    )
    refresh_token: Optional[str] = Field(
        default=None,
        description="Новый JWT токен для обновления access токена. "
        "Будет None если используются cookies (use_cookies=true)",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...", None],
    )
    token_type: str = Field(default="bearer", description="Тип токена (всегда bearer)")


class ResendVerificationDataSchema(BaseCommonResponseSchema):
    email: EmailStr = Field(
        description="Email адрес для повторной отправки", example="john@example.com"
    )
    sent_at: datetime = Field(
        description="Время отправки письма в формате UTC",
        example="2024-01-15T10:40:00Z",
    )
    expires_in: int = Field(
        description="Время действия токена верификации в секундах", example=3600
    )


class VerificationStatusDataSchema(BaseCommonResponseSchema):
    email: EmailStr = Field(
        description="Проверяемый email адрес", example="john@example.com"
    )
    is_verified: bool = Field(description="Статус верификации email", example=True)
    checked_at: datetime = Field(
        description="Время проверки статуса в UTC", example="2024-01-15T10:45:00Z"
    )
