from typing import List

from models import Notification, User
from schemas import NotificationCreateSchema, NotificationDataSchema, PaginationParams
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.v1.base import BaseEntityManager


class NotificationDataManager(BaseEntityManager[NotificationDataSchema]):
    def __init__(self, session: AsyncSession):
        super().__init__(
            session=session, schema=NotificationDataSchema, model=Notification
        )

    async def mark_notifications_as_read(self, notification_ids: List[int]) -> None:
        if not notification_ids:
            return

        update_stmt = (
            update(Notification)
            .where(Notification.id.in_(notification_ids))
            .values(is_read=True)
        )
        await self.session.execute(update_stmt)
        await self.session.commit()

    async def get_all_notifications(
        self,
        user: User,
        pagination: PaginationParams,
    ) -> tuple[List[Notification], int]:
        statement = select(self.model).where(self.model.user_id == user.id)
        notifications, total = await self.get_paginated_items(statement, pagination)
        notification_ids = [notif.id for notif in notifications]
        await self.mark_notifications_as_read(notification_ids)
        return notifications, total

    async def get_unreads(
        self,
        user: User,
        pagination: PaginationParams,
    ) -> List[Notification]:
        statement = select(Notification).where(
            Notification.user_id == user.id, Notification.is_read == False
        )
        notifications, total = await self.get_paginated_items(statement, pagination)
        notification_ids = [notif.id for notif in notifications]
        await self.mark_notifications_as_read(notification_ids)
        return notifications, total

    async def create_notification(
        self, data: NotificationCreateSchema, user: User
    ) -> None:
        notification = Notification(title=data.title, body=data.body, user_id=user.id)
        await self.add_one(notification)
