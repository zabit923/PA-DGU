from sqlalchemy import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.database.models import Notification, User


class NotificationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self, user: User) -> Sequence[Notification]:
        statement = select(Notification).where(Notification.user_id == user.id)
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def get_unreads(self, user: User) -> Sequence[Notification]:
        statement = select(Notification).where(
            Notification.user_id == user.id, Notification.is_read == False
        )
        result = await self.session.execute(statement)
        notifications = result.scalars().all()
        for notification in notifications:
            notification.is_read = True
        await self.session.commit()
        return notifications

    async def create_notification(self, title: str, body: str, user: User) -> None:
        notification = Notification(title=title, body=body, user_id=user.id)
        self.session.add(notification)
        await self.session.commit()
