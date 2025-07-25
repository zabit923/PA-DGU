from typing import Any, Optional

from core.exceptions import BaseAPIException


class CategoryNotFoundError(BaseAPIException):
    def __init__(
        self,
        field: Optional[str] = None,
        value: Any = None,
        detail: Optional[str] = None,
    ):
        message = detail or "Категория не найдена"
        if field and value is not None:
            message = f"Категория с {field}={value} не найдена"

        super().__init__(
            status_code=404,
            detail=message,
            error_type="category_not_found",
            extra={"field": field, "value": value} if field else None,
        )
