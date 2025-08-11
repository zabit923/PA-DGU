import logging
import re

import passlib
from passlib.context import CryptContext
from pydantic import BaseModel

from app.core.exceptions import WeakPasswordError

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    argon2__time_cost=2,
    argon2__memory_cost=102400,
    argon2__parallelism=8,
)

logger = logging.getLogger(__name__)


class BasePasswordValidator(BaseModel):
    @staticmethod
    def validate_password_strength(password: str, username: str = None) -> str:
        errors = []

        if len(password) < 8:
            errors.append("Пароль должен содержать минимум 8 символов")

        if not re.search(r"[A-ZА-Я]", password):
            errors.append("Пароль должен содержать хотя бы одну заглавную букву")

        if not re.search(r"[a-zа-я]", password):
            errors.append("Пароль должен содержать хотя бы одну строчную букву")

        if not re.search(r"\d", password):
            errors.append("Пароль должен содержать хотя бы одну цифру")

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Пароль должен содержать хотя бы один специальный символ")

        common_sequences = [
            "12345",
            "qwerty",
            "password",
            "admin",
            "123456789",
            "abc123",
        ]
        if any(seq in password.lower() for seq in common_sequences):
            errors.append(
                "Пароль не должен содержать распространенные последовательности"
            )

        if username and len(username) > 3:
            if username.lower() in password.lower():
                errors.append("Пароль не должен содержать имя пользователя")

        if errors:
            raise WeakPasswordError("; ".join(errors))

        return password


class PasswordHasher:
    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify(hashed_password: str, plain_password: str) -> bool:
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except passlib.exc.UnknownHashError:
            logger.warning("Неизвестный формат хеша пароля")
            return False
