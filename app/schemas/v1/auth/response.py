from app.schemas.v1.base import BaseResponseSchema

from .base import (
    LogoutDataSchema,
    PasswordResetConfirmDataSchema,
    PasswordResetDataSchema,
    TokenDataSchema,
)


class TokenResponseSchema(BaseResponseSchema):
    access_token: None | str
    refresh_token: None | str
    token_type: str = "Bearer"
    expires_in: int
    message: str = "Авторизация успешна"


class LogoutResponseSchema(BaseResponseSchema):
    data: LogoutDataSchema


class PasswordResetResponseSchema(BaseResponseSchema):
    data: PasswordResetDataSchema


class PasswordResetConfirmResponseSchema(BaseResponseSchema):
    data: PasswordResetConfirmDataSchema


class OAuth2TokenResponseSchema(BaseResponseSchema):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int
    data: TokenDataSchema
