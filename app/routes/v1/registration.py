from typing import Optional

from fastapi import Depends, Query, Response
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db_session, get_redis_client
from app.routes.base import BaseRouter
from app.schemas import (
    RegistrationRequestSchema,
    RegistrationResponseSchema,
    UserCreationResponseSchema,
    UserExistsResponseSchema,
)
from app.services.v1.registration.service import RegisterService


class RegisterRouter(BaseRouter):
    def __init__(self):
        super().__init__(prefix="register", tags=["Registration"])

    def configure(self):
        @self.router.post(
            path="",
            response_model=RegistrationResponseSchema,
            summary="Регистрация нового пользователя",
            responses={
                201: {
                    "model": RegistrationResponseSchema,
                    "description": "Пользователь успешно зарегистрирован",
                },
                409: {
                    "model": UserExistsResponseSchema,
                    "description": "Пользователь с таким email/username/телефоном уже существует",
                },
                500: {
                    "model": UserCreationResponseSchema,
                    "description": "Ошибка при создании пользователя",
                },
            },
        )
        async def registration_user(
            new_user: RegistrationRequestSchema,
            response: Response,
            use_cookies: bool = Query(
                False, description="Использовать куки для хранения токенов"
            ),
            session: AsyncSession = Depends(get_db_session),
            redis: Optional[Redis] = Depends(get_redis_client),
        ) -> RegistrationResponseSchema:
            """
            ## 📝 Регистрация нового пользователя

            Регистрирует нового пользователя в системе и отправляет письмо для подтверждения email.
            После успешной регистрации пользователь получит письмо с ссылкой для активации аккаунта.

            ### Параметры:
            * **username**: Уникальное имя пользователя (3-50 символов)
            * **email**: Email адрес пользователя (должен быть уникальным)
            * **password**: Пароль (минимум 8 символов, должен содержать буквы и цифры)
            * **phone**: Номер телефона в формате +7 (XXX) XXX-XX-XX (опционально)
            * **use_cookies**: Использовать куки для хранения токенов (по умолчанию false)

            ### Returns:
            * **success**: Статус успешной регистрации (true)
            * **message**: Сообщение о результате регистрации
            * **data**: Информация о созданном пользователе и токены доступа

            ### Процесс регистрации:
            1. Валидация входных данных
            2. Проверка уникальности email, username и телефона
            3. Создание пользователя в базе данных
            4. Генерация ограниченных токенов доступа
            5. Отправка письма с ссылкой подтверждения
            6. Опциональная установка куков с токенами

            ### Примечания:
            * Пользователь создается с is_verified=false
            * Выдаются ограниченные токены до подтверждения email
            * Письмо верификации действительно 24 часа
            * При use_cookies=true токены сохраняются в HttpOnly куки
            """
            return await RegisterService(session, redis).create_user(
                new_user, response, use_cookies
            )
