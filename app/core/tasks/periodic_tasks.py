import asyncio
from contextlib import asynccontextmanager

from celery import shared_task
from core.database import get_async_session
from core.database.repositories import (
    ExamRepository,
    NotificationRepository,
    UserRepository,
)


@asynccontextmanager
async def get_session():
    async for session in get_async_session():
        yield session


@shared_task
def check_exams_for_ending() -> None:
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    loop.run_until_complete(check_exams_for_ending_async())


@shared_task
def check_exams_for_starting() -> None:
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    loop.run_until_complete(check_exams_for_starting_async())


async def check_exams_for_ending_async() -> None:
    from api.notifications.service import NotificationService

    async with get_session() as session:
        notification_service = NotificationService(
            NotificationRepository(session),
            ExamRepository(session),
            UserRepository(session),
        )
        await notification_service.end_scheduled_exams()


async def check_exams_for_starting_async() -> None:
    from api.notifications.service import NotificationService

    async with get_session() as session:
        notification_service = NotificationService(
            NotificationRepository(session),
            ExamRepository(session),
            UserRepository(session),
        )
        await notification_service.start_scheduled_exams()
