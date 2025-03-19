import asyncio

from celery import shared_task


@shared_task
def check_exams_for_ending() -> None:
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    loop.run_until_complete(check_exams_for_ending_async())


async def check_exams_for_ending_async() -> None:
    from api.notifications.service import notification_service_factory

    notification_service = notification_service_factory()
    await notification_service.end_scheduled_exams()


@shared_task
def check_exams_for_starting() -> None:
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    loop.run_until_complete(check_exams_for_starting_async())


async def check_exams_for_starting_async() -> None:
    from api.notifications.service import notification_service_factory

    notification_service = notification_service_factory()
    await notification_service.start_scheduled_exams()
