from pydantic import EmailStr, Field, field_validator

from app.core.security.password import BasePasswordValidator
from app.schemas.v1.base import BaseRequestSchema


class RegistrationRequestSchema(BaseRequestSchema):
    username: str = Field(
        min_length=3,
        max_length=30,
        description="Имя пользователя. Должно содержать от 3 до 30 символов",
        examples=["user123", "john_doe"],
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

    password: str = Field(
        min_length=8,
        description=(
            "Пароль пользователя. Требования: "
            "минимум 8 символов, заглавная и строчная буквы, "
            "цифра, специальный символ"
        ),
        examples=["SecurePass123!", "MyP@ssw0rd"],
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, v, info):
        username = info.data.get("username") if info.data else None
        return BasePasswordValidator.validate_password_strength(v, username)


class ResendVerificationRequestSchema(BaseRequestSchema):
    email: EmailStr = Field(description="Email пользователя")
