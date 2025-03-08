from typing import List

from fastapi import APIRouter, Depends
from starlette import status

from api.notifications.schemas import NotificationRead
from api.notifications.service import NotificationService, notification_service_factory
from api.users.dependencies import get_current_user
from core.database.models import User

router = APIRouter(prefix="/notifications")


@router.get(
    "/get-unread-notifications",
    status_code=status.HTTP_200_OK,
    response_model=List[NotificationRead],
)
async def get_unread_notifications(
    user: User = Depends(get_current_user),
    notification_service: NotificationService = Depends(notification_service_factory),
):
    notifications = await notification_service.get_unread_notifications(user)
    return notifications


@router.get(
    "/get-all-notifications",
    status_code=status.HTTP_200_OK,
    response_model=List[NotificationRead],
)
async def get_all_notifications(
    user: User = Depends(get_current_user),
    notification_service: NotificationService = Depends(notification_service_factory),
):
    notifications = await notification_service.get_all_notifications(user)
    return notifications
