import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import Header
from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError

from app.core.exceptions import (
    InvalidCredentialsError,
    TokenExpiredError,
    TokenInvalidError,
    TokenMissingError,
)
from app.core.settings import settings

logger = logging.getLogger(__name__)


class TokenManager:
    @staticmethod
    def generate_token(payload: dict) -> str:
        return jwt.encode(
            payload,
            key=settings.TOKEN_SECRET_KEY.get_secret_value(),
            algorithm=settings.TOKEN_ALGORITHM,
        )

    @staticmethod
    def decode_token(token: str) -> dict:
        try:
            return jwt.decode(
                token,
                key=settings.TOKEN_SECRET_KEY.get_secret_value(),
                algorithms=[settings.TOKEN_ALGORITHM],
            )
        except ExpiredSignatureError as error:
            raise TokenExpiredError() from error
        except JWTError as error:
            raise TokenInvalidError() from error

    @staticmethod
    def verify_token(token: str) -> dict:
        if not token:
            raise TokenMissingError()
        return TokenManager.decode_token(token)

    @staticmethod
    def is_expired(expires_at: int) -> bool:
        current_timestamp = int(datetime.now(timezone.utc).timestamp())
        return current_timestamp > expires_at

    @staticmethod
    def validate_token_payload(
        payload: dict, expected_type: Optional[str] = None
    ) -> dict:
        if expected_type:
            token_type = payload.get("type")
            if token_type != expected_type:
                logger.warning(
                    "Неверный тип токена",
                    extra={"expected": expected_type, "actual": token_type},
                )
                raise TokenInvalidError(f"Ожидался тип токена: {expected_type}")

        expires_at = payload.get("expires_at")
        if TokenManager.is_expired(expires_at):
            logger.warning("Токен истек", extra={"expires_at": expires_at})
            raise TokenExpiredError()

        return payload

    @staticmethod
    def create_payload(user: Any) -> dict:
        expires_at = (
            int(datetime.now(timezone.utc).timestamp())
            + TokenManager.get_token_expiration()
        )
        return {
            "sub": user.email,
            "expires_at": expires_at,
            "user_id": str(user.id),
            "is_verified": user.is_verified,
        }

    @staticmethod
    def get_token_expiration() -> int:
        return settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60

    @staticmethod
    def validate_payload(payload: dict) -> str:
        TokenManager.validate_token_payload(payload)

        email = payload.get("sub")
        if not email:
            raise InvalidCredentialsError()

        return email

    @staticmethod
    def create_refresh_payload(user_id: int) -> dict:
        expires_at = (
            int(datetime.now(timezone.utc).timestamp())
            + settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        )
        return {
            "sub": str(user_id),
            "expires_at": expires_at,
            "type": "refresh",
            "iat": int(time.time()),
            "jti": str(uuid.uuid4()),
        }

    @staticmethod
    def validate_refresh_token(payload: dict) -> uuid.UUID:
        TokenManager.validate_token_payload(payload, "refresh")

        user_id = payload.get("sub")
        if not user_id:
            raise TokenInvalidError("Отсутствует user_id в refresh токене")

        return uuid.UUID(user_id)

    @staticmethod
    def generate_verification_token(user_id: int) -> str:
        from app.core.settings import settings

        expires_at = int(datetime.now(timezone.utc).timestamp()) + (
            settings.VERIFICATION_TOKEN_EXPIRE_MINUTES * 60
        )
        payload = {
            "sub": str(user_id),
            "type": "email_verification",
            "expires_at": expires_at,
        }
        return TokenManager.generate_token(payload)

    @staticmethod
    def validate_verification_token(payload: dict) -> int:
        TokenManager.validate_token_payload(payload, "email_verification")

        user_id = payload.get("sub")
        if not user_id:
            raise TokenInvalidError("Отсутствует user_id в токене верификации")

        return user_id

    @staticmethod
    def generate_password_reset_token(user_id: int) -> str:
        payload = {
            "sub": str(user_id),
            "type": "password_reset",
            "expires_at": (
                int(datetime.now(timezone.utc).timestamp())
                + settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES * 60
            ),
        }
        return TokenManager.generate_token(payload)

    @staticmethod
    def validate_password_reset_token(payload: dict) -> int:
        TokenManager.validate_token_payload(payload, "password_reset")

        user_id = payload.get("sub")
        if not user_id:
            raise TokenInvalidError("Отсутствует user_id в токене сброса пароля")

        return user_id

    @staticmethod
    def get_token_from_header(
        authorization: str = Header(
            None, description="Заголовок Authorization с токеном Bearer"
        )
    ) -> str:
        if not authorization:
            raise TokenMissingError()

        scheme, _, token = authorization.partition(" ")

        if scheme.lower() != "bearer":
            raise TokenInvalidError()

        if not token:
            raise TokenMissingError()

        return token

    @staticmethod
    def create_limited_token(user_schema: Any) -> str:
        payload = TokenManager.create_payload(user_schema)
        payload["limited"] = not user_schema.is_verified

        logger.debug(
            "Создан ограниченный токен",
            extra={
                "user_id": user_schema.id,
                "is_verified": user_schema.is_verified,
                "limited": payload["limited"],
            },
        )

        return TokenManager.generate_token(payload)

    @staticmethod
    def create_full_token(user_schema: Any) -> str:
        payload = TokenManager.create_payload(user_schema)
        payload["limited"] = False

        logger.debug(
            "Создан полный токен",
            extra={
                "user_id": user_schema.id,
                "is_verified": user_schema.is_verified,
                "limited": False,
            },
        )

        return TokenManager.generate_token(payload)

    @staticmethod
    def create_refresh_token(user_id: int) -> str:
        payload = TokenManager.create_refresh_payload(user_id)

        logger.debug("Создан refresh токен", extra={"user_id": str(user_id)})

        return TokenManager.generate_token(payload)

    @staticmethod
    def is_token_limited(payload: dict) -> bool:
        return payload.get("limited", False)

    @staticmethod
    def get_user_id_from_payload(payload: dict) -> int:
        user_id = payload.get("user_id")
        if not user_id:
            raise TokenInvalidError("Отсутствует user_id в токене")
        return user_id

    @staticmethod
    def upgrade_token_to_full(user_schema: Any) -> str:
        new_token = TokenManager.create_full_token(user_schema)

        logger.info(
            "Токен обновлен с ограниченного на полный",
            extra={"user_id": user_schema.id},
        )

        return new_token
