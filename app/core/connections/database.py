from typing import AsyncGenerator

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.connections import BaseClient
from app.core.settings import Config, settings


class DatabaseClient(BaseClient):
    _engine: AsyncEngine | None = None
    _session_factory: async_sessionmaker[AsyncSession] | None = None

    def __init__(self, config: Config = settings) -> None:
        super().__init__()
        self._config = config

    async def connect(self) -> async_sessionmaker[AsyncSession]:
        if self._session_factory is not None:
            self.logger.debug("Фабрика сессий уже инициализирована")
            return self._session_factory

        try:
            self.logger.info("Инициализация подключения к базе данных...")

            self._engine = create_async_engine(
                url=self._config.database_url, **self._config.engine_params
            )

            self._session_factory = async_sessionmaker(
                bind=self._engine, **self._config.session_params
            )

            self.logger.info("Подключение к базе данных успешно инициализировано")
            return self._session_factory

        except SQLAlchemyError as e:
            self.logger.error(f"Ошибка при инициализации базы данных: {e}")
            raise

    async def close(self) -> None:
        if self._engine:
            self.logger.info("Закрытие подключения к базе данных...")
            await self._engine.dispose()
            DatabaseClient._engine = None
            DatabaseClient._session_factory = None
            self.logger.info("Подключение к базе данных закрыто")

    def get_session_factory(self) -> async_sessionmaker[AsyncSession]:
        if self._session_factory is None:
            raise RuntimeError(
                "База данных не инициализирована. "
                "Вызовите connect() перед использованием."
            )
        return self._session_factory

    def get_engine(self) -> AsyncEngine:
        self._engine = create_async_engine(
            url=self._config.database_url, **self._config.engine_params
        )

        if self._engine is None:
            raise RuntimeError(
                "База данных не инициализирована. "
                "Вызовите connect() перед использованием."
            )
        return self._engine


database_client = DatabaseClient()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    if database_client._session_factory is None:
        await database_client.connect()
    session_factory = database_client.get_session_factory()

    async with session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
