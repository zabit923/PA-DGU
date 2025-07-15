import logging

from fastapi import FastAPI

logger = logging.getLogger(__name__)


def setup_messaging(app: FastAPI):
    from .broker import rabbit_router

    app.include_router(rabbit_router)
    logger.info("Обработчики сообщений настроены")
