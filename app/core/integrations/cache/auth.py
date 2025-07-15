import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from redis import Redis

from app.core.exceptions import ForbiddenError, TokenInvalidError
from app.core.security.token import TokenManager
from app.core.settings import settings
from app.schemas import UserCredentialsSchema

from .base import BaseRedisDataManager

logger = logging.getLogger(__name__)


class AuthRedisDataManager(BaseRedisDataManager):
    def __init__(self, redis: Redis):
        super().__init__(redis)

    async def save_token(self, user: UserCredentialsSchema, token: str) -> None:
        user_data = self._prepare_user_data(user)

        await self.set(
            key=f"token:{token}",
            value=json.dumps(user_data),
            expires=TokenManager.get_token_expiration(),
        )
        await self.sadd(f"sessions:{user.email}", token)
        await self.set_online_status(user.id, True)
        await self.update_last_activity(token)

    async def get_user_by_token(self, token: str) -> Optional[UserCredentialsSchema]:
        user_data = await self.get(f"token:{token}")
        return (
            UserCredentialsSchema.model_validate_json(user_data) if user_data else None
        )

    async def remove_token(self, token: str) -> None:
        user_data = await self.get(f"token:{token}")
        if user_data:
            user = UserCredentialsSchema.model_validate_json(user_data)
            await self.srem(f"sessions:{user.email}", token)
        await self.delete(f"token:{token}")

    @staticmethod
    def _prepare_user_data(user: UserCredentialsSchema) -> dict:
        user_data = user.to_dict()
        for key, value in user_data.items():
            if isinstance(value, datetime):
                user_data[key] = value.isoformat()
            elif isinstance(value, uuid.UUID):
                user_data[key] = str(value)
        return user_data

    async def get_user_from_redis(
        self, token: str, email: str
    ) -> UserCredentialsSchema:
        stored_token = await self.get(f"token:{token}")

        if stored_token:
            user_data = json.loads(stored_token)
            return UserCredentialsSchema.model_validate(user_data)

        return UserCredentialsSchema(email=email)

    async def verify_and_get_user(self, token: str) -> UserCredentialsSchema:
        logger.debug("Начало верификации токена: %s", token)

        if not token:
            logger.debug("Токен отсутствует")
            raise TokenInvalidError()
        try:
            payload = TokenManager.verify_token(token)
            logger.debug("Получен payload: %s", payload)

            email = TokenManager.validate_payload(payload)
            logger.debug("Получен email: %s", email)

            user = await self.get_user_from_redis(token, email)
            logger.debug("Получен пользователь: %s", user)
            logger.debug("Проверка активации пользователя: %s", user.is_active)

            if not user.is_active:
                raise ForbiddenError(
                    detail="Аккаунт деактивирован", extra={"user_id": user.id}
                )

            return user

        except Exception as e:
            logger.debug("Ошибка при верификации: %s", str(e))
            raise

    async def get_all_tokens(self) -> list[str]:
        keys = await self.keys("token:*")

        tokens = [key.decode().split(":")[-1] for key in keys]

        return tokens

    async def update_last_activity(self, token: str) -> None:
        await self.set(
            f"last_activity:{token}", str(int(datetime.now(timezone.utc).timestamp()))
        )

    async def get_last_activity(self, token: str) -> Optional[int]:
        timestamp = await self.get(f"last_activity:{token}")
        return int(timestamp) if timestamp else 0

    async def set_online_status(self, user_id: int, is_online: bool) -> None:
        await self.set(
            key=f"online:{str(user_id)}",
            value=str(is_online),
            expires=settings.USER_INACTIVE_TIMEOUT if is_online else None,
        )

    async def get_online_status(self, user_id: int) -> bool:
        status = await self.get(f"online:{str(user_id)}")

        if status is None:
            return False

        if isinstance(status, bytes):
            return status.decode("utf-8") == "True"
        else:
            return status == "True"

    async def get_user_sessions(self, email: str) -> list[str]:
        return await self.smembers(f"sessions:{email}")

    async def save_refresh_token(self, user_id: int, token: str) -> None:
        key = f"user:{str(user_id)}:refresh_tokens"
        await self.sadd(key, token)
        from app.core.settings import settings

        await self.set_expire(key, settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60)

    async def check_refresh_token(self, user_id: int, token: str) -> bool:
        key = f"user:{str(user_id)}:refresh_tokens"
        result = await self.sismember(key, token)
        return bool(result)

    async def remove_refresh_token(self, user_id: int, token: str) -> None:
        key = f"user:{str(user_id)}:refresh_tokens"
        await self.srem(key, token)

    async def remove_all_refresh_tokens(self, user_id: int) -> None:
        key = f"user:{str(user_id)}:refresh_tokens"
        await self.delete(key)
