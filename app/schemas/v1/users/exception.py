from pydantic import Field

from app.schemas.v1.base import ErrorResponseSchema, ErrorSchema

EXAMPLE_TIMESTAMP = "2025-01-01T00:00:00+03:00"
EXAMPLE_REQUEST_ID = "00000000-0000-0000-0000-000000000000"


class UserNotFoundErrorSchema(ErrorSchema):
    detail: str = "Пользователь не найден"
    error_type: str = "user_not_found"
    status_code: int = 404
    timestamp: str = Field(default=EXAMPLE_TIMESTAMP)
    request_id: str = Field(default=EXAMPLE_REQUEST_ID)


class UserNotFoundResponseSchema(ErrorResponseSchema):
    error: UserNotFoundErrorSchema


class UnauthorizedErrorSchema(ErrorSchema):
    detail: str = "Необходима авторизация"
    error_type: str = "unauthorized"
    status_code: int = 401
    timestamp: str = Field(default=EXAMPLE_TIMESTAMP)
    request_id: str = Field(default=EXAMPLE_REQUEST_ID)


class UnauthorizedResponseSchema(ErrorResponseSchema):
    error: UnauthorizedErrorSchema


class ForbiddenErrorSchema(ErrorSchema):
    detail: str = "Недостаточно прав для выполнения операции"
    error_type: str = "forbidden"
    status_code: int = 403
    timestamp: str = Field(default=EXAMPLE_TIMESTAMP)
    request_id: str = Field(default=EXAMPLE_REQUEST_ID)


class ForbiddenResponseSchema(ErrorResponseSchema):
    error: ForbiddenErrorSchema
