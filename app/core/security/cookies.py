import logging
from typing import Optional

from fastapi import Response

from app.core.settings import settings

logger = logging.getLogger(__name__)


class CookieManager:
    ACCESS_TOKEN_KEY = "access_token"
    REFRESH_TOKEN_KEY = "refresh_token"

    @staticmethod
    def set_auth_cookies(
        response: Response, access_token: str, refresh_token: str
    ) -> None:
        CookieManager.set_access_token_cookie(response, access_token)
        CookieManager.set_refresh_token_cookie(response, refresh_token)

        logger.debug(
            "Установлены куки с токенами аутентификации",
            extra={
                "access_token_length": len(access_token),
                "refresh_token_length": len(refresh_token),
            },
        )

    @staticmethod
    def set_access_token_cookie(response: Response, access_token: str) -> None:
        response.set_cookie(
            key=CookieManager.ACCESS_TOKEN_KEY,
            value=access_token,
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            httponly=True,
            secure=settings.COOKIE_SECURE,
            samesite=settings.COOKIE_SAMESITE,
            domain=settings.COOKIE_DOMAIN,
            path="/",
        )

        logger.debug("Установлена кука с access токеном")

    @staticmethod
    def set_refresh_token_cookie(response: Response, refresh_token: str) -> None:
        response.set_cookie(
            key=CookieManager.REFRESH_TOKEN_KEY,
            value=refresh_token,
            max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
            httponly=True,
            secure=settings.COOKIE_SECURE,
            samesite=settings.COOKIE_SAMESITE,
            domain=settings.COOKIE_DOMAIN,
            path="/api/v1/auth/refresh",
        )

        logger.debug("Установлена кука с refresh токеном")

    @staticmethod
    def clear_auth_cookies(response: Response) -> None:
        CookieManager.clear_access_token_cookie(response)
        CookieManager.clear_refresh_token_cookie(response)

        logger.debug("Очищены куки с токенами аутентификации")

    @staticmethod
    def clear_access_token_cookie(response: Response) -> None:
        response.delete_cookie(
            key=CookieManager.ACCESS_TOKEN_KEY,
            path="/",
            domain=settings.COOKIE_DOMAIN,
        )

        logger.debug("Очищена кука с access токеном")

    @staticmethod
    def clear_refresh_token_cookie(response: Response) -> None:
        response.delete_cookie(
            key=CookieManager.REFRESH_TOKEN_KEY,
            path="/api/v1/auth/refresh",
            domain=settings.COOKIE_DOMAIN,
        )

        logger.debug("Очищена кука с refresh токеном")

    @staticmethod
    def set_verification_cookie(
        response: Response, verification_token: str, max_age: Optional[int] = None
    ) -> None:
        if max_age is None:
            max_age = settings.VERIFICATION_TOKEN_EXPIRE_MINUTES * 60

        response.set_cookie(
            key="verification_token",
            value=verification_token,
            max_age=max_age,
            httponly=True,
            secure=settings.COOKIE_SECURE,
            samesite=settings.COOKIE_SAMESITE,
            domain=settings.COOKIE_DOMAIN,
            path="/api/v1/auth/verify",
        )

        logger.debug("Установлена кука с токеном верификации")

    @staticmethod
    def clear_verification_cookie(response: Response) -> None:
        response.delete_cookie(
            key="verification_token",
            path="/api/v1/auth/verify",
            domain=settings.COOKIE_DOMAIN,
        )

        logger.debug("Очищена кука с токеном верификации")

    @staticmethod
    def get_cookie_settings() -> dict:
        return {
            "secure": settings.COOKIE_SECURE,
            "samesite": settings.COOKIE_SAMESITE,
            "domain": settings.COOKIE_DOMAIN,
            "access_token_expire": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "refresh_token_expire": settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        }
