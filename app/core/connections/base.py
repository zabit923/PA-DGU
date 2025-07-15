import logging
from abc import ABC, abstractmethod
from typing import Any, Optional


class BaseClient(ABC):
    def __init__(self) -> None:
        self._client: Optional[Any] = None
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    async def connect(self) -> Any:
        """
        Создает подключение
        Устанавливает подключение к целевому сервису или ресурсу.
        """

    @abstractmethod
    async def close(self) -> None:
        """
        Закрывает подключение
        Закрывает активное подключение и выполняет необходимую очистку.
        """


class BaseContextManager(ABC):
    def __init__(self) -> None:
        self._client = None
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    async def connect(self) -> Any:
        """
        Создает подключение
        Устанавливает подключение к целевому сервису или ресурсу.
        """

    @abstractmethod
    async def close(self) -> None:
        """
        Закрывает подключение
        Закрывает активное подключение и выполняет необходимую очистку.
        """

    async def __aenter__(self):
        return await self.connect()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
