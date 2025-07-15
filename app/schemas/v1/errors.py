from typing import Optional

from .base import ErrorResponseSchema, ErrorSchema


class RateLimitErrorSchema(ErrorSchema):
    reset_time: Optional[int] = None


class RateLimitExceededResponseSchema(ErrorResponseSchema):
    error: RateLimitErrorSchema
