from typing import Optional

from core.integrations.storage import CommonS3DataManager, get_common_s3_manager
from fastapi import Depends, File, Form, Query, UploadFile
from models import User
from redis import Redis
from schemas import UserUpdateResponseSchema, UserUpdateSchema
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.core.dependencies import get_db_session, get_redis_client
from app.core.security.auth import get_current_user
from app.routes.base import BaseRouter
from app.schemas import (
    ForbiddenResponseSchema,
    Page,
    PaginationParams,
    TokenMissingResponseSchema,
    UserListResponseSchema,
    UserReadSchema,
    UserSortFields,
)
from app.services.v1.users.service import UserService


class UserRouter(BaseRouter):
    def __init__(self):
        """
        Инициализирует роутер пользователей.
        """
        super().__init__(prefix="users", tags=["Users"])

    def configure(self):
        @self.router.get(
            path="",
            response_model=UserListResponseSchema,
            responses={
                401: {
                    "model": TokenMissingResponseSchema,
                    "description": "Токен отсутствует",
                },
                403: {
                    "model": ForbiddenResponseSchema,
                    "description": "Недостаточно прав для выполнения операции",
                },
            },
        )
        async def get_users(
            skip: int = Query(0, ge=0, description="Количество пропускаемых элементов"),
            limit: int = Query(
                10, ge=1, le=100, description="Количество элементов на странице"
            ),
            sort_by: Optional[str] = Query(
                UserSortFields.get_default().field,
                description=(
                    "Поле для сортировки пользователей. "
                    f"Доступные значения: {', '.join(UserSortFields.get_field_values())}. "
                    f"По умолчанию: {UserSortFields.get_default().field} "
                    f"({UserSortFields.get_default().description})."
                ),
                enum=UserSortFields.get_field_values(),
            ),
            sort_desc: bool = Query(True, description="Сортировка по убыванию"),
            search: Optional[str] = Query(
                None, description="Поиск по данным пользователя"
            ),
            session: AsyncSession = Depends(get_db_session),
            redis: Optional[Redis] = Depends(get_redis_client),
            current_user: User = Depends(get_current_user),
        ) -> UserListResponseSchema:
            pagination = PaginationParams(
                skip=skip, limit=limit, sort_by=sort_by, sort_desc=sort_desc
            )

            users, total = await UserService(session, redis).get_users(
                pagination=pagination,
                search=search,
                current_user=current_user,
            )
            page = Page(
                items=users, total=total, page=pagination.page, size=pagination.limit
            )
            return UserListResponseSchema(data=page)

        @self.router.patch(
            path="",
            response_model=UserUpdateResponseSchema,
            status_code=status.HTTP_200_OK,
            summary="Обновление пользователя",
        )
        async def update_user(
            user: User = Depends(get_current_user),
            username: Optional[str] = Form(None),
            first_name: Optional[str] = Form(None),
            last_name: Optional[int] = Form(None),
            email: Optional[str] = Form(None),
            image: Optional[UploadFile] = File(None),
            session: AsyncSession = Depends(get_db_session),
            s3_data_manager: CommonS3DataManager = Depends(get_common_s3_manager),
        ) -> UserUpdateResponseSchema:
            user_data = UserUpdateSchema(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
            )
            return await UserService(
                session, s3_data_manager=s3_data_manager
            ).update_user(user, user_data, image)

        @self.router.get(
            path="/get-me",
            status_code=status.HTTP_200_OK,
            response_model=UserReadSchema,
        )
        async def get_me(user: User = Depends(get_current_user)) -> UserReadSchema:
            return user

        @self.router.get(
            "/change-online-status",
            status_code=status.HTTP_200_OK,
            response_model=UserReadSchema,
        )
        async def change_user_status(
            user: User = Depends(get_current_user),
            session: AsyncSession = Depends(get_db_session),
        ):
            return await UserService(session).change_online_status(user)

        @self.router.get(
            "/change-ignore-status",
            status_code=status.HTTP_200_OK,
            response_model=UserReadSchema,
        )
        async def set_user_ignore(
            user: User = Depends(get_current_user),
            session: AsyncSession = Depends(get_db_session),
        ):
            return await UserService(session).change_ignore_status(user)
