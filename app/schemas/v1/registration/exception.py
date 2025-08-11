from pydantic import Field

from app.schemas.v1.base import ErrorResponseSchema, ErrorSchema

EXAMPLE_TIMESTAMP = "2025-01-01T00:00:00+03:00"
EXAMPLE_REQUEST_ID = "00000000-0000-0000-0000-000000000000"


class UserExistsErrorSchema(ErrorSchema):
    detail: str = "Пользователь с таким email уже существует"
    error_type: str = "user_exists"
    status_code: int = 409
    timestamp: str = Field(default=EXAMPLE_TIMESTAMP)
    request_id: str = Field(default=EXAMPLE_REQUEST_ID)


class UserExistsResponseSchema(ErrorResponseSchema):
    error: UserExistsErrorSchema


class UserCreationErrorSchema(ErrorSchema):
    detail: str = "Не удалось создать пользователя. Пожалуйста, попробуйте позже."
    error_type: str = "user_creation_error"
    status_code: int = 500
    timestamp: str = Field(default=EXAMPLE_TIMESTAMP)
    request_id: str = Field(default=EXAMPLE_REQUEST_ID)


class UserCreationResponseSchema(ErrorResponseSchema):
    error: UserCreationErrorSchema


class TokenInvalidErrorSchema(ErrorSchema):
    detail: str = "Невалидный токен"
    error_type: str = "token_invalid"
    status_code: int = 400
    timestamp: str = Field(default=EXAMPLE_TIMESTAMP)
    request_id: str = Field(default=EXAMPLE_REQUEST_ID)


class TokenInvalidResponseSchema(ErrorResponseSchema):
    error: TokenInvalidErrorSchema


class TokenExpiredErrorSchema(ErrorSchema):
    detail: str = "Токен просрочен"
    error_type: str = "token_expired"
    status_code: int = 419
    timestamp: str = Field(default=EXAMPLE_TIMESTAMP)
    request_id: str = Field(default=EXAMPLE_REQUEST_ID)


class TokenExpiredResponseSchema(ErrorResponseSchema):
    error: TokenExpiredErrorSchema
