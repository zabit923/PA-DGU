from typing import Any, Dict, Optional

from app.core.exceptions.base import BaseAPIException


class ForbiddenError(BaseAPIException):
    def __init__(
        self,
        detail: str = "Недостаточно прав для выполнения операции",
        required_role: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
    ):
        extra: Optional[Dict[str, Any]] = (
            {"required_role": required_role} if required_role else None
        )
        super().__init__(
            status_code=403, detail=detail, error_type="forbidden", extra=extra
        )


class UserNotFoundError(BaseAPIException):
    def __init__(
        self,
        field: Optional[str] = None,
        value: Any = None,
        detail: Optional[str] = None,
    ):
        message = detail or "Пользователь не найден"
        if field and value is not None:
            message = f"Пользователь с {field}={value} не найден"

        super().__init__(
            status_code=404,
            detail=message,
            error_type="user_not_found",
            extra={"field": field, "value": value} if field else None,
        )


class UserExistsError(BaseAPIException):
    def __init__(self, field: str, value: Any):
        super().__init__(
            status_code=409,
            detail=f"Пользователь с {field}={value} уже существует",
            error_type="user_exists",
            extra={"field": field, "value": value},
        )


class UserCreationError(BaseAPIException):
    def __init__(
        self,
        detail: str = "Не удалось создать пользователя. Пожалуйста, попробуйте позже.",
        extra: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=500,
            detail=detail,
            error_type="user_creation_error",
            extra=extra or {},
        )
