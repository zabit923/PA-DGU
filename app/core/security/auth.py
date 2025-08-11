import logging

from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db_session
from app.core.exceptions import (
    InvalidCredentialsError,
    TokenError,
    TokenInvalidError,
    TokenMissingError,
)
from app.core.security.token import TokenManager
from app.core.settings import settings
from app.schemas import UserReadSchema
from app.services.v1.users.data_manager import UserDataManager

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=settings.AUTH_URL,
    scheme_name="OAuth2PasswordBearer",
    description="Bearer token",
    auto_error=False,
)


class AuthenticationManager:
    @staticmethod
    async def get_current_user(
        request: Request,
        token: str = Depends(oauth2_scheme),
        session: AsyncSession = Depends(get_db_session),
    ) -> UserReadSchema:
        logger.debug(
            "Обработка запроса аутентификации с заголовками: %s", request.headers
        )
        logger.debug("Начало получения данных пользователя")
        logger.debug("Получен токен: %s", token)

        if not token:
            logger.debug("Токен отсутствует в запросе")
            raise TokenMissingError()

        try:
            payload = TokenManager.verify_token(token)
            user_email = TokenManager.validate_payload(payload)

            user_manager = UserDataManager(session)
            user = await user_manager.get_user_by_identifier(user_email)

            if not user:
                logger.debug("Пользователь с email %s не найден", user_email)
                raise InvalidCredentialsError()

            logger.debug("Пользователь успешно аутентифицирован: %s", user)

            return user

        except TokenError:
            raise
        except Exception as e:
            logger.debug("Ошибка при аутентификации: %s", str(e))
            raise TokenInvalidError() from e


async def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_db_session),
) -> UserReadSchema:
    return await AuthenticationManager.get_current_user(request, token, session)


async def get_current_user_optional(
    request: Request,
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_db_session),
) -> UserReadSchema | None:
    try:
        return await AuthenticationManager.get_current_user(request, token, session)
    except (TokenError, InvalidCredentialsError):
        return None
