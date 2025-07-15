from typing import Any, Dict, Optional

from app.core.exceptions.base import BaseAPIException


class AuthenticationError(BaseAPIException):
    def __init__(
        self,
        detail: str = "Ошибка аутентификации",
        error_type: str = "authentication_error",
        status_code: int = 401,
        extra: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status_code,
            detail=detail,
            error_type=error_type,
            extra=extra or {},
        )


class InvalidCredentialsError(AuthenticationError):
    def __init__(self):
        super().__init__(
            detail="🔐 Неверный email или пароль",
            error_type="invalid_credentials",
        )


class InvalidEmailFormatError(AuthenticationError):
    def __init__(self, email: str):
        super().__init__(
            detail=f"Неверный формат email: {email}",
            error_type="invalid_email_format",
            extra={"email": email},
        )


class InvalidPasswordError(AuthenticationError):
    def __init__(self):
        super().__init__(
            detail="Неверный пароль",
            error_type="invalid_password",
        )


class InvalidCurrentPasswordError(AuthenticationError):
    def __init__(self):
        super().__init__(
            detail="Текущий пароль неверен",
            error_type="invalid_current_password",
        )


class WeakPasswordError(AuthenticationError):
    def __init__(
        self,
        detail: str = "Пароль должен быть минимум 8 символов, иметь заглавную и строчную букву, цифру, спецсимвол",
    ):
        super().__init__(
            detail=detail,
            error_type="weak_password",
        )


class TokenError(AuthenticationError):
    def __init__(
        self,
        detail: str,
        error_type: str = "token_error",
        status_code: int = 401,
        extra: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            detail=detail,
            error_type=error_type,
            status_code=status_code,
            extra=extra or {"token": True},
        )


class TokenMissingError(TokenError):
    def __init__(self):
        super().__init__(detail="Токен отсутствует", error_type="token_missing")


class TokenExpiredError(TokenError):
    def __init__(self):
        super().__init__(
            detail="Токен просрочен", error_type="token_expired", status_code=419
        )


class TokenInvalidError(TokenError):
    def __init__(
        self, detail: str = "Невалидный токен", extra: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            detail=detail, error_type="token_invalid", status_code=422, extra=extra
        )
