from typing import Any, Optional

from core.exceptions import BaseAPIException


class NewsNotFoundError(BaseAPIException):
    def __init__(
        self,
        field: Optional[str] = None,
        value: Any = None,
        detail: Optional[str] = None,
    ):
        message = detail or "Новость не найдена"
        if field and value is not None:
            message = f"Новость с {field}={value} не найдена"

        super().__init__(
            status_code=404,
            detail=message,
            error_type="news_not_found",
            extra={"field": field, "value": value} if field else None,
        )
