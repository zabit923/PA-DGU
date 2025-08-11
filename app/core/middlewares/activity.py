import logging
from datetime import datetime, timezone

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.connections import RedisClient
from app.core.integrations.cache.auth import AuthRedisDataManager
from app.core.settings import settings

logger = logging.getLogger("app.middleware.activity")


class ActivityMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        logger.info("ActivityMiddleware инициализирован")

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        method = request.method

        extra = {
            "client_ip": request.client.host if request.client else "unknown",
            "path": path,
            "method": method,
        }

        logger.debug("Обработка запроса %s %s", method, path, extra=extra)

        auth_header = request.headers.get("Authorization", "")

        if auth_header.startswith(f"{settings.TOKEN_TYPE} "):
            token = auth_header.split(" ")[1]
            masked_token = token[:5] + "..." + token[-5:] if len(token) > 10 else "***"

            logger.info("Обновление активности по токену %s", masked_token, extra=extra)

            start_time = datetime.now(timezone.utc)

            redis_client = RedisClient()
            redis = await redis_client.connect()

            try:
                auth_storage = AuthRedisDataManager(redis)
                await auth_storage.update_last_activity(token)

                user = await auth_storage.get_user_by_token(token)
                if user and user.id:
                    user_extra = {**extra, "user_id": user.id}
                    logger.info(
                        "Установка статуса 'онлайн' для пользователя id=%s",
                        user.id,
                        extra=user_extra,
                    )
                    await auth_storage.set_online_status(user.id, True)
                else:
                    logger.warning(
                        "Пользователь не найден для токена %s",
                        masked_token,
                        extra=extra,
                    )
            except Exception as e:
                logger.error(
                    "Ошибка при обновлении активности: %s",
                    str(e),
                    exc_info=True,
                    extra=extra,
                )
            finally:
                await redis_client.close()

                duration_ms = (
                    datetime.now(timezone.utc) - start_time
                ).total_seconds() * 1000
                perf_extra = {**extra, "duration_ms": duration_ms}
                logger.debug(
                    "Обновление активности выполнено за %.2f мс",
                    duration_ms,
                    extra=perf_extra,
                )
        else:
            logger.debug("Пропуск обновления активности: токен не найден", extra=extra)

        response = await call_next(request)

        result_extra = {**extra, "status_code": response.status_code}
        logger.debug(
            "Запрос %s %s обработан, статус: %s",
            method,
            path,
            response.status_code,
            extra=result_extra,
        )

        return response
