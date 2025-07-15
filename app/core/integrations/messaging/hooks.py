import logging

from fastapi import FastAPI

from .broker import rabbit_router

logger = logging.getLogger("app.faststream.hooks")


@rabbit_router.after_startup
async def setup_queues(app: FastAPI):
    logger.info("Настройка очередей RabbitMQ для отправки email")
    queues = [
        "email_queue",
        "verification_email_queue",
        "password_reset_email_queue",
        "registration_success_email_queue",
    ]

    for queue_name in queues:
        try:
            await rabbit_router.broker.declare_queue(queue_name)
            logger.info("Очередь %s успешно создана/проверена", queue_name)
        except Exception as e:
            logger.error("Ошибка при создании очереди %s: %s", queue_name, str(e))
