from datetime import datetime, timezone
from typing import Optional

from fastapi import Response
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import TokenExpiredError, TokenInvalidError, UserNotFoundError
from app.core.integrations.cache.auth import AuthRedisDataManager
from app.core.integrations.mail import AuthEmailDataManager
from app.core.security.cookies import CookieManager
from app.core.security.token import TokenManager
from app.core.settings import settings
from app.models import User
from app.schemas import (
    RegistrationDataSchema,
    RegistrationRequestSchema,
    RegistrationResponseSchema,
    ResendVerificationDataSchema,
    ResendVerificationResponseSchema,
    UserCredentialsSchema,
    VerificationDataSchema,
    VerificationResponseSchema,
    VerificationStatusDataSchema,
    VerificationStatusResponseSchema,
)
from app.services.v1.base import BaseService

from .data_manager import RegisterDataManager


class RegisterService(BaseService):
    def __init__(self, session: AsyncSession, redis: Optional[Redis] = None):
        super().__init__(session)
        self.data_manager = RegisterDataManager(session)
        self.email_data_manager = AuthEmailDataManager()
        self.redis_data_manager = AuthRedisDataManager(redis) if redis else None

    async def create_user(
        self,
        user_data: RegistrationRequestSchema,
        response: Optional[Response] = None,
        use_cookies: bool = False,
    ) -> RegistrationResponseSchema:
        await self.data_manager.validate_user_uniqueness(email=user_data.email)

        created_user = await self.data_manager.create_user_from_registration(user_data)

        user_schema = UserCredentialsSchema.model_validate(created_user)

        access_token = TokenManager.create_limited_token(user_schema)
        refresh_token = TokenManager.create_refresh_token(created_user.id)

        await self._save_tokens_to_redis(user_schema, access_token, refresh_token)

        if response and use_cookies:
            CookieManager.set_auth_cookies(response, access_token, refresh_token)
            self.logger.debug("Установлены куки с ограниченными токенами")

        await self._send_verification_email(created_user)

        registration_data = RegistrationDataSchema(
            id=created_user.id,
            username=created_user.username,
            first_name=created_user.first_name,
            last_name=created_user.last_name,
            email=created_user.email,
            is_verified=created_user.is_verified,
            is_teacher=created_user.is_teacher,
            created_at=created_user.created_at,
            access_token=None if use_cookies else access_token,
            refresh_token=None if use_cookies else refresh_token,
            token_type=settings.TOKEN_TYPE,
            requires_verification=True,
        )

        self.logger.info(
            "Пользователь зарегистрирован с ограниченными токенами: ID=%s",
            created_user.id,
        )

        return RegistrationResponseSchema(
            message="Регистрация завершена. Подтвердите email для полного доступа.",
            data=registration_data,
        )

    async def _save_tokens_to_redis(
        self, user_schema: UserCredentialsSchema, access_token: str, refresh_token: str
    ) -> None:
        if not self.redis_data_manager:
            return

        try:
            await self.redis_data_manager.save_token(user_schema, access_token)

            await self.redis_data_manager.save_refresh_token(
                user_schema.id, refresh_token
            )

            self.logger.info(
                "Токены сохранены в Redis", extra={"user_id": user_schema.id}
            )
        except Exception as e:
            self.logger.warning(
                "Ошибка сохранения токенов в Redis: %s",
                e,
                extra={"user_id": user_schema.id},
            )

    async def verify_email(
        self, token: str, response: Optional[Response] = None, use_cookies: bool = False
    ) -> VerificationResponseSchema:
        self.logger.info("Попытка верификации email по токену")

        try:
            payload = TokenManager.verify_token(token)
            user_id = TokenManager.validate_verification_token(payload)

            user = await self.data_manager.get_item_by_field("id", user_id)
            if not user:
                self.logger.warning(
                    "Пользователь не найден", extra={"user_id": str(user_id)}
                )
                raise UserNotFoundError(field="id", value=user_id)

            if user.is_verified:
                user_schema = UserCredentialsSchema.model_validate(user)
                access_token = TokenManager.create_full_token(user_schema)
                refresh_token = TokenManager.create_refresh_token(user_schema.id)

                await self._save_tokens_to_redis(
                    user_schema, access_token, refresh_token
                )

                if response and use_cookies:
                    CookieManager.set_auth_cookies(
                        response, access_token, refresh_token
                    )

                verification_data = VerificationDataSchema(
                    id=user_id,
                    email=user_schema.email,
                    verified_at=datetime.now(timezone.utc),
                    access_token=access_token,
                    refresh_token=refresh_token,
                    token_type=settings.TOKEN_TYPE,
                )

                return VerificationResponseSchema(
                    message="Email уже был подтвержден ранее", data=verification_data
                )

            await self.data_manager.update_items(user_id, {"is_verified": True})

            updated_user = await self.data_manager.get_item_by_field("id", user_id)
            user_schema = UserCredentialsSchema.model_validate(updated_user)

            new_access_token = TokenManager.create_full_token(user_schema)
            new_refresh_token = TokenManager.create_refresh_token(user_id)

            await self._save_tokens_to_redis(
                user_schema, new_access_token, new_refresh_token
            )

            if response and use_cookies:
                CookieManager.set_auth_cookies(
                    response, new_access_token, new_refresh_token
                )
                self.logger.debug("Обновлены куки с полными токенами")

            await self._send_registration_success_email(user)

            self.logger.info(
                "Email верифицирован, выданы полные токены",
                extra={"user_id": str(user_id)},
            )

            verification_data = VerificationDataSchema(
                id=user_id,
                email=user.email,
                verified_at=datetime.now(timezone.utc),
                access_token=new_access_token,
                refresh_token=new_refresh_token,
                token_type=settings.TOKEN_TYPE,
            )

            return VerificationResponseSchema(
                message="Email успешно подтвержден. Теперь вы можете войти в систему",
                data=verification_data,
            )
        except (TokenExpiredError, TokenInvalidError) as e:
            self.logger.error("Ошибка верификации токена: %s", e)
            raise

    async def resend_verification_email(self, email: str) -> dict:
        user_model = await self.data_manager.get_user_by_identifier(email)
        if not user_model:
            raise UserNotFoundError(field="email", value=email)

        if user_model.is_verified:
            verification_data = VerificationDataSchema(
                id=user_model.id,
                verified_at=user_model.updated_at or user_model.created_at,
                email=user_model.email,
            )
            return VerificationResponseSchema(
                message="Email уже подтвержден", data=verification_data
            )

        await self._send_verification_email(user_model)

        resend_data = ResendVerificationDataSchema(
            email=email,
            sent_at=datetime.now(timezone.utc),
            expires_in=settings.VERIFICATION_TOKEN_EXPIRE_MINUTES * 60,
        )

        return ResendVerificationResponseSchema(
            message="Письмо верификации отправлено повторно", data=resend_data
        )

    async def check_verification_status(
        self, email: str
    ) -> VerificationStatusResponseSchema:
        user = await self.data_manager.get_item_by_field("email", email)
        if not user:
            self.logger.error("Пользователь с email '%s' не найден", email)
            raise UserNotFoundError(field="email", value=email)

        status_data = VerificationStatusDataSchema(
            email=email,
            is_verified=user.is_verified,
            checked_at=datetime.now(timezone.utc),
        )

        return VerificationStatusResponseSchema(
            message="Email подтвержден" if user.is_verified else "Email не подтвержден",
            data=status_data,
        )

    def _validate_verification_token(self, token: str) -> int:
        try:
            payload = TokenManager.verify_token(token)
            return TokenManager.validate_verification_token(payload)
        except Exception as e:
            self.logger.error("Ошибка валидации токена верификации: %s", e)
            raise

    async def _send_verification_email(self, user: User) -> None:
        try:
            verification_token = TokenManager.generate_verification_token(user.id)
            await self.email_data_manager.send_verification_email(
                to_email=user.email,
                verification_token=verification_token,
            )
            self.logger.info(
                "Письмо верификации отправлено",
                extra={"user_id": user.id, "email": user.email},
            )
        except Exception as e:
            self.logger.error(
                "Ошибка при отправке письма верификации: %s",
                e,
                extra={"user_id": user.id, "email": user.email},
            )

    async def _send_registration_success_email(self, user_schema) -> None:
        try:
            await self.email_data_manager.send_registration_success_email(
                to_email=user_schema.email, user_name=user_schema.username
            )
            self.logger.info(
                "Письмо об успешной регистрации отправлено",
                extra={"user_id": user_schema.id, "email": user_schema.email},
            )
        except Exception as e:
            self.logger.error(
                "Ошибка отправки письма об успешной регистрации: %s",
                e,
                extra={"user_id": user_schema.id, "email": user_schema.email},
            )
