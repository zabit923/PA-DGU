import asyncio
from typing import Optional

from aio_pika import connect_robust
from aio_pika.abc import AbstractRobustConnection
from aio_pika.exceptions import AMQPConnectionError

from app.core.settings import settings

from .base import BaseClient


class RabbitMQClient(BaseClient):
    _instance: Optional[AbstractRobustConnection] = None
    _is_connected: bool = False
    _max_retries: int = 5
    _retry_delay: int = 5

    def __init__(self) -> None:
        super().__init__()
        self._connection_params = settings.rabbitmq_params
        self._debug_mode = getattr(settings, "DEBUG", False)

    async def connect(self) -> Optional[AbstractRobustConnection]:
        if not self._instance and not self._is_connected:
            for attempt in range(self._max_retries):
                try:
                    self.logger.debug("Подключение к RabbitMQ...")
                    self._instance = await connect_robust(**self._connection_params)
                    self._is_connected = True
                    self.logger.info("Подключение к RabbitMQ установлено")
                    break
                except AMQPConnectionError as e:
                    self.logger.error("Ошибка подключения к RabbitMQ: %s", str(e))
                    if attempt < self._max_retries - 1:
                        self.logger.warning(
                            f"Повторная попытка {attempt+1}/{self._max_retries} через {self._retry_delay} секунд..."
                        )
                        await asyncio.sleep(self._retry_delay)
                    else:
                        self._is_connected = False
                        self._instance = None
                        self.logger.warning(
                            "RabbitMQ недоступен после всех попыток, но приложение продолжит работу"
                        )

                        if self._debug_mode:
                            return None
                        else:
                            return None
        return self._instance

    async def close(self) -> None:
        if self._instance and self._is_connected:
            try:
                self.logger.debug("Закрытие подключения к RabbitMQ...")
                await self._instance.close()
                self.logger.info("Подключение к RabbitMQ закрыто")
            finally:
                self._instance = None
                self._is_connected = False

    async def health_check(self) -> bool:
        if not self._instance or not self._is_connected:
            return False
        try:
            return not self._instance.is_closed
        except AMQPConnectionError:
            return False

    @property
    def is_connected(self) -> bool:
        return self._is_connected
