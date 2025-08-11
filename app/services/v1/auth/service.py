from datetime import datetime, timezone
from typing import Optional

from fastapi import Response
from fastapi.security import OAuth2PasswordRequestForm
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    InvalidCredentialsError,
    TokenExpiredError,
    TokenInvalidError,
    UserNotFoundError,
)
from app.core.integrations.cache.auth import AuthRedisDataManager
from app.core.integrations.mail import AuthEmailDataManager
from app.core.security.cookies import CookieManager
from app.core.security.password import PasswordHasher
from app.core.security.token import TokenManager
from app.core.settings import settings
from app.schemas import (
    AuthSchema,
    LogoutDataSchema,
    LogoutResponseSchema,
    PasswordResetConfirmDataSchema,
    PasswordResetConfirmResponseSchema,
    PasswordResetConfirmSchema,
    PasswordResetDataSchema,
    PasswordResetResponseSchema,
    TokenResponseSchema,
    UserCredentialsSchema,
)
from app.services.v1.base import BaseService

from .data_manager import AuthDataManager


class AuthService(BaseService):
    def __init__(self, session: AsyncSession, redis: Optional[Redis] = None):
        super().__init__(session)
        self.data_manager = AuthDataManager(session)
        self.email_data_manager = AuthEmailDataManager()
        self.redis_data_manager = AuthRedisDataManager(redis) if redis else None

    async def authenticate(
        self,
        form_data: OAuth2PasswordRequestForm,
        response: Optional[Response] = None,
        use_cookies: bool = False,
    ) -> TokenResponseSchema:
        credentials = AuthSchema(
            username=form_data.username, password=form_data.password
        )

        identifier = credentials.username

        self.logger.info(
            "Попытка аутентификации",
            extra={
                "identifier": identifier,
                "has_password": bool(credentials.password),
            },
        )

        user_model = await self.data_manager.get_user_by_identifier(identifier)

        self.logger.info(
            "Начало аутентификации",
            extra={"identifier": identifier, "user_found": bool(user_model)},
        )

        if not user_model:
            self.logger.warning(
                "Пользователь не найден", extra={"identifier": identifier}
            )
            raise InvalidCredentialsError()

        if not PasswordHasher.verify(user_model.password, credentials.password):
            self.logger.warning(
                "Неверный пароль",
                extra={"identifier": identifier, "user_id": user_model.id},
            )
            raise InvalidCredentialsError()

        user_schema = UserCredentialsSchema.model_validate(user_model)

        if not user_schema.is_verified:
            self.logger.warning(
                "Вход с неподтвержденным аккаунтом",
                extra={"identifier": identifier, "user_id": user_model.id},
            )

        self.logger.info(
            "Аутентификация успешна",
            extra={
                "user_id": user_schema.id,
                "email": user_schema.email,
            },
        )

        await self.redis_data_manager.set_online_status(user_schema.id, True)
        self.logger.info(
            "Пользователь вошел в систему",
            extra={
                "user_id": user_schema.id,
                "email": user_schema.email,
                "is_online": True,
            },
        )

        await self.data_manager.update_items(
            user_schema.id, {"last_login": datetime.now(timezone.utc)}
        )

        access_token = await self.create_token(user_schema)
        refresh_token = await self.create_refresh_token(user_schema.id)

        if response and use_cookies:
            CookieManager.set_auth_cookies(response, access_token, refresh_token)

            return TokenResponseSchema(
                message="Аутентификация успешна",
                access_token=None,
                refresh_token=None,
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            )

        return TokenResponseSchema(
            message="Аутентификация успешна",
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    async def create_token(self, user_schema: UserCredentialsSchema) -> str:
        if user_schema.is_verified:
            access_token = TokenManager.create_full_token(user_schema)
        else:
            access_token = TokenManager.create_limited_token(user_schema)

        self.logger.debug(
            "Сгенерирован токен", extra={"access_token_length": len(access_token)}
        )

        await self.redis_data_manager.save_token(user_schema, access_token)
        self.logger.info(
            "Токен создан и сохранен в Redis",
            extra={"user_id": user_schema.id, "access_token_length": len(access_token)},
        )

        return access_token

    async def create_refresh_token(self, user_id: int) -> str:
        refresh_token = TokenManager.create_refresh_token(user_id)

        self.logger.debug(
            "Сгенерирован refresh токен",
            extra={"refresh_token_length": len(refresh_token)},
        )

        await self.redis_data_manager.save_refresh_token(user_id, refresh_token)

        self.logger.info(
            "Refresh токен создан и сохранен в Redis",
            extra={"user_id": str(user_id), "refresh_token_length": len(refresh_token)},
        )

        return refresh_token

    async def refresh_token(
        self,
        refresh_token: str,
        response: Optional[Response] = None,
        use_cookies: bool = False,
    ) -> TokenResponseSchema:
        try:
            payload = TokenManager.decode_token(refresh_token)

            user_id = TokenManager.validate_refresh_token(payload)

            if not await self.redis_data_manager.check_refresh_token(
                user_id, refresh_token
            ):
                self.logger.warning(
                    "Попытка использовать неизвестный refresh токен",
                    extra={"user_id": str(user_id)},
                )
                raise TokenInvalidError()

            user_model = await self.data_manager.get_model_by_field("id", user_id)

            if not user_model:
                self.logger.warning(
                    "Пользователь не найден при обновлении токена",
                    extra={"user_id": str(user_id)},
                )
                raise UserNotFoundError(field="id", value=user_id)

            user_schema = UserCredentialsSchema.model_validate(user_model)

            access_token = await self.create_token(user_schema)
            new_refresh_token = await self.create_refresh_token(user_id)

            await self.redis_data_manager.remove_refresh_token(user_id, refresh_token)

            self.logger.info(
                "Токены успешно обновлены",
                extra={"user_id": str(user_id)},
            )

            if response and use_cookies:
                CookieManager.set_auth_cookies(
                    response, access_token, new_refresh_token
                )

                return TokenResponseSchema(
                    message="Токен успешно обновлен",
                    access_token=None,
                    refresh_token=None,
                    expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                )

            return TokenResponseSchema(
                message="Токен успешно обновлен",
                access_token=access_token,
                refresh_token=new_refresh_token,
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            )

        except (TokenExpiredError, TokenInvalidError) as e:
            self.logger.warning(
                "Ошибка при обновлении токена: %s",
                type(e).__name__,
                extra={"error_type": type(e).__name__},
            )
            raise

    async def logout(
        self,
        authorization: Optional[str],
        response: Optional[Response] = None,
        clear_cookies: bool = False,
    ) -> LogoutResponseSchema:
        try:
            token = TokenManager.get_token_from_header(authorization)

            try:
                payload = TokenManager.decode_token(token)

                user_id_str = payload.get("user_id")

                if user_id_str:
                    user_id = int(user_id_str)
                    await self.redis_data_manager.set_online_status(user_id, False)

                    await self.redis_data_manager.remove_all_refresh_tokens(user_id)

                    self.logger.debug(
                        "Пользователь вышел из системы, все токены удалены",
                        extra={"user_id": str(user_id), "is_online": False},
                    )

                    await self.redis_data_manager.update_last_activity(token)

            except (TokenExpiredError, TokenInvalidError) as e:
                self.logger.warning(
                    "Выход с невалидным токеном: %s",
                    type(e).__name__,
                    extra={"token_error": type(e).__name__},
                )

            await self.redis_data_manager.remove_token(token)

            logout_data = LogoutDataSchema(logged_out_at=datetime.now(timezone.utc))

            if response and clear_cookies:
                CookieManager.clear_auth_cookies(response)

            return LogoutResponseSchema(
                message="Выход выполнен успешно", data=logout_data
            )

        except (TokenExpiredError, TokenInvalidError) as e:
            self.logger.warning(
                "Ошибка при выходе: %s",
                type(e).__name__,
                extra={"error_type": type(e).__name__},
            )
            raise

    async def send_password_reset_email(
        self, email: str
    ) -> PasswordResetResponseSchema:
        self.logger.info("Запрос на сброс пароля", extra={"email": email})

        user = await self.data_manager.get_user_by_identifier(email)
        reset_token = TokenManager.generate_password_reset_token(user.id)

        try:
            await self.email_data_manager.send_password_reset_email(
                to_email=user.email, user_name=user.username, reset_token=reset_token
            )

            self.logger.info(
                "Письмо для сброса пароля отправлено",
                extra={"user_id": user.id, "email": user.email},
            )

            reset_data = PasswordResetDataSchema(
                email=email, expires_in=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES
            )

            return PasswordResetResponseSchema(
                message="Инструкции по сбросу пароля отправлены на ваш email",
                data=reset_data,
            )

        except Exception as e:
            self.logger.error(
                "Ошибка при отправке письма сброса пароля: %s",
                e,
                extra={"email": email},
            )
            raise

    async def reset_password(
        self, reset_data: PasswordResetConfirmSchema
    ) -> PasswordResetConfirmResponseSchema:
        self.logger.info("Запрос на установку нового пароля")

        try:
            payload = TokenManager.verify_token(reset_data.token)

            user_id = TokenManager.validate_password_reset_token(payload)

            user = await self.data_manager.get_item_by_field("id", user_id)
            if not user:
                self.logger.warning(
                    "Пользователь не найден", extra={"user_id": str(user_id)}
                )
                raise UserNotFoundError(field="id", value=user_id)

            hashed_password = PasswordHasher.hash_password(reset_data.new_password)

            await self.data_manager.update_items(
                user_id, {"hashed_password": hashed_password}
            )

            self.logger.info("Пароль успешно изменен", extra={"user_id": str(user_id)})

            confirm_data = PasswordResetConfirmDataSchema(
                password_changed_at=datetime.now(timezone.utc)
            )

            return PasswordResetConfirmResponseSchema(
                message="Пароль успешно изменен", data=confirm_data
            )

        except (TokenExpiredError, TokenInvalidError) as e:
            self.logger.error("Ошибка проверки токена сброса пароля: %s", e)
            raise
        except Exception as e:
            self.logger.error("Ошибка при сбросе пароля: %s", e)
            raise
