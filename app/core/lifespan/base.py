import logging
from contextlib import asynccontextmanager
from typing import Awaitable, Callable, List

from fastapi import FastAPI

logger = logging.getLogger("app.lifecycle")

StartupHandler = Callable[[FastAPI], Awaitable[None]]

ShutdownHandler = Callable[[FastAPI], Awaitable[None]]

startup_handlers: List[StartupHandler] = []

shutdown_handlers: List[ShutdownHandler] = []


def register_startup_handler(handler: StartupHandler):
    startup_handlers.append(handler)
    return handler


def register_shutdown_handler(handler: ShutdownHandler):
    shutdown_handlers.append(handler)
    return handler


async def run_startup_handlers(app: FastAPI):
    from app.core.lifespan.clients import initialize_clients
    from app.core.lifespan.database import initialize_database

    if initialize_database not in startup_handlers:
        startup_handlers.append(initialize_database)
    if initialize_clients not in startup_handlers:
        startup_handlers.append(initialize_clients)
    for handler in startup_handlers:
        try:
            logger.info("Запуск обработчика: %s", handler.__name__)
            await handler(app)
            logger.debug("Обработчик %s выполнен успешно", handler.__name__)
        except Exception as e:
            logger.error("Ошибка в обработчике %s: %s", handler.__name__, str(e))


async def run_shutdown_handlers(app: FastAPI):
    from app.core.lifespan.clients import close_clients
    from app.core.lifespan.database import close_database_connection

    if close_database_connection not in shutdown_handlers:
        shutdown_handlers.append(close_database_connection)
    if close_clients not in shutdown_handlers:
        shutdown_handlers.append(close_clients)

    for handler in shutdown_handlers:
        try:
            logger.info("Запуск обработчика остановки: %s", handler.__name__)
            await handler(app)
            logger.debug("Обработчик остановки %s выполнен успешно", handler.__name__)
        except Exception as e:
            logger.error(
                "Ошибка в обработчике остановки %s: %s", handler.__name__, str(e)
            )


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Начало инициализации приложения")
    await run_startup_handlers(app)
    logger.info("Инициализация приложения завершена")

    yield

    logger.info("Начало завершения работы приложения")
    await run_shutdown_handlers(app)
    logger.info("Завершение работы приложения выполнено")
