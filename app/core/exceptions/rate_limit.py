from typing import Any, Dict, Optional

from app.core.exceptions.base import BaseAPIException


class RateLimitExceededError(BaseAPIException):
    def __init__(
        self,
        detail: str = "Слишком много запросов. Пожалуйста, повторите попытку позже.",
        error_type: str = "rate_limit_exceeded",
        reset_time: Optional[int] = None,
        extra: Optional[Dict[str, Any]] = None,
    ):
        _extra = extra or {}
        if reset_time is not None:
            _extra["reset_time"] = reset_time

        super().__init__(
            status_code=429, detail=detail, error_type=error_type, extra=_extra
        )
