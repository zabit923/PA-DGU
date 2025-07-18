from core.dependencies import get_db_session
from core.security.auth import get_current_user
from fastapi import Depends, Query
from models import User
from routes.base import BaseRouter
from schemas import NotificationListResponseSchema, Page, PaginationParams
from services.v1.notifications.service import NotificationService
from starlette import status


class NotificationRouter(BaseRouter):
    def __init__(self):
        super().__init__(prefix="notifications", tags=["Notifications"])

    def configure(self):
        @self.router.get(
            "/get-unread-notifications",
            status_code=status.HTTP_200_OK,
            response_model=NotificationListResponseSchema,
        )
        async def get_unread_notifications(
            skip: int = Query(0, ge=0, description="Количество пропускаемых элементов"),
            limit: int = Query(
                10, ge=1, le=100, description="Количество элементов на странице"
            ),
            user: User = Depends(get_current_user),
            session: Depends = Depends(get_db_session),
        ):
            """
            ### Args:
            * **skip**: Количество пропускаемых элементов
            * **limit**: Количество элементов на странице (от 1 до 100)
            """
            pagination = PaginationParams(skip=skip, limit=limit)
            notifications, total = await NotificationService(
                session
            ).get_unread_notifications(user, pagination)
            page = Page(
                items=notifications,
                total=total,
                page=pagination.page,
                size=pagination.limit,
            )
            return NotificationListResponseSchema(data=page)

        @self.router.get(
            "/get-all-notifications",
            status_code=status.HTTP_200_OK,
            response_model=NotificationListResponseSchema,
        )
        async def get_all_notifications(
            skip: int = Query(0, ge=0, description="Количество пропускаемых элементов"),
            limit: int = Query(
                10, ge=1, le=100, description="Количество элементов на странице"
            ),
            user: User = Depends(get_current_user),
            session: Depends = Depends(get_db_session),
        ):
            """
            ### Args:
            * **skip**: Количество пропускаемых элементов
            * **limit**: Количество элементов на странице (от 1 до 100)
            """
            pagination = PaginationParams(skip=skip, limit=limit)
            notifications, total = await NotificationService(
                session
            ).get_all_notifications(user, pagination)
            page = Page(
                items=notifications,
                total=total,
                page=pagination.page,
                size=pagination.limit,
            )
            return NotificationListResponseSchema(data=page)
