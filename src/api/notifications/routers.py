from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.notifications.schemas import NotificationRead
from api.notifications.service import NotificationService
from api.users.dependencies import get_current_user
from core.database import get_async_session
from core.database.models import User

router = APIRouter(prefix="/notifications")

notification_service = NotificationService()


@router.get(
    "/get-unread-notifications",
    status_code=status.HTTP_200_OK,
    response_model=List[NotificationRead],
)
async def get_unread_notifications(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    notifications = await notification_service.get_unread_notifications(user, session)
    return notifications


@router.get(
    "/get-all-notifications",
    status_code=status.HTTP_200_OK,
    response_model=List[NotificationRead],
)
async def get_all_notifications(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    notifications = await notification_service.get_all_notifications(user, session)
    return notifications
